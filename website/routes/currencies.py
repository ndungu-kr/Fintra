from flask import render_template
from flask_login import current_user, login_required
from .views import views
from .. import db
from website.models import Forex


@views.route("/currencies", methods=["GET", "POST"])
@login_required
def currencies():
    currencies = Forex.query.all()
    currencies.sort(key=lambda x: x.code)
    for currency in currencies:
        if currency.symbol is None:
            currency.symbol = ""
        if currency.current_price != 0:
            currency.usd_price = 1 / currency.current_price
            currency.usd_price = format_with_commas(currency.usd_price)
            currency.current_price = format_with_commas(currency.current_price)

    return render_template("assets/currencies.html", user=current_user, currencies=currencies)


def format_with_commas(value):
    return f"{value:,.2f}"
