from datetime import datetime, timedelta, timezone
from sqlite3 import OperationalError
import threading
import time
from flask import current_app
from sqlalchemy import create_engine
from website.cryptocurrency_import import crypto_import
from website.currency_import import initial_currency_import, currency_import
from sqlalchemy.orm import sessionmaker

from website.stock_import import import_yfinance_codes, stock_import


def start_crypto_thread():
    def generate_crypto_data():
        asset = "cryptocurrency"
        while True:
            try:
                last_updated = check_latest_update(asset)
                print(f"Last updated time for Cryptocurrency: {last_updated}")
            except Exception as e:
                print(f"Error checking last updated time: {e}")

            if determine_validity(asset, last_updated) == True:
                print("###### CRYPTO DATA IS UP TO DATE ######")
            elif determine_validity(asset, last_updated) == False:
                print("###### CRYPTO DATA IS OUT OF DATE, ACQUIRING NEW DATA ######")
                crypto_import()
            time.sleep(60)

    # Start the crypto generation loop on a 1st thread
    crypto_thread = threading.Thread(target=generate_crypto_data)
    # Making daemon to allow crtl + c stop to app
    crypto_thread.daemon = True
    crypto_thread.start()


def start_currency_thread():
    # Run the initial forex import to add relevant currencies to DB
    initial_currency_import()

    # Schedule the forex check to run every 1 minute
    def generate_currency_data():
        asset = "forex"
        while True:
            try:
                last_updated = check_latest_update(asset)
                print(f"Last updated time for Forex: {last_updated}")
            except Exception as e:
                print(f"Error checking last updated time: {e}")

            if determine_validity(asset, last_updated) == True:
                print("###### CURRENCY DATA IS UP TO DATE ######")
            elif determine_validity(asset, last_updated) == False:
                print("###### CURRENCY DATA IS OUT OF DATE, ACQUIRING NEW DATA ######")
                currency_import()
            # Should Wait 15 minutes before checking again (900)
            time.sleep(60)

    # Start the forex generation loop on a 2nd thread
    currency_thread = threading.Thread(target=generate_currency_data)
    currency_thread.daemon = True
    currency_thread.start()


def start_stock_thread():
    # Getting the suffixes for the exchange markets
    import_yfinance_codes()

    def generate_stock_data():
        asset = "stock"
        while True:
            try:
                last_updated = check_latest_update(asset)
                print(f"Last updated time for Stock: {last_updated}")
            except Exception as e:
                print(f"Error checking last updated time: {e}")

            if determine_validity(asset, last_updated) == True:
                print("###### STOCK DATA IS UP TO DATE ######")
            elif determine_validity(asset, last_updated) == False:
                print("###### STOCK DATA IS OUT OF DATE, ACQUIRING NEW DATA ######")
                stock_import()
            time.sleep(60)

    # Start the crypto generation loop on a 1st thread
    stock_thread = threading.Thread(target=generate_stock_data)
    # Making daemon to allow crtl + c stop to app
    stock_thread.daemon = True
    stock_thread.start()


def check_latest_update(asset):
    from website.models import AssetLastUpdated

    try:
        engine = create_engine("sqlite:///./instance/database.db")
        # Session = sessionmaker(bind=engine)
        # session = Session()
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")

    # Create a session
    Session = sessionmaker(bind=engine)
    with Session() as session:
        result = (
            session.query(AssetLastUpdated.last_updated)
            .filter(AssetLastUpdated.asset == asset)
            .first()
        )

        if result:
            last_updated = result.last_updated
            session.commit()
        else:
            last_updated = None

        return last_updated


def determine_validity(asset, last_updated):
    # Set validity period based on asset type in minutes
    if asset == "cryptocurrency":
        # 30 minutes for Crypto data updates
        validity_period = 30
    elif asset == "forex":
        # 1 hour for Forex data updates
        validity_period = 60
    elif asset == "stock":
        # 1 hour to check if new stock data avalaible
        validity_period = 60

    if last_updated:
        expiry_time = last_updated + timedelta(minutes=validity_period)
    else:
        print("###### NO LAST UPDATED TIME FOUND ######")
        return False

    # times in UTC
    current_time = datetime.now(timezone.utc)
    expiry_time = expiry_time.replace(tzinfo=timezone.utc)

    # returns True if the data is still valid, False if it is not
    if expiry_time:
        if current_time > expiry_time:
            return False
        else:
            return True
    else:
        return False


def update_last_updated(asset):
    from website.models import AssetLastUpdated

    try:
        engine = create_engine("sqlite:///./instance/database.db")
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")

    # Checking if last updated time exists
    Session = sessionmaker(bind=engine)

    with Session() as session:
        record_exists = session.query(AssetLastUpdated).filter_by(asset=asset).first()
        try:
            # update the AssetLastUpdated table
            last_updated = datetime.now(timezone.utc)

            # write to database
            if record_exists:
                # update the last_updated time
                record_exists.last_updated = last_updated
                session.commit()
            else:
                new_query = AssetLastUpdated(
                    asset=asset,
                    last_updated=last_updated,
                )
                session.add(new_query)
                session.commit()
            print("###### Updated AssetLastUpdated table successfully ######")

        except Exception as e:
            print(f"Error inserting data into AssetLastUpdated table: {e}")
