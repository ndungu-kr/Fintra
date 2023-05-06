import csv

from .models import Cryptocurrency
from sqlalchemy import create_engine
from datetime import datetime


def convert_time(last_updated):
    date_format = "%Y-%m-%dT%H:%M:%S"
    last_updated = datetime.strptime(last_updated, date_format)
    print(last_updated)
    return last_updated


def data_insert(latest_cryptocurrency_file):
    # Import data from the cryptocurrencies CSV file
    engine = create_engine("sqlite:///database.db")
    try:
        with open(latest_cryptocurrency_file, newline="") as csvfile:
            # skip the header row
            next(csvfile)
            reader = csv.DictReader(csvfile)
            added_counter = 0
            updated_counter = 0
            print("We are here")
            for row in reader:
                code = row["code"]
                name = row["name"]
                current_price = int(row["current_price"])
                last_updated = row["last_updated"]
                convert_time(last_updated)
                crypto_exists = Cryptocurrency.query.filter_by(code=code).first()
                if crypto_exists:
                    crypto_exists.price = current_price
                    crypto_exists.last_updated = last_updated
                    crypto_exists.commit()
                    updated_counter = updated_counter + 1
                else:
                    new_query = Cryptocurrency(
                        name=name,
                        current_price=current_price,
                        last_updated=last_updated,
                    )
                    new_query.add()
                    added_counter = added_counter + 1

            print(added_counter, " New Cryptocurrencies added")
            print(updated_counter, " Cryptocurrencies updated")
    except:
        print("Crypto CSV db transfer failed")


# I want it to check the db first using the code column
# if the code exists
# update the current row
# if it doesnt exist
# add


# # Import data from the currencies CSV file
# with open("currencies.csv", "r") as csvfile:
#     reader = csv.DictReader(csvfile)
#     currencies = list(reader)
# # Insert data into Currency
# db.session.bulk_insert_mappings(Currency, currencies)
# db.session.commit()
