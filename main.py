from multiprocessing import Process
import threading
from website import create_app
from website.loops import start_crypto_thread, start_currency_thread

app = create_app()


# # Helper function to easily  parallelize multiple functions
# def parallelize_functions(*functions):
#     processes = []
#     for function in functions:
#         p = Process(target=function)
#         p.start()
#         processes.append(p)
#     for p in processes:
#         p.join()


def start_application():
    app.run(debug=True, use_reloader=False)


# def start_application():
#     def run_app():
#         app.run(debug=False, use_reloader=False, threaded=True)
#         """ use_reloader=False to prevent the app from running twice and
#         removed debug=True as the reloader expects to run in the main thread"""

#     app_thread = threading.Thread(target=run_app)
#     app_thread.daemon = True
#     print("Starting app")
#     app_thread.start()


if __name__ == "__main__":
    with app.app_context():
        start_crypto_thread()
        start_currency_thread()
    start_application()

    # # Start app on a 1st thread
    # start_application()
    # with app.app_context():
    #     # Start the crypto generation loop on a 2nd thread
    #     start_crypto_thread()
    # Start the currency generation loop on a 3rd thread
    # start_currency_thread()
