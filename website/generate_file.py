import csv


def create_crypto_csv(cryptos, filename):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["code", "name", "current_price", "last_updated"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for crypto in cryptos:
            writer.writerow(crypto)

        print("Cryptocurrency file created successfully.")
