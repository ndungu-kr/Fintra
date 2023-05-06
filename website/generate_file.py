import csv
from . import db_ingestion


def create_crypto_csv(cryptos, filename_path, latest_cryptocurrency_file):
    with open(filename_path, "w", newline="") as csvfile:
        fieldnames = ["code", "name", "current_price", "last_updated"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for crypto in cryptos:
            writer.writerow(crypto)

        print("Cryptocurrency file created successfully.")

    db_ingestion.data_insert(latest_cryptocurrency_file)
