from website import create_app
from website.cryptocurrency_import import start_csv_check_loop

app = create_app()

if __name__ == "__main__":
    start_csv_check_loop()
    app.run(
        debug=True, use_reloader=False
    )  # use_reloader=False to prevent the app from running twice
