from flask import render_template
from flask_login import current_user, login_required
from ..utils.stock_import import stock_validity_check
from .views import views
from .. import db
import decimal
import json
from datetime import datetime, timedelta
from flask import redirect, render_template, request, flash, url_for
from unicodedata import category


from website.models import (
    Exchange,
    Stock,
    StockAmount,
    StockBuy,
    StockSell,
    Goals,
)


@views.route("/stock-wallet", methods=["GET", "POST"])
@login_required
def stock_wallet():
    ############### modal errors ###############
    buy_modal_errors, sell_modal_errors = modal_errors()

    ############### Getting asset totals for the user ###############
    user_assets, user_asset_values, asset_balance = calc_asset_totals()
    total_asset_balance = format_to_2dp_with_commas(asset_balance)

    ############### Calculating total asset profit ###############
    (
        total_asset_profit,
        total_asset_profit_percentage,
        total_invested,
        total_withdrawn,
    ) = calc_total_profits()
    # Formatting values
    total_invested = format_to_2dp_with_commas(total_invested)
    total_withdrawn = format_to_2dp_with_commas(total_withdrawn)

    ############### Getting the users monthly breakdown ###############
    total_invested_this_month, total_sold_this_month = calc_monthly_breakdown()
    # Formatting values
    total_invested_this_month = format_to_2dp_with_commas(total_invested_this_month)
    total_sold_this_month = format_to_2dp_with_commas(total_sold_this_month)

    ############### Compiling transactions for transactions table ###############
    user_transactions = compiling_transactions_table()

    five_month_history = investment_history()

    asset_codes = get_asset_codes()
    exchanges = get_exchanges()
    goal_history = get_goal_history()

    return render_template(
        "wallets/stock_wallet.html",
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
        five_month_history=five_month_history,
        asset_codes=asset_codes,
        exchanges=exchanges,
        goal_history=goal_history,
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


def get_asset_data(code):
    asset_data = Stock.query.filter_by(code=code).first()
    return asset_data


def calc_asset_totals():
    user_assets = StockAmount.query.filter_by(user_id=current_user.id).all()
    asset_balance = 0
    user_asset_values = {}

    if user_assets is not None:
        for asset in user_assets:
            asset_data = get_asset_data(asset.code)

            # using USD price
            if asset_data.usd_price is not None:
                asset_data.price = asset_data.usd_price

            # add asset price and name to the object
            asset.price = asset_data.price
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
            asset.buy_instances = StockBuy.query.filter_by(
                user_id=current_user.id, code=asset.code
            ).all()
            asset.sell_instances = StockSell.query.filter_by(
                user_id=current_user.id, code=asset.code
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


def calc_total_profits():
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
        if buy_tranz.code in asset_quantities:
            asset_quantities[buy_tranz.code] += buy_tranz.quantity
        else:
            asset_quantities[buy_tranz.code] = buy_tranz.quantity

    # calculating value of asset sold
    for sell_tranz in user_sell_transactions:
        total_monetary_gained += sell_tranz.monetary_amount
        total_withdrawn += sell_tranz.monetary_amount
        asset_quantities[sell_tranz.code] -= sell_tranz.quantity

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

    return (
        total_asset_profit,
        total_asset_profit_percentage,
        total_invested,
        total_withdrawn,
    )


def calc_monthly_breakdown():
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

    return total_invested_this_month, total_sold_this_month


def compiling_transactions_table():
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
            asset_data = get_asset_data(transaction.code)
            transaction.name = asset_data.name
            transaction.quantity = round(transaction.quantity, 6)
            # formatting the value to 2 decimal places and adding commas to thousands
            transaction.value = float(transaction.monetary_amount)
            transaction.value = f"${transaction.value:,.2f}"
            # changing the date to a string in the format "Day/Month/Year"
            transaction.short_date = transaction.date.strftime("%d/%m/%Y")

    return user_transactions


def get_asset_codes():
    assets = Stock.query.all()
    asset_codes = []
    for asset in assets:
        asset_codes.append(asset.code)
    return asset_codes


def get_exchanges():
    exchanges = Exchange.query.all()
    exchange_names = []
    for exchange in exchanges:
        exchange_names.append(exchange.name)
    return exchange_names


def format_to_2dp_with_commas(value):
    return f"${value:,.2f}"


def investment_history():
    # getting the buy and sell transactions for the current user
    user_buy_transactions = StockBuy.query.filter_by(user_id=current_user.id).all()
    user_sell_transactions = StockSell.query.filter_by(user_id=current_user.id).all()

    now = datetime.now()
    one_month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)
    three_months_ago = now - timedelta(days=90)
    four_months_ago = now - timedelta(days=120)

    investments_this_month = 0
    investments_one_month_ago = 0
    investments_two_months_ago = 0
    investments_three_months_ago = 0
    investments_four_months_ago = 0

    if user_buy_transactions is not None:
        for transaction in user_buy_transactions:
            if (
                transaction.date.month == now.month
                and transaction.date.year == now.year
            ):
                investments_this_month += transaction.monetary_amount
            elif (
                transaction.date.month == one_month_ago.month
                and transaction.date.year == one_month_ago.year
            ):
                investments_one_month_ago += transaction.monetary_amount
            elif (
                transaction.date.month == two_months_ago.month
                and transaction.date.year == two_months_ago.year
            ):
                investments_two_months_ago += transaction.monetary_amount
            elif (
                transaction.date.month == three_months_ago.month
                and transaction.date.year == three_months_ago.year
            ):
                investments_three_months_ago += transaction.monetary_amount
            elif (
                transaction.date.month == four_months_ago.month
                and transaction.date.year == four_months_ago.year
            ):
                investments_four_months_ago += transaction.monetary_amount

    if user_sell_transactions is not None:
        for transaction in user_sell_transactions:
            if (
                transaction.date.month == now.month
                and transaction.date.year == now.year
            ):
                investments_this_month -= transaction.monetary_amount
            elif (
                transaction.date.month == one_month_ago.month
                and transaction.date.year == one_month_ago.year
            ):
                investments_one_month_ago -= transaction.monetary_amount
            elif (
                transaction.date.month == two_months_ago.month
                and transaction.date.year == two_months_ago.year
            ):
                investments_two_months_ago -= transaction.monetary_amount
            elif (
                transaction.date.month == three_months_ago.month
                and transaction.date.year == three_months_ago.year
            ):
                investments_three_months_ago -= transaction.monetary_amount
            elif (
                transaction.date.month == four_months_ago.month
                and transaction.date.year == four_months_ago.year
            ):
                investments_four_months_ago -= transaction.monetary_amount

    # converting the decimal values to string
    investments_this_month = str(round(investments_this_month, 2))
    investments_one_month_ago = str(round(investments_one_month_ago, 2))
    investments_two_months_ago = str(round(investments_two_months_ago, 2))
    investments_three_months_ago = str(round(investments_three_months_ago, 2))
    investments_four_months_ago = str(round(investments_four_months_ago, 2))

    # putting the data into a dictionary with date in str form as the key and investment as the value

    investment_history = {
        now.strftime("%Y-%m-%d"): investments_this_month,
        one_month_ago.strftime("%Y-%m-%d"): investments_one_month_ago,
        two_months_ago.strftime("%Y-%m-%d"): investments_two_months_ago,
        three_months_ago.strftime("%Y-%m-%d"): investments_three_months_ago,
        four_months_ago.strftime("%Y-%m-%d"): investments_four_months_ago,
    }

    return investment_history


def get_goal_history():
    all_goal_history = Goals.query.filter_by(user_id=current_user.id).all()

    # arrange all_goal_history in descending order of date so that the most recent goal appears first
    all_goal_history.sort(key=lambda x: x.date, reverse=True)

    now = datetime.now()
    one_month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)
    three_months_ago = now - timedelta(days=90)
    four_months_ago = now - timedelta(days=120)

    if all_goal_history:
        for goal in all_goal_history:
            # if the month of the date of the goal is the same as the month of 4 months ago
            if (
                goal.date.month == four_months_ago.month
                and goal.date.year == four_months_ago.year
            ):
                # use the goal amount as the goal for 4 months ago
                goal_four_months_ago = goal.stock_goal
                break
            # if there is no goal for 4 months ago
            elif goal.date < four_months_ago:
                # use the next goal as the goal for 4 months ago
                goal_four_months_ago = goal.stock_goal
            else:
                # otherwise, there is no goal for 4 months ago
                goal_four_months_ago = 0

        for goal in all_goal_history:
            if (
                goal.date.month == three_months_ago.month
                and goal.date.year == three_months_ago.year
            ):
                goal_three_months_ago = goal.stock_goal
                break
            else:
                goal_three_months_ago = goal_four_months_ago

        for goal in all_goal_history:
            if (
                goal.date.month == two_months_ago.month
                and goal.date.year == two_months_ago.year
            ):
                goal_two_months_ago = goal.stock_goal
                break
            else:
                goal_two_months_ago = goal_three_months_ago

        for goal in all_goal_history:
            if (
                goal.date.month == one_month_ago.month
                and goal.date.year == one_month_ago.year
            ):
                goal_one_month_ago = goal.stock_goal
                break
            else:
                goal_one_month_ago = goal_two_months_ago

        for goal in all_goal_history:
            if goal.date.month == now.month and goal.date.year == now.year:
                goal_this_month = goal.stock_goal
                break
            else:
                goal_this_month = goal_one_month_ago

        goal_history = {
            now.strftime("%Y-%m-%d"): goal_this_month,
            one_month_ago.strftime("%Y-%m-%d"): goal_one_month_ago,
            two_months_ago.strftime("%Y-%m-%d"): goal_two_months_ago,
            three_months_ago.strftime("%Y-%m-%d"): goal_three_months_ago,
            four_months_ago.strftime("%Y-%m-%d"): goal_four_months_ago,
        }

    else:
        goal_history = {
            now.strftime("%Y-%m-%d"): 0,
            one_month_ago.strftime("%Y-%m-%d"): 0,
            two_months_ago.strftime("%Y-%m-%d"): 0,
            three_months_ago.strftime("%Y-%m-%d"): 0,
            four_months_ago.strftime("%Y-%m-%d"): 0,
        }

    return goal_history


