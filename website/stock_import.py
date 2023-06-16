import datetime
from website.models import Stock
import yfinance as yf
import requests
import requests_cache
from ratelimit import limits, sleep_and_retry

# Set up requests_cache to cache API responses
requests_cache.install_cache(
    "yfinance_cache", expire_after=180
)  # Cache responses for 180 seconds (3 minutes)


# Define the rate limit for API requests
@sleep_and_retry
@limits(calls=33, period=60)  # 33 requests per minute
def make_request():
    pass


def stock_import():
    stock_tickers = []
    # getting stock codes from the database
    user_stocks = Stock.query.all()
    for stock in user_stocks:
        # changing the last updated db time to a datetime object
        stock.last_updated = datetime.strptime(
            stock.last_updated, "%Y-%m-%d %H:%M:%S.%f"
        )
        # if the stock has already been updated today, skip it
        if stock.last_updated.date() == datetime.date.today():
            continue
        else:
            # adding stock code in the list with quotes around it
            stock_tickers.append(f"{stock.code}")

    # Divide the tickers into batches if need be
    if len(stock_tickers) > 100:
        batch_size = 100
        ticker_batches = [
            stock_tickers[i : i + batch_size]
            for i in range(0, len(stock_tickers), batch_size)
        ]

    if len(stock_tickers) > 0:
        # Make API requests for a group of tickers while respecting rate limit
        try:
            make_request()  # Respect the rate limit

            # Retrieve the most recent 5 day's data including market cap
            # Period is 4 days to ensure that the most recent trading day's data is included
            # even if the market is closed for a holiday or 4 day weekend
            df = yf.download(stock_tickers, period="5d", group_by="ticker")

        except Exception as e:
            print(f"Error retrieving data for {stock_tickers}: {str(e)}")

        # # Make API requests for each ticker while respecting rate limit
        # data = {}
        # for ticker in stock_tickers:
        #     try:
        #         make_request()  # Respect the rate limit
        #         # Retrieve the most recent 5 day's data including market cap
        #         # Period is 4 days to ensure that the most recent trading day's data is included
        #         # even if the market is closed for a holiday or 4 day weekend
        #         data[ticker] = yf.download(ticker, period="5d", group_by="ticker")
        #     except Exception as e:
        #         print(f"Error retrieving data for {ticker}: {str(e)}")

        # # Updating last updated time for stock
        # from website.loops import update_last_updated

        # asset = "stock"
        # update_last_updated(asset)
    else:
        print("########### NO STOCKS FOUND IN TABLE ###########")
        return
