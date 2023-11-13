from flask import render_template
from flask_login import current_user, login_required
from website.views import views
from . import db
from website.models import Stock, Exchange


@views.route("/stocks", methods=["GET", "POST"])
@login_required
def stocks():
    stocks = Stock.query.all()

    # arrange stocks in alphabetical order of code
    stocks.sort(key=lambda x: x.code)

    for stock in stocks:
        # stocks are saved with a suffix so we need to remove it, i.e "NXT.L" to "NXT" or "AAPL.OQ" to "AAPL"
        dot_index = stock.code.find(".")
        if dot_index != -1:
            stock.ticker = stock.code[:dot_index]
            stock.suffix = stock.code[dot_index:]
        else:
            stock.ticker = stock.code
            stock.suffix = None

        if stock.suffix is None:
            if stock.exchange == "NMS":
                stock.exchange_name = "NASDAQ"
            elif stock.exchange == "NYQ":
                stock.exchange_name = "New York Stock Exchange"
        else:
            stock.exchange_name = Exchange.query.filter_by(suffix=stock.suffix).first()
            stock.exchange_name = stock.exchange_name.name

        stock.formatted_price = format_to_2dp_with_commas(stock.usd_price)

        # removing time from date
        stock.price_date_only = stock.price_date.strftime("%d/%m/%Y")

    return render_template(
        "assets/stocks.html",
        user=current_user,
        stocks=stocks,
    )


def format_to_2dp_with_commas(value):
    return f"${value:,.2f}"
