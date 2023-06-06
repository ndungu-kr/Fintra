import csv
from .models import Cryptocurrency
from sqlalchemy import create_engine
from datetime import datetime
from re import sub
from decimal import Decimal
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

# Functions not in use:
# this function is not in use, but can be used to create a csv file of the latest cryptocurrency data


def convert_time(last_updated):
    date_format = "%Y-%m-%dT%H:%M:%S"
    last_updated = datetime.strptime(last_updated, date_format)
    return last_updated


def crypto_data_insert(latest_cryptocurrency_file):
    # Creating an engine and session
    try:
        engine = create_engine("sqlite:///./instance/database.db")
        Session = sessionmaker(bind=engine)
        session = Session()
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")

    try:
        with open(latest_cryptocurrency_file, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            added_counter = 0
            updated_counter = 0

            for row in reader:
                code = row["code"]
                name = row["name"]
                current_price = row["current_price"]
                # Removing any character that is not an int or ".", and then making the str decimal
                current_price = Decimal(sub(r"[^\d.]", "", current_price))
                last_updated = convert_time(row["last_updated"])

                crypto_code_exists = (
                    session.query(Cryptocurrency).filter_by(code=code).first()
                )
                crypto_name_exists = (
                    session.query(Cryptocurrency).filter_by(name=name).first()
                )

                # if the crypto exists in db, update, if not add to db
                # some cryptos share the code, hence both checks below:
                if crypto_code_exists and crypto_name_exists:
                    crypto_code_exists.price = current_price
                    crypto_code_exists.last_updated = last_updated
                    updated_counter = updated_counter + 1
                else:
                    new_query = Cryptocurrency(
                        code=code,
                        name=name,
                        current_price=current_price,
                        last_updated=last_updated,
                    )
                    session.add(new_query)
                    added_counter = added_counter + 1

            session.commit()
            session.close()

            print(added_counter, " New Cryptocurrencies added")
            print(updated_counter, " Cryptocurrencies updated")
    except:
        print("No changes made to db")
