import requests
import csv
from os import path
from datetime import datetime, timezone


def crypto_import():
    api_key = "175fea6e-3c78-4ea7-82af-7fbe9f03a6a5"

    # URL for the API endpoint
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=500&convert=USD"

    # Setting header with API key
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": api_key}

    current_time = datetime.now(timezone.utc)
    current_timestamp = current_time.timestamp()

    # Removing milliseconds from time for csv
    formatted_time = current_time.strftime("%Y-%m-%d %H%M%S")

    filename = f"top_cryptocurrencies {formatted_time}.csv"

    # Check if the CSV file already exists
    if path.exists(filename):
        file_timestamp = path.getmtime(filename)
        time_diff = current_timestamp - file_timestamp

        # Check if the CSV file is older than 7 minutes (420 seconds)
        if time_diff < 420:
            print("CSV file is up-to-date. Exiting script...")
            return
        else:
            print(
                "CSV file is older than 7 minutes. Calling API to create new CSV file..."
            )
            # Move file to past details folder here
            crypto_data_to_csv(url, headers, filename)

    else:
        print("CSV file does not exist. Calling API to create new CSV file...")
        crypto_data_to_csv(url, headers, filename)


def crypto_data_to_csv(url, headers, filename):
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
                "current_price": crypto["quote"]["USD"]["price"],
                "last_updated": timestamp,
            }
        )

    # Writing the cryptocurrency data onto a CSV file
    with open(path.filename, "w", newline="") as csvfile:
        fieldnames = ["code", "name", "current_price", "last_updated"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for crypto in cryptos:
            writer.writerow(crypto)

        print("Cryptocurrency file created successfully.")
