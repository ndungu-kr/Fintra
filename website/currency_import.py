import csv
from datetime import datetime, timezone
from os import getcwd, path
import os
from sqlite3 import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from website.models import Currency


def currency_import():
    # check the currencies csv and db and compare for matching values
    # if the db is missing values from the file add them
    # otherwise make a call to the api to get the updated prices
    # save that info to a csv and to the db

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

    with open(csv_file_path, "r", newline="", encoding="utf8") as csvfile:
        currency_reader = csv.DictReader(csvfile)
        added_counter = 0
        # updated_counter = 0

        for row in currency_reader:
            code = row["code"]
            name = row["name"]
            symbol = row["symbol"]

            currency_code_exists = session.query(Currency).filter_by(code=code).first()

            if currency_code_exists:
                pass
            else:
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

        print(added_counter, " New Currencies added")
        # print(updated_counter, " Currencies updated")
