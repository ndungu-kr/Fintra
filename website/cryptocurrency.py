from flask import render_template
from flask_login import current_user, login_required
from website.views import views
from . import db
import decimal
import json
from datetime import datetime, timedelta
from flask import redirect, render_template, request, flash, url_for
from unicodedata import category


from website.models import (
    Cryptocurrency,
    CryptocurrencyAmount,
    CryptocurrencyBuy,
    CryptocurrencySell,
)


@views.route("/cryptocurrency-wallet", methods=["GET", "POST"])
@login_required
def cryptocurrency_wallet():
    ############### modal errors ###############
    buy_modal_errors, sell_modal_errors = modal_errors()

    ############### Getting cryptocurrency asset totals for the user ###############
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

    cryptocurrency_codes = get_cryptocurency_codes()

    return render_template(
        "cryptocurrency_wallet.html",
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
        cryptocurrency_codes=cryptocurrency_codes,
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


def get_cryptocurrency_data(code):
    cryptocurrency_data = Cryptocurrency.query.filter_by(code=code).first()
    return cryptocurrency_data


def calc_asset_totals():
    user_assets = CryptocurrencyAmount.query.filter_by(user_id=current_user.id).all()
    asset_balance = 0
    user_asset_values = {}
    if user_assets is not None:
        for crypto in user_assets:
            cryptocurrency_data = get_cryptocurrency_data(crypto.code)

            # add cryptocurrency price and name to the crypto object
            crypto.price = cryptocurrency_data.current_price
            crypto.name = cryptocurrency_data.name

            # calculating the total value of the cryptocurrency
            crypto.full_value = crypto.quantity * crypto.price
            crypto.quantity = round(crypto.quantity, 6)

            # adding names and values to the dict for the charts
            crypto.formatted_value = f"{crypto.full_value:.1f}"
            user_asset_values[crypto.name] = crypto.formatted_value

            # adding the value of the cryptocurrency to the total crypto balance
            asset_balance += crypto.full_value

            # formatting the value to 2 decimal places and adding commas to thousands
            crypto.value = f"${crypto.full_value:,.2f}"

            # getting all the buy and sell instances for the specific cryptocurrency
            crypto.buy_instances = CryptocurrencyBuy.query.filter_by(
                user_id=current_user.id, code=crypto.code
            ).all()
            crypto.sell_instances = CryptocurrencySell.query.filter_by(
                user_id=current_user.id, code=crypto.code
            ).all()

            # calculating the total amount spent on the cryptocurrency
            spent_on_asset = 0
            gained_on_asset = 0

            for buy_instance in crypto.buy_instances:
                spent_on_asset += buy_instance.monetary_amount
            for sell_instance in crypto.sell_instances:
                gained_on_asset += sell_instance.monetary_amount

            crypto.total_spent = spent_on_asset
            crypto.total_gained = gained_on_asset
            average_purchase_price = (
                spent_on_asset * crypto.quantity
            ) / crypto.quantity
            crypto.average_purchase_price = average_purchase_price

            # calculating the profit/loss on the cryptocurrency
            crypto.profit = crypto.total_gained + crypto.full_value - crypto.total_spent
            crypto.profit_percentage = (crypto.profit / crypto.total_spent) * 100
            crypto.profit = f"{crypto.profit:,.2f}"

            # adding "$" to the profit value
            if crypto.profit[0] != "-":
                crypto.profit = f"${crypto.profit}"
            else:
                crypto.profit = f"-${crypto.profit[1:]}"
            crypto.profit_percentage = f"{crypto.profit_percentage:,.2f}%"

    return user_assets, user_asset_values, asset_balance


def calc_total_profits():
    total_invested = 0
    total_withdrawn = 0
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
        crypto_data = get_cryptocurrency_data(asset)
        value_of_remaining_assets += asset_quantities[asset] * crypto_data.current_price
    # calculating total profit
    total_asset_profit = (
        total_monetary_gained + value_of_remaining_assets - total_crypto_spend
    )

    if total_crypto_spend != 0:
        total_asset_profit_percentage = (total_asset_profit / total_crypto_spend) * 100
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
    user_buy_transactions2 = CryptocurrencyBuy.query.filter_by(
        user_id=current_user.id
    ).all()
    user_sell_transactions2 = CryptocurrencySell.query.filter_by(
        user_id=current_user.id
    ).all()

    # calculating the total invested and sold this month
    total_invested_this_month = 0
    total_sold_this_month = 0

    for buy_transaction in user_buy_transactions2:
        if buy_transaction.date.month == datetime.now().month:
            total_invested_this_month += buy_transaction.monetary_amount
    for sell_transaction in user_sell_transactions2:
        if sell_transaction.date.month == datetime.now().month:
            total_sold_this_month += sell_transaction.monetary_amount

    return total_invested_this_month, total_sold_this_month


def compiling_transactions_table():
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
            cryptocurrency_data = get_cryptocurrency_data(transaction.code)
            transaction.name = cryptocurrency_data.name
            transaction.quantity = round(transaction.quantity, 6)
            # formatting the value to 2 decimal places and adding commas to thousands
            transaction.value = float(transaction.monetary_amount)
            transaction.value = f"${transaction.value:,.2f}"
            # changing the date to a string in the format "Day/Month/Year"
            transaction.short_date = transaction.date.strftime("%d/%m/%Y")

    return user_transactions


def format_to_2dp_with_commas(value):
    return f"${value:,.2f}"


def investment_history():
    # getting the buy and sell transactions for the current user
    user_buy_transactions = CryptocurrencyBuy.query.filter_by(
        user_id=current_user.id
    ).all()
    user_sell_transactions = CryptocurrencySell.query.filter_by(
        user_id=current_user.id
    ).all()

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


def get_cryptocurency_codes():
    cryptocurrencies = Cryptocurrency.query.all()
    cryptocurrency_codes = []
    for cryptocurrency in cryptocurrencies:
        cryptocurrency_codes.append(cryptocurrency.code)
    return cryptocurrency_codes


@views.route("/submit-crypto-buy-modal", methods=["POST"])
def submit_crypto_buy():
    code = request.form.get("cryptocurrency")
    date_input = request.form.get("transactionDate")
    description = request.form.get("description")
    modal_errors = []

    cryptocurrency_code_exists = Cryptocurrency.query.filter_by(code=code).first()

    if len(code) == 0:
        modal_errors.append("Please select a cryptocurrency.")
    elif cryptocurrency_code_exists is None:
        modal_errors.append(
            "Cryptocurrency does not exist. Please select one from our selection."
        )

    try:
        cryptocurrency_amount = decimal.Decimal(
            request.form.get("cryptocurrencyAmount")
        )
    except decimal.InvalidOperation:
        modal_errors.append("Please enter a cryptocurrency amount.")

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
            url_for("views.cryptocurrency_wallet", buy_modal_errors=buy_modal_errors)
        )

    if (
        cryptocurrency_amount == 0
        or cryptocurrency_amount < 0
        or cryptocurrency_amount is None
    ):
        modal_errors.append("Please enter a valid cryptocurrency amount.")

    if monetary_amount == 0 or monetary_amount < 0 or monetary_amount is None:
        modal_errors.append("Please enter a valid monetary value.")

    now = datetime.now()
    if date > now:
        modal_errors.append("You cannot enter a future date.")

    if len(modal_errors) > 0:
        for error in modal_errors:
            flash(error, category="modal_error")
        buy_modal_errors = json.dumps(modal_errors)
        return redirect(
            url_for("views.cryptocurrency_wallet", buy_modal_errors=buy_modal_errors)
        )

    else:
        # adding transaction to buy cryptocurrency
        add_to_crypto_buy = CryptocurrencyBuy(
            code=code,
            user_id=current_user.id,
            quantity=cryptocurrency_amount,
            monetary_amount=monetary_amount,
            description=description,
            date=date,
        )
        db.session.add(add_to_crypto_buy)

        # updating the cryptocurrency amounts table if the user already owns the cryptocurrency
        user_owns_asset = CryptocurrencyAmount.query.filter_by(
            code=code, user_id=current_user.id
        ).first()
        if user_owns_asset is None:
            add_to_crypto_amounts = CryptocurrencyAmount(
                code=code,
                quantity=cryptocurrency_amount,
                user_id=current_user.id,
            )
            db.session.add(add_to_crypto_amounts)
        else:
            user_owns_asset.quantity += cryptocurrency_amount

        db.session.commit()
        flash("Cryptocurrency successfully purchased.", category="success")
        return redirect(url_for("views.cryptocurrency_wallet"))


