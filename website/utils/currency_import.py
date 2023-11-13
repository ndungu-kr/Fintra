import csv
from datetime import datetime, timedelta, timezone
from os import getcwd, listdir, path, getenv
import os
from sqlite3 import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import requests
from forex_python.converter import CurrencyCodes


def initial_currency_import():
    from website.models import Forex

    # Acessing forex file and csv
    currency_file = "currency_data"
    currency_data = "currencies.csv"
    cwd = path.abspath(getcwd())
    currency_folder_path = path.join(cwd, "website", currency_file)

    csv_file_path = os.path.join(currency_folder_path, currency_data)

    try:
        engine = create_engine("sqlite:///./Database/database.db")
        Session = sessionmaker(bind=engine)
        session = Session()
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")

    try:
        # Opening csv file to check all initial currencies are in the db
        with open(csv_file_path, "r", newline="", encoding="utf8") as csvfile:
            currency_reader = csv.DictReader(csvfile)
            added_counter = 0

            for row in currency_reader:
                code = row["code"]
                name = row["name"]
                symbol = row["symbol"]

                currency_code_exists = session.query(Forex).filter_by(code=code).first()

                # if forex code exists then skip
                if currency_code_exists:
                    pass
                # otherwise add it to the db
                else:
                    # DATATIMEFUNCTION
                    last_updated = datetime.now().replace(microsecond=0).isoformat()
                    date_format = "%Y-%m-%dT%H:%M:%S"
                    last_updated = datetime.strptime(last_updated, date_format)
                    new_query = Forex(
                        code=code,
                        name=name,
                        current_price=None,
                        symbol=symbol,
                        last_updated=last_updated,
                    )
                    session.add(new_query)
                    added_counter = added_counter + 1

            session.commit()
            session.close()

            print(
                "##### Database Update: ", added_counter, " New Currencies added #####"
            )

    except Exception as e:
        print(f"Error inserting data into forex table: {e}")


def get_currency_pairs():
    from website.models import Forex

    # Read db for codes in forex table
    try:
        engine = create_engine("sqlite:///./Database/database.db")
        Session = sessionmaker(bind=engine)
        session = Session()
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")

    try:
        currency_codes = session.query(Forex.code).all()
        currency_pairs = []
    except Exception as e:
        print(f"Error reading forex table: {e}")

    # Create forex pairs for API request
    for code in currency_codes:
        currency_pairs.append(f"USD/{code[0]}")

    session.close()

    return currency_pairs


def currency_import():
    # Building the API request URL with base currency as USD
    url = f"https://openexchangerates.org/api/latest.json?app_id={getenv('oer_api_key')}&show_alternative=1"
    response = requests.get(url)

    # Parse the response JSON
    data = response.json()

    # Building the data

    # Extract the timestamp and rates against USD
    timestamp = data["timestamp"]
    rates = data["rates"]

    # Fetch the forex asset names using the CurrencyCodes library
    currency_codes = list(rates.keys())
    c = CurrencyCodes()
    currency_names = [c.get_currency_name(code) for code in currency_codes]

    # Prepare the data
    currency_data = [["code", "name", "current_price", "last_updated"]]

    from website.models import Forex

    engine = create_engine("sqlite:///./Database/database.db")
    Session = sessionmaker(bind=engine)

    for code, name in zip(currency_codes, currency_names):
        current_price = rates[code]
        # change timestamp to utc datetime object
        last_updated = datetime.utcfromtimestamp(timestamp).replace(microsecond=0)
        # change timestamp to isoformat
        last_updated = last_updated.isoformat()
        csv_row = [code, name, current_price, last_updated]
        currency_data.append(csv_row)

        # Check if forex code exists in db

        with Session() as session:
            currency_code_exists = session.query(Forex).filter_by(code=code).first()
            # change timestamp to datetime object
            last_updated = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S")
            if name is None:
                name = code

            if currency_code_exists:
                # Update price and last updated
                currency_code_exists.current_price = current_price
                currency_code_exists.last_updated = last_updated
                session.commit()
            else:
                # Add new forex asset to db
                new_query = Forex(
                    code=code,
                    name=name,
                    current_price=current_price,
                    last_updated=last_updated,
                )
                session.add(new_query)
                session.commit()

    # Update AssetLastUpdated table
    from .loops import update_last_updated

    asset = "forex"
    update_last_updated(asset)
