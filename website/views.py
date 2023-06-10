from unicodedata import category
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

from website.models import Cryptocurrency, CryptocurrencyAmount, CryptocurrencyBuy

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
    crypto_balance = None
    profit = None
    total_invested = None
    total_invested_this_month = None
    profit_this_month = None
    return render_template(
        "cryptocurrency_wallet.html",
        user=current_user,
        crypto_balance=crypto_balance,
        profit=profit,
        total_invested=total_invested,
        total_invested_this_month=total_invested_this_month,
        profit_this_month=profit_this_month,
    )


@views.route("/cryptocurrency-wallet/buy-cryptocurrency", methods=["GET", "POST"])
@login_required
def buy_cryptocurrency():
    return render_template("buy_cryptocurrency.html", user=current_user)


@views.route("/submit-crypto-buy", methods=["POST"])
def submit_crypto_buy():
    cryptocurrency_code = request.form.get("cryptocurrency")
    cryptocurrency_amount = int(request.form.get("cryptocurrencyAmount"))
    monetary_amount = float(request.form.get("monetaryAmount"))
    description = request.form.get("description")

    errors = []
    if cryptocurrency_amount == 0 or cryptocurrency_amount < 0:
        errors.append("Please enter a valid cryptocurrency amount.")

    if monetary_amount == 0 or monetary_amount < 0:
        errors.append("Please enter a valid monetary value.")

    cryptocurrency_code_exists = Cryptocurrency.query.filter_by(
        code=cryptocurrency_code
    ).first()
    if cryptocurrency_code_exists is None:
        errors.append(
            "Cryptocurrency does not exist. Please select one from our selection."
        )

    if len(errors) > 0:
        for error in errors:
            flash(error, category="error")
        return render_template("buy_cryptocurrency.html", user=current_user)
    else:
        # adding transaction to buy cryptocurrency
        add_to_crypto_buy = CryptocurrencyBuy(
            cryptocurrency_code=cryptocurrency_code,
            user_id=current_user.id,
            crypto_amount=cryptocurrency_amount,
            monetary_amount=monetary_amount,
            description=description,
            date=None,
        )
        db.session.add(add_to_crypto_buy)

        # updating the cryptocurrency amounts table if the user already owns the cryptocurrency
        user_owns_asset = CryptocurrencyAmount.query.filter_by(
            cryptocurrency_code=cryptocurrency_code, user_id=current_user.id
        ).first()
        if user_owns_asset is None:
            add_to_crypto_amounts = CryptocurrencyAmount(
                cryptocurrency_code=cryptocurrency_code,
                quantity=cryptocurrency_amount,
                user_id=current_user.id,
            )
            db.session.add(add_to_crypto_amounts)
        else:
            user_owns_asset.quantity += cryptocurrency_amount

        db.session.commit()
        flash("Transaction successfully added.", category="success")
        return render_template("cryptocurrency_wallet.html", user=current_user)


@views.route("/submit-crypto-sell", methods=["POST"])
def submit_crypto_sell():
    pass


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
