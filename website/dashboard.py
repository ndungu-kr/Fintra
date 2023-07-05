from flask import render_template
from flask_login import current_user, login_required
from website.views import views
from . import db
from decimal import Decimal

from website.cryptocurrency import (
    calc_asset_totals as calc_crypto_totals,
    calc_total_profits as calc_crypto_profits,
    calc_monthly_breakdown as calc_crypto_monthly_breakdown,
    investment_history as crypto_investment_history,
)
from website.forex import (
    calc_asset_totals as calc_forex_totals,
    calc_total_profits as calc_forex_profits,
    calc_monthly_breakdown as calc_forex_monthly_breakdown,
    investment_history as forex_investment_history,
)
from website.stock import (
    calc_asset_totals as calc_stock_totals,
    calc_total_profits as calc_stock_profits,
    calc_monthly_breakdown as calc_stock_monthly_breakdown,
    investment_history as stock_investment_history,
)


@views.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    # Calculating net worth
    crypto_assets, crypto_asset_values, crypto_balance = calc_crypto_totals()
    forex_assets, forex_asset_values, forex_balance = calc_forex_totals()
    stock_assets, stock_asset_values, stock_balance = calc_stock_totals()
    net_worth = crypto_balance + forex_balance + stock_balance

    # combining asset objects (crypto_asset_values, forex_asset_values, stock_asset_values) into one object
    asset_values = {}
    for asset in crypto_asset_values:
        asset_values[asset] = crypto_asset_values[asset]
    for asset in forex_asset_values:
        asset_values[asset] = forex_asset_values[asset]
    for asset in stock_asset_values:
        asset_values[asset] = stock_asset_values[asset]

    top_5_assets = dict(
        sorted(asset_values.items(), key=lambda x: float(x[1]), reverse=True)[:5]
    )

    (
        total_crypto_profit,
        total_crypto_profit_percentage,
        crypto_invested,
        crypto_withdrawals,
    ) = calc_crypto_profits()

    (
        total_forex_profit,
        total_forex_profit_percentage,
        forex_invested,
        forex_withdrawals,
    ) = calc_forex_profits()

    (
        total_stock_profit,
        total_stock_profit_percentage,
        stock_invested,
        stock_withdrawals,
    ) = calc_stock_profits()

    # Calculating total profit
    sum_of_withdrawals = crypto_withdrawals + forex_withdrawals + stock_withdrawals
    sum_of_invested = crypto_invested + forex_invested + stock_invested

    total_profit = sum_of_withdrawals + net_worth - sum_of_invested

    # Calculating total profit percentage

    if sum_of_invested != 0:
        total_profit_percentage = (total_profit / sum_of_invested) * 100
        total_profit_percentage = f"{total_profit_percentage:,.2f}%"
        if total_profit >= 0:
            total_profit = f"${total_profit:,.2f}"
        elif total_profit < 0:
            total_profit = total_profit * -1
            total_profit = f"-${total_profit:,.2f}"
    else:
        total_profit_percentage = "0.00%"
        total_profit = "$0.00"

    # Calculating monthly breakdown
    crypto_invested_this_month, crypto_sold_this_month = calc_crypto_monthly_breakdown()
    forex_invested_this_month, forex_sold_this_month = calc_forex_monthly_breakdown()
    stock_invested_this_month, stock_sold_this_month = calc_stock_monthly_breakdown()

    total_invested_this_month = (
        crypto_invested_this_month
        + forex_invested_this_month
        + stock_invested_this_month
    )
    total_withdrawn_this_month = (
        crypto_sold_this_month + forex_sold_this_month + stock_sold_this_month
    )

    # Calculating investment history
    crypto_history = crypto_investment_history()
    forex_history = forex_investment_history()
    stock_history = stock_investment_history()

    # adding the values of the three dictionaries together
    investment_history = {}
    for key in crypto_history:
        value1 = Decimal(crypto_history[key])
        value2 = Decimal(forex_history[key])
        value3 = Decimal(stock_history[key])
        investment_history[key] = str(value1 + value2 + value3)

    # Formatting values
    net_worth = format_to_2dp_with_commas(net_worth)
    sum_of_invested = format_to_2dp_with_commas(sum_of_invested)
    sum_of_withdrawals = format_to_2dp_with_commas(sum_of_withdrawals)
    total_invested_this_month = format_to_2dp_with_commas(total_invested_this_month)
    total_withdrawn_this_month = format_to_2dp_with_commas(total_withdrawn_this_month)

    return render_template(
        "dashboard.html",
        user=current_user,
        net_worth=net_worth,
        total_profit=total_profit,
        total_profit_percentage=total_profit_percentage,
        sum_of_invested=sum_of_invested,
        sum_of_withdrawals=sum_of_withdrawals,
        total_invested_this_month=total_invested_this_month,
        total_withdrawn_this_month=total_withdrawn_this_month,
        asset_values=asset_values,
        top_5_assets=top_5_assets,
        investment_history=investment_history,
    )


def format_to_2dp_with_commas(value):
    return f"${value:,.2f}"
