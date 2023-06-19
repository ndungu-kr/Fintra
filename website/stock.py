from flask import render_template
from flask_login import current_user, login_required
from website.stock_import import (
    get_stock_info,
    stock_import,
    stock_validity_check,
    yfinance_check,
)
from website.views import views
from . import db
import decimal
import json
from datetime import datetime
from flask import redirect, render_template, request, flash, url_for
from unicodedata import category
import yfinance as yf


from website.models import (
    Stock,
    StockAmount,
    StockBuy,
    StockSell,
)


@views.route("/stock-wallet", methods=["GET", "POST"])
@login_required
def stock_wallet():
    ############### modal errors ###############
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

    ############### Getting asset totals for the user ###############
    user_assets = StockAmount.query.filter_by(user_id=current_user.id).all()
    asset_balance = 0
    user_asset_values = {}

    if user_assets is not None:
        for asset in user_assets:
            asset_data = get_asset_data(asset.stock_code)

            # using USD price
            asset_data.price = asset_data.usd_price

            # add asset price and name to the object
            asset.price = asset_data.price
            asset.name = asset_data.name

            if asset.price is None:
                asset.price = 0

            # calculating the total value of the asset
            asset.full_value = asset.quantity * asset.price
            asset.quantity = round(asset.quantity, 6)

            # adding names and values to the dict for the charts
            asset.formatted_value = f"{asset.full_value:.1f}"
            user_asset_values[asset.name] = asset.formatted_value

            # adding the value of the asset to the total asset balance
            asset_balance += asset.full_value

            # formatting the value to 2 decimal places and adding commas to thousands
            asset.value = f"${asset.full_value:,.2f}"

            # getting all the buy and sell instances for the specific asset
            asset.buy_instances = StockBuy.query.filter_by(
                user_id=current_user.id, stock_code=asset.stock_code
            ).all()
            asset.sell_instances = StockBuy.query.filter_by(
                user_id=current_user.id, stock_code=asset.stock_code
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

    ############### Calculating total asset profit ###############
    total_invested = 0
    total_withdrawn = 0

    user_buy_transactions = StockBuy.query.filter_by(user_id=current_user.id).all()
    user_sell_transactions = StockSell.query.filter_by(user_id=current_user.id).all()

    total_monetary_gained = 0
    total_asset_spend = 0
    value_of_remaining_assets = 0
    asset_quantities = {}

    # Calculate the total spent
    for buy_tranz in user_buy_transactions:
        total_asset_spend += buy_tranz.monetary_amount
        total_invested += buy_tranz.monetary_amount
        # if asset exists in dictionary, add to the quantity
        if buy_tranz.stock_code in asset_quantities:
            asset_quantities[buy_tranz.stock_code] += buy_tranz.stock_amount
        else:
            asset_quantities[buy_tranz.stock_code] = buy_tranz.stock_amount

    # calculating value of asset sold
    for sell_tranz in user_sell_transactions:
        total_monetary_gained += sell_tranz.monetary_amount
        total_withdrawn += sell_tranz.monetary_amount
        asset_quantities[sell_tranz.stock_code] -= sell_tranz.stock_amount

    # calculating value of remaining assets
    for asset in asset_quantities:
        asset_data = get_asset_data(asset)
        if asset_data.price is None:
            asset_data.price = 0
        value_of_remaining_assets += asset_quantities[asset] * asset_data.price

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

    ############### Getting the users monthly breakdown ###############
    buy_transactions = StockBuy.query.filter_by(user_id=current_user.id).all()
    sell_transactions = StockSell.query.filter_by(user_id=current_user.id).all()

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

    ############### Compiling transactions for transactions table ###############
    user_buys = StockBuy.query.filter_by(user_id=current_user.id).all()
    user_sells = StockSell.query.filter_by(user_id=current_user.id).all()
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
            asset_data = get_asset_data(transaction.stock_code)
            transaction.name = asset_data.name
            transaction.stock_amount = round(transaction.stock_amount, 6)
            # formatting the value to 2 decimal places and adding commas to thousands
            transaction.value = float(transaction.monetary_amount)
            transaction.value = f"${transaction.value:,.2f}"
            # changing the date to a string in the format "Day/Month/Year"
            transaction.short_date = transaction.date.strftime("%d/%m/%Y")

    return render_template(
        "stock_wallet.html",
        user=current_user,
        total_asset_balance=total_asset_balance,
        total_asset_profit=total_asset_profit,
        total_asset_profit_percentage=total_asset_profit_percentage,
        total_invested=total_invested,
        total_withdrawn=total_withdrawn,
        total_invested_this_month=total_invested_this_month,
        total_sold_this_month=total_sold_this_month,
        user_assets=user_assets,
        user_transactions=user_transactions,
        buy_modal_errors=buy_modal_errors,
        sell_modal_errors=sell_modal_errors,
        user_asset_values=user_asset_values,
    )


def get_asset_data(stock_code):
    asset_data = Stock.query.filter_by(code=stock_code).first()
    return asset_data


@views.route("/submit-stock-buy-modal", methods=["POST"])
def submit_stock_buy():
    asset_code = request.form.get("assetCode")
    date_input = request.form.get("transactionDate")
    description = request.form.get("description")
    modal_errors = []

    asset_code_exists = Stock.query.filter_by(code=asset_code).first()

    if len(asset_code) == 0:
        modal_errors.append("Please select a stock.")
    elif asset_code_exists is None:
        # run stock validity check
        stock_valid = stock_validity_check(asset_code)
        if stock_valid is False:
            modal_errors.append("Cannot receive stock info, please select another.")

    try:
        asset_amount = decimal.Decimal(request.form.get("assetAmount"))
    except decimal.InvalidOperation:
        modal_errors.append("Please enter a stock amount.")

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
        buy_modal_errors = json.dumps(modal_errors)
        return redirect(
            url_for("views.stock_wallet", buy_modal_errors=buy_modal_errors)
        )

    if asset_amount == 0 or asset_amount < 0 or asset_amount is None:
        modal_errors.append("Please enter a valid asset amount.")

    if monetary_amount == 0 or monetary_amount < 0 or monetary_amount is None:
        modal_errors.append("Please enter a valid monetary value.")

    if len(modal_errors) > 0:
        for error in modal_errors:
            flash(error, category="modal_error")
        buy_modal_errors = json.dumps(modal_errors)
        return redirect(
            url_for("views.stock_wallet", buy_modal_errors=buy_modal_errors)
        )

    else:
        # adding transaction to buy asset
        add_to_asset_buy = StockBuy(
            stock_code=asset_code,
            user_id=current_user.id,
            stock_amount=asset_amount,
            monetary_amount=monetary_amount,
            description=description,
            date=date,
        )
        db.session.add(add_to_asset_buy)

        # updating the asset amounts table if the user already owns the asset
        user_owns_asset = StockAmount.query.filter_by(
            stock_code=asset_code, user_id=current_user.id
        ).first()
        if user_owns_asset is None:
            add_to_asset_amounts = StockAmount(
                stock_code=asset_code,
                quantity=asset_amount,
                user_id=current_user.id,
            )
            db.session.add(add_to_asset_amounts)
        else:
            user_owns_asset.quantity += asset_amount

        db.session.commit()

        flash("Stock successfully purchased.", category="success")
        return redirect(url_for("views.stock_wallet"))


@views.route("/submit-stock-sell-modal", methods=["POST"])
def submit_stock_sell():
    asset_code = request.form.get("assetCode")
    date_input = request.form.get("transactionDate")
    description = request.form.get("description")
    modal_errors = []

    user_owns_asset = StockAmount.query.filter_by(
        stock_code=asset_code, user_id=current_user.id
    ).first()

    if len(asset_code) == 0:
        modal_errors.append("Please select a stock.")
    elif user_owns_asset is None:
        modal_errors.append("You do not own this stock.")

    try:
        asset_amount = decimal.Decimal(request.form.get("assetAmount"))
    except decimal.InvalidOperation:
        modal_errors.append("Please enter a stock amount.")

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
            url_for("views.stock_wallet", sell_modal_errors=sell_modal_errors)
        )

    # checking that the inputs made are valid
    if asset_amount == 0 or asset_amount < 0 or asset_amount is None:
        modal_errors.append("Please enter a valid stock amount.")

    if monetary_amount == 0 or monetary_amount < 0 or monetary_amount is None:
        modal_errors.append("Please enter a valid monetary value.")

    if len(modal_errors) > 0:
        for error in modal_errors:
            flash(error, category="modal_error")
        sell_modal_errors = json.dumps(modal_errors)
        return redirect(
            url_for("views.stock_wallet", sell_modal_errors=sell_modal_errors)
        )
    else:
        # adding transaction to sell asset sell
        add_to_asset_sell = StockSell(
            stock_code=asset_code,
            user_id=current_user.id,
            stock_amount=asset_amount,
            monetary_amount=monetary_amount,
            description=description,
            date=date,
        )
        db.session.add(add_to_asset_sell)

        # updating the asset amounts table
        user_asset_amount = StockAmount.query.filter_by(
            stock_code=asset_code, user_id=current_user.id
        ).first()
        user_asset_amount.quantity -= asset_amount

        # if the user has sold all of their asset, delete the row from the table
        if user_asset_amount.quantity == 0:
            db.session.delete(user_asset_amount)

        db.session.commit()

        flash("Stock successfully sold.", category="success")
        return redirect(url_for("views.stock_wallet"))
