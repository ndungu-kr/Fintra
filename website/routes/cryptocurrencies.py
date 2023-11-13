from flask import render_template
from flask_login import current_user, login_required
from .views import views
from .. import db
from website.models import Cryptocurrency


@views.route("/cryptocurrencies", methods=["GET", "POST"])
@login_required
def cryptocurrencies():
    cryptocurrencies = Cryptocurrency.query.all()
    for cryptocurrency in cryptocurrencies:
        cryptocurrency.current_price = format_to_2dp_with_commas(
            cryptocurrency.current_price
        )
        cryptocurrency.market_cap = format_to_2dp_with_commas(cryptocurrency.market_cap)
        cryptocurrency.circulating_supply = format_with_commas(
            cryptocurrency.circulating_supply
        )
        cryptocurrency.max_supply = format_with_commas(cryptocurrency.max_supply)
        cryptocurrency.last_updated = convert_time_from_utc_to_local(
            cryptocurrency.last_updated
        )

    return render_template(
        "assets/cryptocurrencies.html", user=current_user, cryptocurrencies=cryptocurrencies
    )


def format_to_2dp_with_commas(value):
    return f"${value:,.2f}"


def format_with_commas(value):
    return f"{value:,.2f}"


def convert_time_from_utc_to_local(utc_time):
    # find out what timezone the user is in
    utc_time.astimezone(tz=None)
    return utc_time
