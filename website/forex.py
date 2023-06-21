from flask import render_template
from flask_login import current_user, login_required
from website.views import views
from . import db
import decimal
import json
from datetime import datetime
from flask import redirect, render_template, request, flash, url_for
from unicodedata import category


from website.models import (
    Currency,
    CurrencyAmount,
    ForexBuy,
    ForexSell,
)

holding = Currency
holdingAmount = CurrencyAmount
holdingBuy = ForexBuy
holdingSell = ForexSell


@views.route("/forex-wallet", methods=["GET", "POST"])
@login_required
def forex_wallet():
    ############### modal errors ###############
    buy_modal_errors, sell_modal_errors = modal_errors()

    ############### Getting asset totals for the user ###############
    user_assets, user_asset_values, asset_balance = calc_asset_totals()

    ############### Calculating total asset profit ###############
    (
        total_asset_balance,
        total_asset_profit,
        total_asset_profit_percentage,
        total_invested,
        total_withdrawn,
    ) = calc_total_profits(asset_balance)

    ############### Getting the users monthly breakdown ###############
    total_invested_this_month, total_sold_this_month = calc_monthly_breakdown()

    ############### Compiling transactions for transactions table ###############
    user_transactions = compiling_transactions_table()

    return render_template(
        "forex_wallet.html",
        user=current_user,
        user_assets=user_assets,
        user_asset_values=user_asset_values,
        total_asset_balance=total_asset_balance,
        total_asset_profit=total_asset_profit,
        total_asset_profit_percentage=total_asset_profit_percentage,
        total_invested=total_invested,
        total_withdrawn=total_withdrawn,
        total_invested_this_month=total_invested_this_month,
        total_sold_this_month=total_sold_this_month,
        user_transactions=user_transactions,
        buy_modal_errors=buy_modal_errors,
        sell_modal_errors=sell_modal_errors,
    )


def modal_errors():
    buy_modal_errors = request.args.get("buy_modal_errors")
    sell_modal_errors = request.args.get("sell_modal_errors")

    if buy_modal_errors is not None:
        buy_modal_errors = json.loads(buy_modal_errors)
    else:
        buy_modal_errors = {}

    if sell_modal_errors is not None:
        sell_modal_errors = json.loads(sell_modal_errors)
    else:
        sell_modal_errors = {}

    return buy_modal_errors, sell_modal_errors


def get_asset_data(cryptocurrency_code):
    cryptocurrency_data = Currency.query.filter_by(code=cryptocurrency_code).first()
    return cryptocurrency_data


def calc_asset_totals():
    user_assets = holdingAmount.query.filter_by(user_id=current_user.id).all()
    user_asset_values = {}
    asset_balance = 0

    if user_assets is not None:
        for asset in user_assets:
            asset_data = get_asset_data(asset.currency_code)

            # add asset price and name to the object
            asset.price = asset_data.current_price
            asset.name = asset_data.name
            asset.code = asset_data.code

            if asset.price is None:
                asset.price = 0

            # calculating the total value of the asset
            asset.full_value = asset.quantity * asset.price
            asset.quantity = round(asset.quantity, 6)

            # adding names and values to the dict for the charts
            asset.formatted_value = f"{asset.full_value:.1f}"
            user_asset_values[asset.code] = asset.formatted_value

            # adding the value of the asset to the total asset balance
            asset_balance += asset.full_value

            # formatting the value to 2 decimal places and adding commas to thousands
            asset.value = f"${asset.full_value:,.2f}"

            # getting all the buy and sell instances for the specific asset
            asset.buy_instances = holdingBuy.query.filter_by(
                user_id=current_user.id, currency_code=asset.currency_code
            ).all()
            asset.sell_instances = holdingSell.query.filter_by(
                user_id=current_user.id, currency_code=asset.currency_code
            ).all()

            # calculating the total amount spent on the asset
            spent_on_asset = 0
            gained_on_asset = 0

            for buy_instance in asset.buy_instances:
                spent_on_asset += buy_instance.monetary_amount
            for sell_instance in asset.sell_instances:
                gained_on_asset += sell_instance.monetary_amount

            asset.total_spent = spent_on_asset
            asset.total_gained = gained_on_asset
            average_purchase_price = (spent_on_asset * asset.quantity) / asset.quantity
            asset.average_purchase_price = average_purchase_price

            # calculating the profit/loss on the asset
            asset.profit = asset.total_gained + asset.full_value - asset.total_spent
            asset.profit_percentage = (asset.profit / asset.total_spent) * 100
            asset.profit = f"{asset.profit:,.2f}"

            # adding "$" to the profit value
            if asset.profit[0] != "-":
                asset.profit = f"${asset.profit}"
            else:
                asset.profit = f"-${asset.profit[1:]}"
            asset.profit_percentage = f"{asset.profit_percentage:,.2f}%"

    return user_assets, user_asset_values, asset_balance


