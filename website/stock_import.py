from datetime import datetime
from sqlite3 import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from website.models import Stock
import yfinance as yf
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND * 5)),
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)

yf.pdr_override()  # Overrides the default requests session used by yfinance
yf.session = session


def stock_import():
    try:
        engine = create_engine("sqlite:///./instance/database.db")
        dbSession = sessionmaker(bind=engine)
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")

    stock_tickers = []

    # getting stock codes from the database
    with dbSession() as session:
        user_stocks = session.query(Stock).all()

    if len(user_stocks) > 0:
        # Only update stocks that haven't been updated today
        for stock in user_stocks:
            # if the stock has already been updated today, skip it
            today = datetime.now().date()
            if stock.last_updated:
                if stock.last_updated.date() == today:
                    continue
            else:
                # adding stock code in the list with quotes around it
                stock_tickers.append(f"{stock.code}")

        # Divide the tickers into batches if need be
        if len(stock_tickers) > 100:
            # batch_size = 100
            # ticker_batches = [
            #     stock_tickers[i : i + batch_size]
            #     for i in range(0, len(stock_tickers), batch_size)
            # ]
            # get_stock_prices(ticker_batches)
            print("######### BATCH SIZE OVER 100 UNABLE TO COMPUTE #########")
            # end function if batch size is over 100
            return

        if stock_tickers:
            data = get_stock_prices(stock_tickers)
        else:
            print("########### NO NEW STOCKS FOUND IN TABLE ###########")
            return False

        try:
            with dbSession() as session:
                updated_counter = 0

                if len(stock_tickers) > 1:
                    # Get the values from the dataframe
                    tickers = data["Ticker"]
                    close_prices = data["Close"]
                    dates = data.index

                    # Print the values
                    for ticker, close, date in zip(tickers, close_prices, dates):
                        stock = session.query(Stock).filter_by(code=ticker).first()
                        stock.price = close
                        stock.price_date = date
                        stock.last_updated = datetime.now()

                        session.commit()

                        updated_counter += 1
                else:
                    ticker, close, date = data
                    stock = session.query(Stock).filter_by(code=ticker).first()
                    stock.price = close
                    stock.price_date = date
                    stock.last_updated = datetime.now()

                    session.commit()

                    updated_counter += 1

                print(
                    "##### Database Update: ",
                    updated_counter,
                    "Stocks updated #####",
                )
                # Update the last updated date for stocks
            from website.loops import update_last_updated

            asset = "stock"
            update_last_updated(asset)

        except Exception as e:
            print(f"Error updating stocks table: {e}")

    else:
        print("########### NO STOCKS FOUND IN TABLE ###########")
        return False


def get_stock_prices(tickers):
    # Make API requests for a group of tickers while respecting rate limit
    try:
        df = yf.download(tickers, period="1d", group_by="ticker")
    except Exception as e:
        print(f"Error retrieving data for {tickers}: {str(e)}")

    # unsack the dataframe to get the data in the right format
    if len(tickers) == 1:
        # if there is only one ticker, the dataframe is different from multiple tickers
        ticker = tickers[0]
        close = df["Close"][0]
        date = df.index[0]

        return ticker, close, date
    else:
        data = df.stack(level=0).rename_axis(["Date", "Ticker"]).reset_index(level=1)
        return data


def get_stock_info(asset_code):
    stock_info = yf.Ticker(asset_code)
    return stock_info.info


def update_metadata(asset_code):
    stock_info = yf.Ticker(asset_code)
    stock_info.info
