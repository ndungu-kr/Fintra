import requests
import csv
from os import path
from datetime import datetime


def crypto_import():
    # Replace YOUR_API_KEY with your actual API key
    api_key = "175fea6e-3c78-4ea7-82af-7fbe9f03a6a5"

    # Define the URL for the API endpoint
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=500&convert=USD"

    # Set the headers with your API key
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": api_key}

    # Check if the CSV file already exists
    if path.exists("top500_cryptos.csv"):
        print("Cryptocurrencies file already exists. Exiting script...")
    else:
        # Send a GET request to the API endpoint and retrieve the data
        response = requests.get(url, headers=headers)
        data = response.json()

        # Create a list of dictionaries containing the cryptocurrency data
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

        # Write the cryptocurrency data to a CSV file
        with open("top500_cryptos.csv", "w", newline="") as csvfile:
            fieldnames = ["code", "name", "current_price", "last_updated"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for crypto in cryptos:
                writer.writerow(crypto)

        print("Cryptocurrency file created successfully.")