def calc_total_profits(asset_balance):
    total_invested = 0
    total_withdrawn = 0

    user_buy_transactions = holdingBuy.query.filter_by(user_id=current_user.id).all()
    user_sell_transactions = holdingSell.query.filter_by(user_id=current_user.id).all()

    total_monetary_gained = 0
    total_asset_spend = 0
    value_of_remaining_assets = 0
    asset_quantities = {}

    # Calculate the total spent
    for buy_tranz in user_buy_transactions:
        total_asset_spend += buy_tranz.monetary_amount
        total_invested += buy_tranz.monetary_amount
        # if asset exists in dictionary, add to the quantity
        if buy_tranz.currency_code in asset_quantities:
            asset_quantities[buy_tranz.currency_code] += buy_tranz.currency_amount
        else:
            asset_quantities[buy_tranz.currency_code] = buy_tranz.currency_amount

    # calculating value of asset sold
    for sell_tranz in user_sell_transactions:
        total_monetary_gained += sell_tranz.monetary_amount
        total_withdrawn += sell_tranz.monetary_amount
        asset_quantities[sell_tranz.currency_code] -= sell_tranz.currency_amount

    # calculating value of remaining assets
    for asset in asset_quantities:
        asset_data = get_asset_data(asset)
        if asset_data.current_price is None:
            asset_data.current_price = 0
        value_of_remaining_assets += asset_quantities[asset] * asset_data.current_price

    # calculating total profit
    total_asset_profit = (
        total_monetary_gained + value_of_remaining_assets - total_asset_spend
    )
    if total_asset_spend != 0:
        total_asset_profit_percentage = (total_asset_profit / total_asset_spend) * 100
        total_asset_profit_percentage = f"{total_asset_profit_percentage:,.2f}%"
        if total_asset_profit >= 0:
            total_asset_profit = f"${total_asset_profit:,.2f}"
        elif total_asset_profit < 0:
            total_asset_profit = total_asset_profit * -1
            total_asset_profit = f"-${total_asset_profit:,.2f}"
    else:
        total_asset_profit_percentage = "0.00%"
        total_asset_profit = "$0.00"

    # formatting to 2 decimal places and adding commas to thousands
    total_asset_balance = f"${asset_balance:,.2f}"
    total_invested = f"${total_invested:,.2f}"
    total_withdrawn = f"${total_withdrawn:,.2f}"

    return (
        total_asset_balance,
        total_asset_profit,
        total_asset_profit_percentage,
        total_invested,
        total_withdrawn,
    )


def calc_monthly_breakdown():
    buy_transactions = holdingBuy.query.filter_by(user_id=current_user.id).all()
    sell_transactions = holdingSell.query.filter_by(user_id=current_user.id).all()

    # calculating the total invested and sold this month
    total_invested_this_month = 0
    total_sold_this_month = 0

    for buy in buy_transactions:
        if buy.date.month == datetime.now().month:
            total_invested_this_month += buy.monetary_amount
    for sell in sell_transactions:
        if sell.date.month == datetime.now().month:
            total_sold_this_month += sell.monetary_amount

    # formating after as we need to calculate the total invested this month first
    total_invested_this_month = f"${total_invested_this_month:,.2f}"
    total_sold_this_month = f"${total_sold_this_month:,.2f}"

    return total_invested_this_month, total_sold_this_month


