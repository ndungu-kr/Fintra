from multiprocessing import Process
import threading
from website import create_app
from website.loops import start_crypto_thread, start_currency_thread, start_stock_thread

app = create_app()


def start_application():
    app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    with app.app_context():
        start_currency_thread()
        start_crypto_thread()
        start_stock_thread()
    start_application()
