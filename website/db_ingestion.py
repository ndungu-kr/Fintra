import csv
from . import db, Currency, Cryptocurrency


def data_insert():
    # Import data from the currencies CSV file
    with open("currencies.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        currencies = list(reader)
    # Insert data into Currency
    db.session.bulk_insert_mappings(Currency, currencies)
    db.session.commit()

    # Import data from the cryptocurrencies CSV file - Temp (will use API in Future)
    with open("cryptocurrencies.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        cryptocurrencies = list(reader)
    # Insert data into Cryptocurrency
    db.session.bulk_insert_mappings(Cryptocurrency, cryptocurrencies)
    db.session.commit()
