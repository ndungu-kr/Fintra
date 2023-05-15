import threading
import time
from website.cryptocurrency_import import crypto_import
from website.currency_import import initial_currency_import, currency_import


def start_crypto_thread():
    def generate_crypto_csv():
        while True:
            crypto_import()
            time.sleep(60)

    # crypto_import()
    # # Schedule the function to run every 1 minutes
    # threading.Timer(15.0, generate_csv_loop).start()

    # Start the crypto generation loop on a 1st thread
    crypto_csv_thread = threading.Thread(target=generate_crypto_csv)
    # Making daemon to allow crtl + c stop to app
    crypto_csv_thread.daemon = True
    crypto_csv_thread.start()


def start_currency_thread():
    # Run the initial currency import to add relevant currencies to DB
    initial_currency_import()

    # Schedule the currency check to run every 1 minute
    def generate_currency_csv():
        while True:
            currency_import()
            time.sleep(60)

    # Start the currency generation loop on a 2nd thread
    currency_csv_thread = threading.Thread(target=generate_currency_csv)
    currency_csv_thread.daemon = True
    currency_csv_thread.start()
