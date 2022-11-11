from unicodedata import category
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

# from .models import Transaction
from . import db
import json

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        pass
        # description = request.form.get("description")
        # transaction_amount = request.form.get("transaction_amount")

        # if len(description) < 1:
        #     flash("Note is too short", category="error")
        # elif transaction_amount == 0:
        #     flash("Please enter an amount", category="error")
        # else:
        #     new_description = Transaction(
        #         description=description,
        #         user_id=current_user.id,
        #         amount=transaction_amount,
        #     )
        #     db.session.add(new_description)
        #     db.session.add()
        #     db.session.commit()
        #     flash("Transaction successfully added.", category="success")
    else:
        pass
    return render_template("dashboard.html", user=current_user)


@views.route("/delete-transaction", methods=["POST"])
def delete_transaction():
    # transaction = json.loads(request.data)
    # transactionId = transaction["transactionId"]
    # transaction = Transaction.query.get(transactionId)
    # if transaction:
    #     if transaction.user_id == current_user.id:
    #         db.session.delete(transaction)
    #         db.session.commit()

    return jsonify({})


@views.route("/cryptocurrency-wallet", methods=["GET", "POST"])
@login_required
def cryptocurrency_wallet():
    return render_template("cryptocurrency_wallet.html", user=current_user)


@views.route("/cryptocurrency-wallet/buy-cryptocurrency", methods=["GET", "POST"])
@login_required
def buy_cryptocurrency():
    return render_template("buy_cryptocurrency.html", user=current_user)


@views.route("/cryptocurrency-wallet/sell-cryptocurrency", methods=["GET", "POST"])
@login_required
def sell_cryptocurrency():
    return render_template("sell_cryptocurrency.html", user=current_user)


@views.route("/forex-wallet", methods=["GET", "POST"])
@login_required
def forex_wallet():
    return render_template("forex_wallet.html", user=current_user)


@views.route("/forex-wallet/buy-forex", methods=["GET", "POST"])
@login_required
def buy_forex():
    return render_template("buy_forex.html", user=current_user)


@views.route("/forex-wallet/sell-forex", methods=["GET", "POST"])
@login_required
def sell_forex():
    return render_template("sell_forex.html", user=current_user)


@views.route("/stock-wallet", methods=["GET", "POST"])
@login_required
def stock_wallet():
    return render_template("stock_wallet.html", user=current_user)


@views.route("/stock-wallet/buy-stock", methods=["GET", "POST"])
@login_required
def buy_stock():
    return render_template("buy_stock.html", user=current_user)


@views.route("/stock-wallet/sell-stock", methods=["GET", "POST"])
@login_required
def sell_stock():
    return render_template("sell_stock.html", user=current_user)


@views.route("/cryptocurrency-tracker", methods=["GET", "POST"])
@login_required
def cryptocurrency_tracker():
    return render_template("cryptocurrency_tracker.html", user=current_user)


@views.route("/forex-tracker", methods=["GET", "POST"])
@login_required
def forex_tracker():
    return render_template("forex_tracker.html", user=current_user)


@views.route("/stock-tracker", methods=["GET", "POST"])
@login_required
def stock_tracker():
    return render_template("stock_tracker.html", user=current_user)
