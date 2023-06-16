from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

views = Blueprint("views", __name__)

# import functions
from website.forex import *
from website.stock import *
from website.cryptocurrency import *


@views.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@views.route("/cryptocurrency-wallet/buy-cryptocurrency", methods=["GET", "POST"])
@login_required
def buy_cryptocurrency():
    return render_template("buy_cryptocurrency.html", user=current_user)


@views.route("/cryptocurrency-wallet/sell-cryptocurrency", methods=["GET", "POST"])
@login_required
def sell_cryptocurrency():
    return render_template("sell_cryptocurrency.html", user=current_user)


@views.route("/forex-wallet/buy-forex", methods=["GET", "POST"])
@login_required
def buy_forex():
    return render_template("buy_forex.html", user=current_user)


@views.route("/forex-wallet/sell-forex", methods=["GET", "POST"])
@login_required
def sell_forex():
    return render_template("sell_forex.html", user=current_user)


@views.route("/stock-wallet/buy-stock", methods=["GET", "POST"])
@login_required
def buy_stock():
    return render_template("buy_stock.html", user=current_user)


@views.route("/stock-wallet/sell-stock", methods=["GET", "POST"])
@login_required
def sell_stock():
    return render_template("sell_stock.html", user=current_user)
