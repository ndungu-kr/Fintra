import csv

def create_crypto_csv(cryptos, crypto_folder_path):    
    with open(crypto_folder_path, "w", newline="") as csvfile:
        fieldnames = ["code", "name", "current_price", "last_updated"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for crypto in cryptos:
            writer.writerow(crypto)

        print("Cryptocurrency file created successfully.")