@views.route("/submit-stock-buy-modal", methods=["POST"])
def submit_stock_buy():
    asset_code = request.form.get("assetCode")
    date_input = request.form.get("transactionDate")
    description = request.form.get("description")
    exchange = request.form.get("exchange")
    modal_errors = []

    exchange_exists = Exchange.query.filter_by(name=exchange).first()

    # checking that a valid exchange was entered
    if len(exchange) == 0:
        modal_errors.append("Please select an exchange.")
    elif exchange_exists is None:
        modal_errors.append(
            "Please select a valid exchange. Refer to the exchanges supported."
        )

    # adding suffix to stock code if it exists
    if exchange_exists is not None:
        suffix = exchange_exists.suffix
        if suffix is not None:
            asset_code = asset_code + suffix

    # checking that a stock code was entered
    if len(asset_code) == 0:
        modal_errors.append("Please select a stock.")

    # checking that a asset amount was entered
    try:
        asset_amount = decimal.Decimal(request.form.get("assetAmount"))
    except decimal.InvalidOperation:
        modal_errors.append("Please enter a stock amount.")

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
            url_for("views.stock_wallet", buy_modal_errors=buy_modal_errors)
        )

    # checking that a valid asset amount was entered
    if asset_amount == 0 or asset_amount < 0 or asset_amount is None:
        modal_errors.append("Please enter a valid asset amount.")

    # checking that a valid monetary amount was entered
    if monetary_amount == 0 or monetary_amount < 0 or monetary_amount is None:
        modal_errors.append("Please enter a valid monetary value.")

    now = datetime.now()
    if date > now:
        modal_errors.append("You cannot enter a future date.")

    # confirming that the inputs are valid
    if len(modal_errors) > 0:
        for error in modal_errors:
            flash(error, category="modal_error")
        buy_modal_errors = json.dumps(modal_errors)
        return redirect(
            url_for("views.stock_wallet", buy_modal_errors=buy_modal_errors)
        )

    else:
        asset_code_exists = Stock.query.filter_by(code=asset_code).first()

        # checking that the stock code is exists on yfinance
        if asset_code_exists is None:
            # run stock validity check
            stock_valid = stock_validity_check(asset_code)
            if stock_valid is False:
                modal_errors.append("Cannot receive stock info, please select another.")
            # confirming that the inputs are valid
            if len(modal_errors) > 0:
                for error in modal_errors:
                    flash(error, category="modal_error")
                buy_modal_errors = json.dumps(modal_errors)
                return redirect(
                    url_for("views.stock_wallet", buy_modal_errors=buy_modal_errors)
                )

        # adding transaction to buy asset
        add_to_asset_buy = StockBuy(
            code=asset_code,
            user_id=current_user.id,
            quantity=asset_amount,
            monetary_amount=monetary_amount,
            description=description,
            date=date,
        )
        db.session.add(add_to_asset_buy)

        # updating the asset amounts table if the user already owns the asset
        user_owns_asset = StockAmount.query.filter_by(
            code=asset_code, user_id=current_user.id
        ).first()
        if user_owns_asset is None:
            add_to_asset_amounts = StockAmount(
                code=asset_code,
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
    exchange = request.form.get("exchange")
    modal_errors = []

    exchange_exists = Exchange.query.filter_by(name=exchange).first()

    # checking that a valid exchange was entered
    if len(exchange) == 0:
        modal_errors.append("Please select an exchange.")
    elif exchange_exists is None:
        modal_errors.append(
            "Please select a valid exchange. Refer to the exchanges supported."
        )

    # adding suffix to stock code if it exists
    if exchange_exists is not None:
        suffix = exchange_exists.suffix
        if suffix is not None:
            asset_code = asset_code + suffix

    user_owns_asset = StockAmount.query.filter_by(
        code=asset_code, user_id=current_user.id
    ).first()

    if len(asset_code) == 0:
        modal_errors.append("Please select a stock.")

    if user_owns_asset is None:
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

    if user_owns_asset.quantity < asset_amount:
        modal_errors.append("You do not own enough of this asset for this transaction.")

    now = datetime.now()
    if date > now:
        modal_errors.append("You cannot enter a future date.")

    # getting all crypto buys before the sell date
    asset_buys = StockBuy.query.filter(
        StockBuy.date <= date,
        StockBuy.user_id == current_user.id,
        StockBuy.code == asset_code,
    ).all()
    # getting all crypto sells before the sell date
    asset_sells = StockSell.query.filter(
        StockSell.date <= date,
        StockSell.user_id == current_user.id,
        StockSell.code == asset_code,
    ).all()

    # calculating the total amount of cryptocurrency held before the sell date
    total_asset = 0
    for buy in asset_buys:
        total_asset += buy.quantity
    for sell in asset_sells:
        total_asset -= sell.quantity

    # checking the user owned enough cryptocurrency before the sell date
    if total_asset < asset_amount:
        modal_errors.append("You did not own enough of this asset on this date.")

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
            code=asset_code,
            user_id=current_user.id,
            quantity=asset_amount,
            monetary_amount=monetary_amount,
            description=description,
            date=date,
        )
        db.session.add(add_to_asset_sell)

        # updating the asset amounts table
        user_asset_amount = StockAmount.query.filter_by(
            code=asset_code, user_id=current_user.id
        ).first()
        user_asset_amount.quantity -= asset_amount

        # if the user has sold all of their asset, delete the row from the table
        if user_asset_amount.quantity == 0:
            db.session.delete(user_asset_amount)

        db.session.commit()

        flash("Stock successfully sold.", category="success")
        return redirect(url_for("views.stock_wallet"))
