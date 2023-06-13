from datetime import datetime
from unicodedata import category
from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
import decimal

from website.models import (
    Cryptocurrency,
    CryptocurrencyAmount,
    CryptocurrencyBuy,
    CryptocurrencySell,
)

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


# @views.route("/delete-transaction", methods=["POST"])
# def delete_transaction():
#     # transaction = json.loads(request.data)
#     # transactionId = transaction["transactionId"]
#     # transaction = Transaction.query.get(transactionId)
#     # if transaction:
#     #     if transaction.user_id == current_user.id:
#     #         db.session.delete(transaction)
#     #         db.session.commit()

#     return jsonify({})


@views.route("/cryptocurrency-wallet", methods=["GET", "POST"])
@login_required
def cryptocurrency_wallet():
    crypto_balance = 0
    total_invested = 0
    total_withdrawn = 0

    # getting the total amount of cryptocurrency owned by the user
    user_cryptos = CryptocurrencyAmount.query.filter_by(user_id=current_user.id).all()
    if user_cryptos is not None:
        for crypto in user_cryptos:
            cryptocurrency_data = get_cryptocurrency_data(crypto.cryptocurrency_code)

            # add cryptocurrency price and name to the crypto object
            crypto.price = cryptocurrency_data.current_price
            crypto.name = cryptocurrency_data.name

            # calculating the total value of the cryptocurrency
            crypto.full_value = crypto.quantity * crypto.price
            crypto.quantity = round(crypto.quantity, 6)

            # adding the value of the cryptocurrency to the total crypto balance
            crypto_balance += crypto.full_value

            # formatting the value to 2 decimal places and adding commas to thousands
            crypto.value = f"{crypto.full_value:,.2f}"

            # # getting all the buy and sell instances for the specific cryptocurrency
            # crypto.buy_instances = CryptocurrencyBuy.query.filter_by(
            #     user_id=current_user.id, cryptocurrency_code=crypto.cryptocurrency_code
            # ).all()
            # crypto.sell_instances = CryptocurrencySell.query.filter_by(
            #     user_id=current_user.id, cryptocurrency_code=crypto.cryptocurrency_code
            # ).all()

            # # calculating the total amount spent on the cryptocurrency
            # total_spent_on_asset = 0
            # for buy_instance in crypto.buy_instances:
            #     total_spent_on_asset += buy_instance.monetary_amount
            # for sell_instance in crypto.sell_instances:
            #     total_spent_on_asset -= sell_instance.monetary_amount
            # crypto.total_spent = total_spent_on_asset

            # total_invested += crypto.total_spent

            # # calculating the profit/loss on the cryptocurrency
            # Use average spend here
            # crypto.profit = crypto.full_value - crypto.total_spent
            # if crypto.total_spent == 0:
            #     crypto.profit_percentage = 0
            # else:
            #     crypto.profit_percentage = (crypto.profit / crypto.total_spent) * 100
            # crypto.profit = f"{crypto.profit:,.2f}"

            # # adding "$" to the profit value
            # if crypto.profit[0] != "-":
            #     crypto.profit = f"${crypto.profit}"
            # else:
            #     crypto.profit = f"-${crypto.profit[1:]}"
            # crypto.profit_percentage = f"{crypto.profit_percentage:,.2f}%"

        # getting all the users buy transactions, only picking the monetary values

    # calculating total asset profit
    # first we get the users cryptocurrency transactions
    user_buy_transactions = CryptocurrencyBuy.query.filter_by(
        user_id=current_user.id
    ).all()
    user_sell_transactions = CryptocurrencySell.query.filter_by(
        user_id=current_user.id
    ).all()
    total_monetary_gained = 0
    total_crypto_spend = 0
    value_of_remaining_assets = 0
    asset_quantities = {}
    # then we calculate the total spent
    for buy_tranz in user_buy_transactions:
        total_crypto_spend += buy_tranz.monetary_amount
        total_invested += buy_tranz.monetary_amount
        # if asset exists in dictionary, add to the quantity
        if buy_tranz.cryptocurrency_code in asset_quantities:
            asset_quantities[buy_tranz.cryptocurrency_code] += buy_tranz.crypto_amount
        else:
            asset_quantities[buy_tranz.cryptocurrency_code] = buy_tranz.crypto_amount
    # calculating value of asset sold
    for sell_tranz in user_sell_transactions:
        total_monetary_gained += sell_tranz.monetary_amount
        total_withdrawn += sell_tranz.monetary_amount
        asset_quantities[sell_tranz.cryptocurrency_code] -= sell_tranz.crypto_amount
    # calculating value of remaining assets
    for asset in asset_quantities:
        crypto_data = get_cryptocurrency_data(asset)
        value_of_remaining_assets += asset_quantities[asset] * crypto_data.current_price
    # calculating total profit
    total_crypto_profit = (
        total_monetary_gained + value_of_remaining_assets - total_crypto_spend
    )
    if total_crypto_spend != 0:
        total_crypto_profit_percentage = (
            total_crypto_profit / total_crypto_spend
        ) * 100
        total_crypto_profit_percentage = f"{total_crypto_profit_percentage:,.2f}%"
        if total_crypto_profit >= 0:
            total_crypto_profit = f"${total_crypto_profit:,.2f}"
        elif total_crypto_profit < 0:
            total_crypto_profit = total_crypto_profit * -1
            total_crypto_profit = f"-${total_crypto_profit:,.2f}"
    else:
        total_crypto_profit_percentage = "0.00%"
        total_crypto_profit = "$0.00"

    # formatting to 2 decimal places and adding commas to thousands
    total_crypto_balance = f"${crypto_balance:,.2f}"
    total_invested = f"${total_invested:,.2f}"
    total_withdrawn = f"${total_withdrawn:,.2f}"

    # getting the users cryptocurrency transactions
    user_buy_transactions2 = CryptocurrencyBuy.query.filter_by(
        user_id=current_user.id
    ).all()
    user_sell_transactions2 = CryptocurrencySell.query.filter_by(
        user_id=current_user.id
    ).all()

    # calculating the total invested and sold this month
    total_invested_this_month = 0
    total_sold_this_month = 0
    monetary_amount_gained_this_month = 0
    total_spent_on_crypto_this_month = 0
    value_of_rem_crypto_purchased_this_month = 0
    remaining_crypto_quantities = {}

    for buy_transaction in user_buy_transactions2:
        if buy_transaction.date.month == datetime.now().month:
            total_invested_this_month += buy_transaction.monetary_amount
    for sell_transaction in user_sell_transactions2:
        if sell_transaction.date.month == datetime.now().month:
            total_sold_this_month += sell_transaction.monetary_amount

    # calculating the total spent this month
    for buy_transaction in user_buy_transactions2:
        if buy_transaction.date.month == datetime.now().month:
            total_spent_on_crypto_this_month += buy_transaction.monetary_amount
            # put crypto code and quantity into dictionary
            if buy_transaction.cryptocurrency_code in remaining_crypto_quantities:
                remaining_crypto_quantities[
                    buy_transaction.cryptocurrency_code
                ] += buy_transaction.crypto_amount
            else:
                remaining_crypto_quantities[
                    buy_transaction.cryptocurrency_code
                ] = buy_transaction.crypto_amount

    # calculating the value of the cryptocurrency sold this month
    for sell_transaction in user_sell_transactions2:
        if sell_transaction.date.month == datetime.now().month:
            monetary_amount_gained_this_month += sell_transaction.monetary_amount
        # subtracting the quantity of the cryptocurrency sold from the dictionary
        if sell_transaction.cryptocurrency_code in remaining_crypto_quantities:
            remaining_crypto_quantities[
                sell_transaction.cryptocurrency_code
            ] -= sell_transaction.crypto_amount
        # situation where the user sold asset bought before this month
        else:
            remaining_crypto_quantities[
                sell_transaction.cryptocurrency_code
            ] = sell_transaction.crypto_amount

    # calculating the value of the remaining cryptocurrency purchased this month
    for crypto in remaining_crypto_quantities:
        cryptocurrency_data = get_cryptocurrency_data(crypto)
        value_of_rem_crypto_purchased_this_month += (
            remaining_crypto_quantities[crypto] * cryptocurrency_data.current_price
        )

    print("monetary amount gained this month:", monetary_amount_gained_this_month)
    print(
        "value of remaining crypto purchased this month:",
        value_of_rem_crypto_purchased_this_month,
    )
    print("total spent on crypto this month:", total_spent_on_crypto_this_month)

    profit_this_month = (
        monetary_amount_gained_this_month
        + value_of_rem_crypto_purchased_this_month
        - total_spent_on_crypto_this_month
    )

    if total_spent_on_crypto_this_month != 0:
        profit_this_month_percentage = (
            profit_this_month / total_spent_on_crypto_this_month
        ) * 100
        profit_this_month = f"${profit_this_month:,.2f}"
        profit_this_month_percentage = f"{profit_this_month_percentage:,.2f}%"
    else:
        profit_this_month = "$0.00"
        profit_this_month_percentage = "0.00%"

    # formating after as we need to calculate the total invested this month first
    total_invested_this_month = f"${total_invested_this_month:,.2f}"
    total_sold_this_month = f"${total_sold_this_month:,.2f}"

    # calculating the profit this month
    user_buy_transactions3 = CryptocurrencyBuy.query.filter_by(
        user_id=current_user.id
    ).all()
    user_sell_transactions3 = CryptocurrencySell.query.filter_by(
        user_id=current_user.id
    ).all()
    # marking the buy and sell transactions as buy or sell
    for buy_transaction in user_buy_transactions3:
        buy_transaction.type = "Buy"
    for sell_transaction in user_sell_transactions3:
        sell_transaction.type = "Sell"
    # merging the buy and sell transactions into one list in decending order of date
    user_transactions = user_buy_transactions3 + user_sell_transactions3
    user_transactions.sort(key=lambda x: x.date, reverse=True)
    if user_transactions is not None:
        for transaction in user_transactions:
            cryptocurrency_data = get_cryptocurrency_data(
                transaction.cryptocurrency_code
            )
            transaction.name = cryptocurrency_data.name
            transaction.crypto_amount = round(transaction.crypto_amount, 6)
            # formatting the value to 2 decimal places and adding commas to thousands
            # transaction.monetary amount is a string but i need to change it to a float to format it
            transaction.value = float(transaction.monetary_amount)
            transaction.value = f"${transaction.value:,.2f}"
            # changing the date to a string in the format "Day/Month/Year"
            transaction.short_date = transaction.date.strftime("%d/%m/%Y")

    return render_template(
        "cryptocurrency_wallet.html",
        user=current_user,
        total_crypto_balance=total_crypto_balance,
        total_crypto_profit=total_crypto_profit,
        total_crypto_profit_percentage=total_crypto_profit_percentage,
        total_invested=total_invested,
        total_withdrawn=total_withdrawn,
        total_invested_this_month=total_invested_this_month,
        total_sold_this_month=total_sold_this_month,
        user_cryptos=user_cryptos,
        user_transactions=user_transactions,
        profit_this_month=profit_this_month,
        profit_this_month_percentage=profit_this_month_percentage,
    )


