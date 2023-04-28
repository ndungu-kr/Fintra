import requests
from os import path, listdir, getcwd
from datetime import datetime, timezone, timedelta
from . import generate_file


def crypto_import():
    api_key = "175fea6e-3c78-4ea7-82af-7fbe9f03a6a5"

    # URL for the API endpoint
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=500&convert=USD"

    # Setting header with API key
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": api_key}

    # Acessing crypto file
    crypto_folder = "crypto_data"
    cwd = path.abspath(getcwd())
    crypto_folder_path = path.join(cwd, "website", crypto_folder)

    # getting a list of crypto csvs
    crypto_file_list = listdir(crypto_folder_path)

    # removing string from file names to make datetime objs
    crypto_file_times = [s.strip("top_cryptocurrencies ") for s in crypto_file_list]
    crypto_file_times = [
        datetime.strptime(d, "%Y-%m-%d %H%M%S") for d in crypto_file_times
    ]

    # finding the latest file in the folder
    if crypto_file_times:
        latest_file_timestamp = max(crypto_file_times)
    else:
        latest_file_timestamp = None

    current_time = datetime.now(timezone.utc)

    # Removing milliseconds from time for csv
    formatted_time = current_time.strftime("%Y-%m-%d %H%M%S")

    filename = f"top_cryptocurrencies {formatted_time}.csv"
    current_refresh_time = current_time - timedelta(minutes=7)

    # Checking if latest CSV file is older than refresh refresh time
    if latest_file_timestamp is None:
        print("CSV file does not exist. Calling API to create new CSV file...")
        crypto_data_to_csv(url, headers, crypto_folder_path)
    elif latest_file_timestamp < current_refresh_time:
        print("CSV file is older than 7 minutes. Calling API to create new CSV file...")
        crypto_data_to_csv(url, headers, crypto_folder_path)
    else:
        print("CSV file is up-to-date. Exiting script...")


def crypto_data_to_csv(url, headers, crypto_folder_path):
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
    generate_file.create_crypto_csv(cryptos, crypto_folder_path)
