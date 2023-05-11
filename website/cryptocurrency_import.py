import requests
from os import path, listdir, getcwd
from datetime import datetime, timezone, timedelta
from . import generate_file
import time
import threading


def start_csv_check_loop():
    def generate_csv_loop():
        while True:
            crypto_import()
            time.sleep(60)

        # crypto_import()
        # # Schedule the function to run every 1 minutes
        # threading.Timer(15.0, generate_csv_loop).start()

    # Start the CSV generation loop on a separate thread
    generate_csv_loop_thread = threading.Thread(target=generate_csv_loop)
    # Making daemon to allow crtl + c stop to app
    generate_csv_loop_thread.daemon = True
    generate_csv_loop_thread.start()


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

    # removing string from file names to make datetime objs, MAKE SURE ONLY CSV IN CRYPTO CSV FILE
    crypto_file_times_unedited = [
        s.strip("top_cryptocurrencies ") for s in crypto_file_list
    ]
    crypto_file_times_in_string = [s.strip(".csv") for s in crypto_file_times_unedited]
    crypto_file_times = [
        datetime.strptime(d, "%Y-%m-%d %H%M%S") for d in crypto_file_times_in_string
    ]

    # finding the latest file in the folder
    if crypto_file_times:
        latest_file_timestamp = max(crypto_file_times)
        latest_cryptocurrency_file = path.join(
            crypto_folder_path,
            (
                "top_cryptocurrencies "
                + latest_file_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                + ".csv"
            ),
        )
    else:
        latest_file_timestamp = None
    print("###### LATEST CRYPTO FOLDER TIME ######", latest_file_timestamp)

    current_time = datetime.now(timezone.utc)
    print("##### CURRENT TIME #####", current_time)

    # Removing milliseconds from time for naming csv
    formatted_time = current_time.strftime("%Y-%m-%d %H%M%S")
    filename = f"top_cryptocurrencies {formatted_time}.csv"

    # setting csv save location
    filename_path = path.join(crypto_folder_path, filename)

    # Checking time at the refresh/cutoff time - 7 mins
    current_refresh_time = current_time - timedelta(minutes=7)
    current_refresh_time = current_refresh_time.replace(microsecond=0, tzinfo=None)

    # Checking if latest CSV file is older than refresh refresh time
    if latest_file_timestamp is None:
        print("CSV file does not exist. Calling API to create new CSV file...")
        latest_cryptocurrency_file = path.join(crypto_folder_path, filename)
        crypto_data_to_csv(url, headers, filename_path, latest_cryptocurrency_file)
    elif latest_file_timestamp < current_refresh_time:
        print("CSV file is older than 7 minutes. Calling API to create new CSV file...")
        latest_cryptocurrency_file = path.join(crypto_folder_path, filename)
        crypto_data_to_csv(url, headers, filename_path, latest_cryptocurrency_file)
    else:
        print("CSV file is up-to-date. Exiting script...")


def crypto_data_to_csv(url, headers, filename_path, latest_cryptocurrency_file):
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

    # Do something else with cryptos
    # Write it in db

    print(
        "########## Crypto file created at #############",
        latest_cryptocurrency_file,
    )

    # Writing the cryptocurrency data onto a CSV file
    generate_file.create_crypto_csv(cryptos, filename_path, latest_cryptocurrency_file)
