from sqlite3 import OperationalError
import requests
from os import path, getcwd
from datetime import datetime, timezone, timedelta
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def crypto_import():
    api_key = "175fea6e-3c78-4ea7-82af-7fbe9f03a6a5"

    # URL for the API endpoint
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=500&convert=USD"

    # Setting header with API key
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": api_key}

    # Retreiving data from API using a GET request
    response = requests.get(url, headers=headers)
    data = response.json()

    # Creating a list of dictionaries containing the cryptocurrency data
    cryptos = []
    for crypto in data["data"]:
        timestamp_str = crypto["last_updated"]
        timestamp = datetime.strptime(
            timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ"
        ).isoformat()
        cryptos.append(
            {
                "code": crypto["symbol"],
                "name": crypto["name"],
                "current_price": f"${crypto['quote']['USD']['price']}",
                "last_updated": timestamp,
            }
        )

    # Writing the cryptocurrency data to the database
    crypto_data_to_db(cryptos)

    # Writing the cryptocurrency data onto a CSV file
    create_crypto_csv(cryptos)


def crypto_data_to_db(cryptos):
    from website.models import Cryptocurrency

    try:
        engine = create_engine("sqlite:///./instance/database.db")
        Session = sessionmaker(bind=engine)
        # session = Session()
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")

    try:
        added_counter = 0
        updated_counter = 0
        for crypto in cryptos:
            code = crypto["code"]
            name = crypto["name"]
            current_price = crypto["current_price"]
            last_updated = crypto["last_updated"]

            # converting current_price and last_updated to correct format
            current_price = float(current_price.strip("$"))
            last_updated = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S")

            Session = sessionmaker(bind=engine)
            with Session() as session:
                crypto_code_exists = (
                    session.query(Cryptocurrency).filter_by(code=code).first()
                )
                crypto_name_exists = (
                    session.query(Cryptocurrency).filter_by(name=name).first()
                )
                if crypto_code_exists and crypto_name_exists:
                    crypto_code_exists.price = current_price
                    crypto_code_exists.last_updated = last_updated
                    updated_counter = updated_counter + 1
                    session.commit()
                else:
                    new_query = Cryptocurrency(
                        code=code,
                        name=name,
                        current_price=current_price,
                        last_updated=last_updated,
                    )
                    session.add(new_query)
                    session.commit()
                    added_counter = added_counter + 1

        print(
            "##### Database Update: ",
            added_counter,
            " New Cryptocurrencies added #####",
        )
        print(
            "##### Database Update: ",
            updated_counter,
            " Cryptocurrencies updated #####",
        )

    except Exception as e:
        print(f"Error inserting data into cryptocurrency table: {e}")

    # Update AssetLastUpdated table
    from website.loops import update_last_updated

    asset = "cryptocurrency"
    update_last_updated(asset)


def create_crypto_csv(cryptos):
    # Acessing crypto file
    crypto_folder = "crypto_data"
    cwd = path.abspath(getcwd())
    crypto_folder_path = path.join(cwd, "website", crypto_folder)

    current_time = datetime.now(timezone.utc)

    # Removing milliseconds from time for naming csv
    formatted_time = current_time.strftime("%Y-%m-%d %H%M%S")
    filename = f"top_cryptocurrencies {formatted_time}.csv"

    # setting csv save location
    file_path = path.join(crypto_folder_path, filename)

    with open(file_path, "w", newline="") as csvfile:
        fieldnames = ["code", "name", "current_price", "last_updated"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for crypto in cryptos:
            writer.writerow(crypto)

        print("###### Cryptocurrency CSV created successfully ######")
