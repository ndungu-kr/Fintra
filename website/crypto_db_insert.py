# script to insert csv to db manually
from . import db_ingestion


def insert_file_to_db():
    cryptocurrency_file = (
        "website\crypto_data\top_cryptocurrencies 2023-05-06 223228.csv"
    )
    db_ingestion.data_insert(cryptocurrency_file)