@views.route("/submit-crypto-sell-modal", methods=["POST"])
def submit_crypto_sell():
    code = request.form.get("cryptocurrency")
    date_input = request.form.get("transactionDate")
    description = request.form.get("description")
    modal_errors = []

    user_owns_crypto = CryptocurrencyAmount.query.filter_by(
        code=code, user_id=current_user.id
    ).first()

    if len(code) == 0:
        modal_errors.append("Please select a cryptocurrency.")
    elif user_owns_crypto is None:
        modal_errors.append("You do not own this cryptocurrency.")

    try:
        cryptocurrency_amount = decimal.Decimal(
            request.form.get("cryptocurrencyAmount")
        )
    except decimal.InvalidOperation:
        modal_errors.append("Please enter a cryptocurrency amount.")

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
            url_for("views.cryptocurrency_wallet", sell_modal_errors=sell_modal_errors)
        )

    # checking that the inputs made are valid
    if (
        cryptocurrency_amount == 0
        or cryptocurrency_amount < 0
        or cryptocurrency_amount is None
    ):
        modal_errors.append("Please enter a valid cryptocurrency amount.")

    if monetary_amount == 0 or monetary_amount < 0 or monetary_amount is None:
        modal_errors.append("Please enter a valid monetary value.")

    if user_owns_crypto.quantity < cryptocurrency_amount:
        modal_errors.append("You do not own enough of this asset for this transaction.")

    now = datetime.now()
    if date > now:
        modal_errors.append("You cannot enter a future date.")

    if len(modal_errors) > 0:
        for error in modal_errors:
            flash(error, category="modal_error")
        sell_modal_errors = json.dumps(modal_errors)
        return redirect(
            url_for("views.cryptocurrency_wallet", sell_modal_errors=sell_modal_errors)
        )
    else:
        # adding transaction to sell cryptocurrency
        add_to_crypto_sell = CryptocurrencySell(
            code=code,
            user_id=current_user.id,
            quantity=cryptocurrency_amount,
            monetary_amount=monetary_amount,
            description=description,
            date=date,
        )
        db.session.add(add_to_crypto_sell)

        # updating the cryptocurrency amounts table
        user_crypto_amount = CryptocurrencyAmount.query.filter_by(
            code=code, user_id=current_user.id
        ).first()
        user_crypto_amount.quantity -= cryptocurrency_amount

        # if the user has sold all of their cryptocurrency, delete the row from the table
        if user_crypto_amount.quantity == 0:
            db.session.delete(user_crypto_amount)

        db.session.commit()

        flash("Cryptocurrency successfully sold.", category="success")
        return redirect(url_for("views.cryptocurrency_wallet"))
