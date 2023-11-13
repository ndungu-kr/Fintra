from datetime import datetime, timedelta
from sqlite3 import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from website.models import Forex, Stock
import yfinance as yf
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter
import decimal


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND * 5)),
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)

yf.pdr_override()  # Overrides the default requests session used by yfinance
yf.session = session


class DbSession:
    def __init__(self):
        try:
            engine = create_engine("sqlite:///./Database/database.db")
            self.dbSession = sessionmaker(bind=engine)
        except OperationalError as e:
            print(f"Error connecting to the database: {e}")

    def __enter__(self):
        self.sesh = self.dbSession()
        return self.sesh

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sesh.close()


def import_yfinance_codes():
    from website.models import Exchange
    from os import getcwd, path
    import os
    import csv

    # Acessing stock file and csv
    stock_file = "stock_data"
    stock_data = "yfinance_codes.csv"
    cwd = path.abspath(getcwd())
    stock_folder_path = path.join(cwd, "website", stock_file)

    csv_file_path = os.path.join(stock_folder_path, stock_data)

    try:
        # Opening csv file to check all initial currencies are in the db
        with open(csv_file_path, "r", newline="", encoding="utf-8-sig") as csvfile:
            stock_reader = csv.DictReader(csvfile)
            for row in stock_reader:
                country = row["country"]
                name = row["name"]
                suffix = row["suffix"]

                with DbSession() as sesh:
                    suffix_exists = sesh.query(Exchange).filter_by(name=name).first()

                    if suffix_exists:
                        continue
                    else:
                        new_query = Exchange(
                            name=name,
                            suffix=suffix,
                            country=country,
                        )
                        sesh.add(new_query)

                    sesh.commit()

    except Exception as e:
        print(f"Error inserting data into exchange table: {e}")


def stock_import():
    stock_tickers = []

    # getting stock codes from the database
    with DbSession() as sesh:
        user_stocks = sesh.query(Stock).all()

    if len(user_stocks) > 0:
        # Only update stocks that haven't been updated today
        for stock in user_stocks:
            today = datetime.now().date()
            four_days_ago = today - timedelta(days=4)

            # if there is a last updated and price date
            if stock.last_updated and stock.price_date:
                # and if the last updated is today
                if stock.last_updated.date() == today:
                    # and if the price date falls within the last 4 days
                    if stock.price_date.date() >= four_days_ago:
                        continue
                    else:
                        stock_tickers.append(f"{stock.code}")
                else:
                    # if the price date is older than 4 days and last updated is today then try to update
                    stock_tickers.append(f"{stock.code}")
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
            try:
                data = get_stock_prices(stock_tickers)
            except Exception as e:
                print(f"Error retrieving stock prices: {e}")
                return False

            update_prices(stock_tickers, data)

            # Update the last updated date for stocks
            from .loops import update_last_updated

            asset = "stock"
            update_last_updated(asset)

        else:
            print("########### NO NEW STOCKS FOUND IN TABLE ###########")
            return False

    else:
        print("########### NO STOCKS FOUND IN TABLE ###########")
        return False


def stock_validity_check(asset_code):
    # first we check the stock exists and has information available
    data_available, stock_info = yfinance_check(asset_code)
    if data_available is False:
        return False

    # then we check if it has the last trading days price information
    ticker = []
    ticker.append(asset_code)

    stock_prices = get_stock_prices(ticker)

    if stock_prices is False:
        return False

    # we then check it has the relevant information and add stock info to the database if true
    add_to_db = add_stock(asset_code, stock_info)
    if add_to_db is False:
        return False

    # if all checks are passed, we update the stock price
    update_prices(ticker, stock_prices)

    return True


def yfinance_check(asset_code):
    stock_info = get_stock_info(asset_code)

    if stock_info is False:
        return False, False

    return True, stock_info


def get_stock_info(asset_code):
    try:
        stock_info = yf.Ticker(asset_code)
        return stock_info.info
    except Exception as e:
        print(f"Error retrieving stock info for {asset_code}: {str(e)}")
        return False


def get_stock_prices(tickers):
    # Make API requests for a group of tickers while respecting rate limit
    try:
        df = yf.download(tickers, period="1d", group_by="ticker")
        # if df is an empty dataframe, return False
        if df.empty:
            return False
    except Exception as e:
        print(f"Error retrieving data for {tickers}: {str(e)}")
        return False

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


def add_stock(asset_code, stock_info):
    name = stock_info.get("shortName", None)
    market_cap = stock_info.get("marketCap", None)
    country = stock_info.get("country", None)
    exchange = stock_info.get("exchange", None)
    sector = stock_info.get("sector", None)
    currency = stock_info.get("currency", None)
    if currency:
        currency = currency.upper()

    if name is None or currency is None:
        return False

    with DbSession() as sesh:
        add_stock_to_database = Stock(
            name=name,
            market_cap=market_cap,
            country=country,
            exchange=exchange,
            sector=sector,
            code=asset_code,
            currency=currency,
        )
        sesh.add(add_stock_to_database)
        sesh.commit()
    return True


def update_prices(stock_tickers, data):
    try:
        with DbSession() as sesh:
            updated_counter = 0

            if len(stock_tickers) > 1:
                # Get the values from the dataframe
                tickers = data["Ticker"]
                close_prices = data["Close"]
                dates = data.index

                # Print the values
                for ticker, close, date in zip(tickers, close_prices, dates):
                    stock = sesh.query(Stock).filter_by(code=ticker).first()
                    stock.price = close
                    stock.price_date = date
                    stock.last_updated = datetime.now()

                    # calculate USD value of stock
                    stock_currency = stock.currency
                    # search forex table for currency code
                    if stock_currency:
                        stock.usd_price = calculate_usd_price(stock_currency, close)

                    sesh.commit()

                    updated_counter += 1
            else:
                ticker, close, date = data
                stock = sesh.query(Stock).filter_by(code=ticker).first()
                stock.price = close
                stock.price_date = date
                stock.last_updated = datetime.now()

                # calculate USD value of stock
                stock_currency = stock.currency
                # search forex table for currency code
                if stock_currency:
                    stock.usd_price = calculate_usd_price(stock_currency, close)

                sesh.commit()

                updated_counter += 1

            print(
                "##### Database Update: ",
                updated_counter,
                "Stocks updated #####",
            )

    except Exception as e:
        print(f"Error updating stocks table: {e}")
        return False


def calculate_usd_price(stock_currency, close):
    with DbSession() as sesh:
        # search forex table for currency code
        currency = sesh.query(Forex).filter_by(code=stock_currency).first()
    exchange_rate = currency.current_price
    # calculate the USD value of the stock
    usd_price = decimal.Decimal(close) / exchange_rate
    return usd_price


# def update_metadata(asset_code):
#     stock_info = yf.Ticker(asset_code)
#     stock_info.info
