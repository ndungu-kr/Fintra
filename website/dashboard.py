from flask import render_template
from flask_login import current_user, login_required
from website.views import views
from . import db
from decimal import Decimal
from datetime import datetime, timedelta

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
from website.models import Goals


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

    goal_history = investment_goals_history()

    return render_template(
        "wallets/dashboard.html",
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
        goal_history=goal_history,
    )


def format_to_2dp_with_commas(value):
    return f"${value:,.2f}"


def investment_goals_history():
    set_goals_history = Goals.query.filter_by(user_id=current_user.id).all()

    # arrange set_goals_history in descending order of date so that the most recent goal appears first
    set_goals_history.sort(key=lambda x: x.date, reverse=True)

    now = datetime.now()
    one_month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)
    three_months_ago = now - timedelta(days=90)
    four_months_ago = now - timedelta(days=120)

    if set_goals_history:
        for goal in set_goals_history:
            # if the month of the date of the goal is the same as the month of 4 months ago
            if (
                goal.date.month == four_months_ago.month
                and goal.date.year == four_months_ago.year
            ):
                # use the goal amount as the goal for 4 months ago
                goal_four_months_ago = goal.monthly_goal
                break
            # if there is no goal for 4 months ago
            elif goal.date < four_months_ago:
                # use the next goal as the goal for 4 months ago
                goal_four_months_ago = goal.monthly_goal
            else:
                # otherwise, there is no goal for 4 months ago
                goal_four_months_ago = 0

        for goal in set_goals_history:
            if (
                goal.date.month == three_months_ago.month
                and goal.date.year == three_months_ago.year
            ):
                goal_three_months_ago = goal.monthly_goal
                break
            else:
                goal_three_months_ago = goal_four_months_ago

        for goal in set_goals_history:
            if (
                goal.date.month == two_months_ago.month
                and goal.date.year == two_months_ago.year
            ):
                goal_two_months_ago = goal.monthly_goal
                break
            else:
                goal_two_months_ago = goal_three_months_ago

        for goal in set_goals_history:
            if (
                goal.date.month == one_month_ago.month
                and goal.date.year == one_month_ago.year
            ):
                goal_one_month_ago = goal.monthly_goal
                break
            else:
                goal_one_month_ago = goal_two_months_ago

        for goal in set_goals_history:
            if goal.date.month == now.month and goal.date.year == now.year:
                goal_this_month = goal.monthly_goal
                break
            else:
                goal_this_month = goal_one_month_ago

        goals_history = {
            now.strftime("%Y-%m-%d"): goal_this_month,
            one_month_ago.strftime("%Y-%m-%d"): goal_one_month_ago,
            two_months_ago.strftime("%Y-%m-%d"): goal_two_months_ago,
            three_months_ago.strftime("%Y-%m-%d"): goal_three_months_ago,
            four_months_ago.strftime("%Y-%m-%d"): goal_four_months_ago,
        }

    else:
        goals_history = {
            now.strftime("%Y-%m-%d"): 0,
            one_month_ago.strftime("%Y-%m-%d"): 0,
            two_months_ago.strftime("%Y-%m-%d"): 0,
            three_months_ago.strftime("%Y-%m-%d"): 0,
            four_months_ago.strftime("%Y-%m-%d"): 0,
        }

    return goals_history
