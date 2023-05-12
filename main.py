from website import create_app
from website.loops import start_crypto_thread, start_currency_thread

app = create_app()

if __name__ == "__main__":
    start_crypto_thread()
    start_currency_thread()
    app.run(
        debug=True, use_reloader=False
    )  # use_reloader=False to prevent the app from running twice