def compiling_transactions_table():
    user_buys = holdingBuy.query.filter_by(user_id=current_user.id).all()
    user_sells = holdingSell.query.filter_by(user_id=current_user.id).all()

    # marking the buy and sell transactions as buy or sell
    for buy_transaction in user_buys:
        buy_transaction.type = "Buy"
    for sell_transaction in user_sells:
        sell_transaction.type = "Sell"

    # merging the buy and sell transactions into one list in decending order of date
    user_transactions = user_buys + user_sells
    user_transactions.sort(key=lambda x: x.date, reverse=True)
    if user_transactions is not None:
        for transaction in user_transactions:
            asset_data = get_asset_data(transaction.currency_code)
            transaction.name = asset_data.name
            transaction.currency_amount = round(transaction.currency_amount, 6)
            # formatting the value to 2 decimal places and adding commas to thousands
            transaction.value = float(transaction.monetary_amount)
            transaction.value = f"${transaction.value:,.2f}"
            # changing the date to a string in the format "Day/Month/Year"
            transaction.short_date = transaction.date.strftime("%d/%m/%Y")

    return user_transactions


@views.route("/submit-forex-buy-modal", methods=["POST"])
def submit_forex_buy():
    modal_errors = []

    # check that inputs were entered and if so return them
    asset_code, asset_amount, monetary_amount, date, description = check_for_buy_inputs(
        modal_errors
    )

    # check that inputs are valid
    check_buy_input_validity(modal_errors, asset_amount, monetary_amount, asset_code)

    # adding transaction to buy asset
    add_to_asset_buy = holdingBuy(
        currency_code=asset_code,
        user_id=current_user.id,
        currency_amount=asset_amount,
        monetary_amount=monetary_amount,
        description=description,
        date=date,
    )
    db.session.add(add_to_asset_buy)

    # updating the asset amounts table if the user already owns the asset
    user_owns_asset = holdingAmount.query.filter_by(
        currency_code=asset_code, user_id=current_user.id
    ).first()
    if user_owns_asset is None:
        add_to_asset_amounts = holdingAmount(
            currency_code=asset_code,
            quantity=asset_amount,
            user_id=current_user.id,
        )
        db.session.add(add_to_asset_amounts)
    else:
        user_owns_asset.quantity += asset_amount

    db.session.commit()

    flash("Forex asset successfully purchased.", category="success")
    return redirect(url_for("views.forex_wallet"))


def check_for_buy_inputs(modal_errors):
    asset_code = request.form.get("assetCode")
    date_input = request.form.get("transactionDate")
    description = request.form.get("description")

    # checking that a forex code was entered
    if len(asset_code) == 0:
        modal_errors.append("Please select a forex asset.")

    # checking that a asset amount was entered
    try:
        asset_amount = decimal.Decimal(request.form.get("assetAmount"))
    except decimal.InvalidOperation:
        modal_errors.append("Please enter a forex asset amount.")

    # checking that a monetary amount was entered
    try:
        monetary_amount = float(request.form.get("monetaryAmount"))
    except ValueError:
        modal_errors.append("Please enter a monetary amount.")

    # checking that a date was entered
    try:
        date = datetime.strptime(date_input, "%d/%m/%Y")
    except ValueError:
        modal_errors.append("Please enter a valid date.")

    # confirming the inputs
    if len(modal_errors) > 0:
        for error in modal_errors:
            flash(error, category="modal_error")
        buy_modal_errors = json.dumps(modal_errors)
        return redirect(
            url_for("views.forex_wallet", buy_modal_errors=buy_modal_errors)
        )

    return asset_code, asset_amount, monetary_amount, date, description


