import csv
from datetime import datetime, timedelta, timezone
from os import getcwd, listdir, path
import os
from sqlite3 import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import requests
from forex_python.converter import CurrencyCodes


def initial_currency_import():
    from website.models import Currency

    # Acessing currency file and csv
    currency_file = "currency_data"
    currency_data = "currencies.csv"
    cwd = path.abspath(getcwd())
    currency_folder_path = path.join(cwd, "website", currency_file)

    csv_file_path = os.path.join(currency_folder_path, currency_data)

    try:
        engine = create_engine("sqlite:///./instance/database.db")
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

                currency_code_exists = (
                    session.query(Currency).filter_by(code=code).first()
                )

                # if currency code exists then skip
                if currency_code_exists:
                    pass
                # otherwise add it to the db
                else:
                    # DATATIMEFUNCTION
                    last_updated = datetime.now().replace(microsecond=0).isoformat()
                    date_format = "%Y-%m-%dT%H:%M:%S"
                    last_updated = datetime.strptime(last_updated, date_format)
                    new_query = Currency(
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
        print(f"Error inserting data into currency table: {e}")


def get_currency_pairs():
    from website.models import Currency

    # Read db for codes in currency table
    try:
        engine = create_engine("sqlite:///./instance/database.db")
        Session = sessionmaker(bind=engine)
        session = Session()
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")

    try:
        currency_codes = session.query(Currency.code).all()
        currency_pairs = []
    except Exception as e:
        print(f"Error reading currency table: {e}")

    # Create currency pairs for API request
    for code in currency_codes:
        currency_pairs.append(f"USD/{code[0]}")

    session.close()

    return currency_pairs


def currency_import():
    api_key = "2a398dea570d408aa9058f71145957a9"

    # Building the API request URL with base currency as USD
    url = f"https://openexchangerates.org/api/latest.json?app_id={api_key}&show_alternative=1"
    response = requests.get(url)

    # Parse the response JSON
    data = response.json()

    # Building the data

    # Extract the timestamp and rates against USD
    timestamp = data["timestamp"]
    rates = data["rates"]

    # Fetch the currency names using the CurrencyCodes library
    currency_codes = list(rates.keys())
    c = CurrencyCodes()
    currency_names = [c.get_currency_name(code) for code in currency_codes]

    # Prepare the data
    currency_data = [["code", "name", "current_price", "last_updated"]]

    from website.models import Currency

    engine = create_engine("sqlite:///./instance/database.db")
    Session = sessionmaker(bind=engine)

    for code, name in zip(currency_codes, currency_names):
        current_price = rates[code]
        # change timestamp to utc datetime object
        last_updated = datetime.utcfromtimestamp(timestamp).replace(microsecond=0)
        # change timestamp to isoformat
        last_updated = last_updated.isoformat()
        csv_row = [code, name, current_price, last_updated]
        currency_data.append(csv_row)

        # Check if currency code exists in db

        with Session() as session:
            currency_code_exists = session.query(Currency).filter_by(code=code).first()
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
                # Add new currency to db
                new_query = Currency(
                    code=code,
                    name=name,
                    current_price=current_price,
                    last_updated=last_updated,
                )
                session.add(new_query)
                session.commit()

    # Update AssetLastUpdated table
    from website.loops import update_last_updated

    asset = "currency"
    update_last_updated(asset)

    save_to_csv(currency_data)


def save_to_csv(currency_data):
    # Acessing prices folder
    prices_folder = "currency_data\prices"
    cwd = path.abspath(getcwd())
    prices_folder_path = path.join(cwd, "website", prices_folder)

    current_time = datetime.now(timezone.utc)
    # Removing milliseconds from time for naming csv
    formatted_time = current_time.strftime("%Y-%m-%d %H%M%S")

    filename = f"currency prices {formatted_time}.csv"
    file_path = os.path.join(prices_folder_path, filename)

    # Write data to CSV file
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(currency_data)

    print(f"Currency prices, names, and timestamps saved to {filename}.")


def check_for_csv(current_time, prices_folder_path):
    # Getting a list of CSV file names in order to check if the latest file is already there
    currency_file_list = listdir(prices_folder_path)

    # Removing string from filenames to make datetime objs
    prices_file_times_unedited = [
        s.strip("currency prices ") for s in currency_file_list
    ]
    prices_file_times_in_string = [s.strip(".csv") for s in prices_file_times_unedited]
    prices_file_times = [
        datetime.strptime(d, "%Y-%m-%d %H%M%S") for d in prices_file_times_in_string
    ]

    # finding the latest file in the folder
    if prices_file_times:
        latest_file_timestamp = max(prices_file_times)
    else:
        latest_file_timestamp = None

    if latest_file_timestamp:
        validity_period = latest_file_timestamp + timedelta(minutes=60)
        validity_period = validity_period.replace(microsecond=0, tzinfo=None)
    else:
        validity_period = None

    current_time = current_time.replace(microsecond=0, tzinfo=None)

    if validity_period is None:
        print("###### NO CURRENCY FILE FOUND ######")
        return False
    elif current_time > validity_period:
        print("###### CURRENCY FILE IS OUT OF DATE ######")
        return False
    else:
        print("###### CURRENCY FILE IS UP TO DATE ######")
        return True