def get_cryptocurrency_data(cryptocurrency_code):
    cryptocurrency_data = Cryptocurrency.query.filter_by(
        code=cryptocurrency_code
    ).first()
    return cryptocurrency_data


@views.route("/cryptocurrency-wallet/buy-cryptocurrency", methods=["GET", "POST"])
@login_required
def buy_cryptocurrency():
    return render_template("buy_cryptocurrency.html", user=current_user)


@views.route("/submit-crypto-buy", methods=["POST"])
def submit_crypto_buy():
    cryptocurrency_code = request.form.get("cryptocurrency")
    cryptocurrency_amount = decimal.Decimal(request.form.get("cryptocurrencyAmount"))
    monetary_amount = float(request.form.get("monetaryAmount"))
    date_input = request.form.get("transactionDate")
    description = request.form.get("description")
    errors = []

    # date is entered as a string in the format "DD/MM/YYYY" so we need to convert it to a datetime object
    try:
        date = datetime.strptime(date_input, "%d/%m/%Y")
    except ValueError:
        errors.append("Please enter a valid date.")

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
            date=date,
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
        flash("Cryptocurrency successfully purchased.", category="success")
        return redirect(url_for("views.cryptocurrency_wallet"))


@views.route("/submit-crypto-sell", methods=["POST"])
def submit_crypto_sell():
    cryptocurrency_code = request.form.get("cryptocurrency")
    cryptocurrency_amount = decimal.Decimal(request.form.get("cryptocurrencyAmount"))
    monetary_amount = float(request.form.get("monetaryAmount"))
    date_input = request.form.get("transactionDate")
    description = request.form.get("description")
    errors = []

    # date is entered as a string in the format "DD/MM/YYYY" so we need to convert it to a datetime object
    try:
        date = datetime.strptime(date_input, "%d/%m/%Y")
    except ValueError:
        errors.append("Please enter a valid date.")

    if cryptocurrency_amount == 0 or cryptocurrency_amount < 0:
        errors.append("Please enter a valid cryptocurrency amount.")

    if monetary_amount == 0 or monetary_amount < 0:
        errors.append("Please enter a valid monetary value.")

    user_owns_crypto = CryptocurrencyAmount.query.filter_by(
        cryptocurrency_code=cryptocurrency_code, user_id=current_user.id
    ).first()
    if user_owns_crypto is None:
        errors.append("You do not own this cryptocurrency.")

    if len(errors) > 0:
        for error in errors:
            flash(error, category="error")
        return render_template("sell_cryptocurrency.html", user=current_user)
    else:
        # adding transaction to sell cryptocurrency
        add_to_crypto_sell = CryptocurrencySell(
            cryptocurrency_code=cryptocurrency_code,
            user_id=current_user.id,
            crypto_amount=cryptocurrency_amount,
            monetary_amount=monetary_amount,
            description=description,
            date=date,
        )
        db.session.add(add_to_crypto_sell)

        # updating the cryptocurrency amounts table
        user_crypto_amount = CryptocurrencyAmount.query.filter_by(
            cryptocurrency_code=cryptocurrency_code, user_id=current_user.id
        ).first()
        user_crypto_amount.quantity -= cryptocurrency_amount

        # if the user has sold all of their cryptocurrency, delete the row from the table
        if user_crypto_amount.quantity == 0:
            db.session.delete(user_crypto_amount)

        db.session.commit()

        flash("Cryptocurrency successfully sold.", category="success")
        return redirect(url_for("views.cryptocurrency_wallet"))


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
