from sqlite3 import OperationalError
import requests
from os import path, getcwd
from datetime import datetime, timezone
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def crypto_import():
    api_key = "175fea6e-3c78-4ea7-82af-7fbe9f03a6a5"

    # URL for the API endpoint
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=1000"

    # Setting header with API key
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": api_key}

    # Retreiving data from API using a GET request
    response = requests.get(url, headers=headers)
    data = response.json()

    # Creating a list of dictionaries containing the cryptocurrency data
    cryptos = []
    for crypto in data["data"]:
        cryptos.append(
            {
                "code": crypto["symbol"],
                "name": crypto["name"],
                "current_price": f"${crypto['quote']['USD']['price']}",
                "market_cap": crypto["quote"]["USD"]["market_cap"],
                "ciurculating_supply": crypto["circulating_supply"],
                "total_supply": crypto["total_supply"],
                "max_supply": crypto["max_supply"],
                "last_updated": crypto["last_updated"],
            }
        )

    # Writing the cryptocurrency data to the database
    crypto_data_to_db(cryptos)


def crypto_data_to_db(cryptos):
    from website.models import Cryptocurrency

    try:
        engine = create_engine("sqlite:///./instance/database.db")
        Session = sessionmaker(bind=engine)
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")

    try:
        added_counter = 0
        updated_counter = 0
        for crypto in cryptos:
            code = crypto["code"]
            name = crypto["name"]
            current_price = crypto["current_price"]
            market_cap = crypto["market_cap"]
            circulating_supply = crypto["ciurculating_supply"]

            total_supply = crypto["total_supply"]
            if total_supply is None or total_supply == 0:
                total_supply = circulating_supply

            max_supply = crypto["max_supply"]
            if max_supply is None or max_supply == 0:
                max_supply = total_supply

            last_updated = crypto["last_updated"]

            # converting current_price and last_updated to correct format
            current_price = float(current_price.strip("$"))
            last_updated = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ")

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
                    crypto_code_exists.market_cap = market_cap
                    crypto_code_exists.circulating_supply = circulating_supply
                    crypto_code_exists.total_supply = total_supply
                    crypto_code_exists.max_supply = max_supply
                    updated_counter = updated_counter + 1
                    session.commit()
                else:
                    new_query = Cryptocurrency(
                        code=code,
                        name=name,
                        current_price=current_price,
                        market_cap=market_cap,
                        circulating_supply=circulating_supply,
                        total_supply=total_supply,
                        max_supply=max_supply,
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