def check_buy_input_validity(modal_errors, asset_amount, monetary_amount, asset_code):
    # checking that a valid asset amount was entered
    if asset_amount == 0 or asset_amount < 0 or asset_amount is None:
        modal_errors.append("Please enter a valid asset amount.")

    # checking that a valid monetary amount was entered
    if monetary_amount == 0 or monetary_amount < 0 or monetary_amount is None:
        modal_errors.append("Please enter a valid monetary value.")

    asset_code_exists = holding.query.filter_by(code=asset_code).first()

    # checking that the forex asset code is exists in db
    if asset_code_exists is None:
        modal_errors.append("Please enter a valid forex asset code.")

    # confirming that the inputs are valid
    if len(modal_errors) > 0:
        for error in modal_errors:
            flash(error, category="modal_error")
        buy_modal_errors = json.dumps(modal_errors)
        return redirect(
            url_for("views.forex_wallet", buy_modal_errors=buy_modal_errors)
        )


@views.route("/submit-forex-sell-modal", methods=["POST"])
def submit_forex_sell():
    modal_errors = []

    # check that inputs were entered and if so return them
    (
        asset_code,
        asset_amount,
        monetary_amount,
        date,
        description,
    ) = check_for_sell_inputs(modal_errors)

    # check that inputs are valid
    check_sell_input_validity(asset_code, modal_errors, asset_amount, monetary_amount)

    # adding transaction to sell asset sell
    add_to_asset_sell = holdingSell(
        currency_code=asset_code,
        user_id=current_user.id,
        currency_amount=asset_amount,
        monetary_amount=monetary_amount,
        description=description,
        date=date,
    )
    db.session.add(add_to_asset_sell)

    # updating the asset amounts table
    user_asset_amount = holdingAmount.query.filter_by(
        currency_code=asset_code, user_id=current_user.id
    ).first()
    user_asset_amount.quantity -= asset_amount

    # if the user has sold all of their asset, delete the row from the table
    if user_asset_amount.quantity == 0:
        db.session.delete(user_asset_amount)

    db.session.commit()

    flash("Forex asset successfully sold.", category="success")
    return redirect(url_for("views.forex_wallet"))


def check_for_sell_inputs(modal_errors):
    asset_code = request.form.get("assetCode")
    date_input = request.form.get("transactionDate")
    description = request.form.get("description")

    if len(asset_code) == 0:
        modal_errors.append("Please select a forex asset.")

    try:
        asset_amount = decimal.Decimal(request.form.get("assetAmount"))
    except decimal.InvalidOperation:
        modal_errors.append("Please enter a forex asset amount.")

    try:
        monetary_amount = float(request.form.get("monetaryAmount"))
    except ValueError:
        modal_errors.append("Please enter a monetary amount.")

    try:
        date = datetime.strptime(date_input, "%d/%m/%Y")
    except ValueError:
        modal_errors.append("Please enter a valid date.")

    # checking that inputs were made
    if len(modal_errors) > 0:
        for error in modal_errors:
            flash(error, category="modal_error")
        sell_modal_errors = json.dumps(modal_errors)
        return redirect(
            url_for("views.forex_wallet", sell_modal_errors=sell_modal_errors)
        )

    return asset_code, asset_amount, monetary_amount, date, description


def check_sell_input_validity(asset_code, modal_errors, asset_amount, monetary_amount):
    user_owns_asset = holdingAmount.query.filter_by(
        currency_code=asset_code, user_id=current_user.id
    ).first()

    if user_owns_asset is None:
        modal_errors.append("You do not own this forex asset.")

    # checking that the inputs made are valid
    if asset_amount == 0 or asset_amount < 0 or asset_amount is None:
        modal_errors.append("Please enter a valid forex asset amount.")

    if monetary_amount == 0 or monetary_amount < 0 or monetary_amount is None:
        modal_errors.append("Please enter a valid monetary value.")

    if len(modal_errors) > 0:
        for error in modal_errors:
            flash(error, category="modal_error")
        sell_modal_errors = json.dumps(modal_errors)
        return redirect(
            url_for("views.forex_wallet", sell_modal_errors=sell_modal_errors)
        )