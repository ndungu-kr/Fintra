from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from website.views import views
from . import db
import decimal
import json

from website.models import Goals


@views.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    goal_modal_errors, profile_modal_errors = modal_errors()

    user_goals = get_user_goals(user=current_user)

    if user_goals:
        # latest goal is the user goal with the latest date
        latest_user_goal = user_goals[-1]

        latest_user_goal.monthly_goal = format_to_2dp_with_commas(
            latest_user_goal.monthly_goal
        )
        if latest_user_goal.crypto_goal is not None:
            latest_user_goal.crypto_goal = format_to_2dp_with_commas(
                latest_user_goal.crypto_goal
            )
        if latest_user_goal.forex_goal is not None:
            latest_user_goal.forex_goal = format_to_2dp_with_commas(
                latest_user_goal.forex_goal
            )
        if latest_user_goal.stock_goal is not None:
            latest_user_goal.stock_goal = format_to_2dp_with_commas(
                latest_user_goal.stock_goal
            )
    else:
        latest_user_goal = None

    return render_template(
        "profile.html",
        user=current_user,
        profile_modal_errors=profile_modal_errors,
        goal_modal_errors=goal_modal_errors,
        latest_user_goal=latest_user_goal,
    )


def get_user_goals(user):
    # get goals for user
    user_goals = Goals.query.filter_by(user_id=user.id).all()
    return user_goals


def format_to_2dp_with_commas(value):
    return f"${value:,.2f}"


def modal_errors():
    goal_modal_errors = request.args.get("goal_modal_errors")
    profile_modal_errors = request.args.get("profile_modal_errors")

    if goal_modal_errors is not None:
        goal_modal_errors = json.loads(goal_modal_errors)
    else:
        goal_modal_errors = {}

    if profile_modal_errors is not None:
        profile_modal_errors = json.loads(profile_modal_errors)
    else:
        profile_modal_errors = {}

    return goal_modal_errors, profile_modal_errors


@views.route("/edit-goals", methods=["POST"])
def edit_goals():
    monthly_goal = request.form.get("monthly_goal")
    crypto_goal = request.form.get("crypto_goal")
    forex_goal = request.form.get("forex_goal")
    stock_goal = request.form.get("stock_goal")
    goal_modal_errors = []

    if len(monthly_goal) == 0:
        goal_modal_errors.append("Monthly goal cannot be empty")

    try:
        monthly_goal = decimal.Decimal(monthly_goal)
    except decimal.InvalidOperation:
        goal_modal_errors.append("Please enter a valid number for monthly goal.")

    if len(goal_modal_errors) > 0:
        for error in goal_modal_errors:
            flash(error, category="modal_error")
        goal_modal_errors = json.dumps(goal_modal_errors)
        return redirect(url_for("views.profile", goal_modal_errors=goal_modal_errors))

    if len(crypto_goal) > 0 or len(forex_goal) > 0 or len(stock_goal) > 0:
        try:
            crypto_goal = decimal.Decimal(crypto_goal)
        except decimal.InvalidOperation:
            goal_modal_errors.append("Please enter a valid number for crypto goal.")
        try:
            forex_goal = decimal.Decimal(forex_goal)
        except decimal.InvalidOperation:
            goal_modal_errors.append("Please enter a valid number for forex goal.")
        try:
            stock_goal = decimal.Decimal(stock_goal)
        except decimal.InvalidOperation:
            goal_modal_errors.append("Please enter a valid number for stock goal.")

        total_goals = crypto_goal + forex_goal + stock_goal

        if monthly_goal != total_goals:
            goal_modal_errors.append(
                "Monthly goal must equal the sum of all other goals."
            )

        if len(goal_modal_errors) > 0:
            for error in goal_modal_errors:
                flash(error, category="modal_error")
            goal_modal_errors = json.dumps(goal_modal_errors)
            return redirect(
                url_for("views.profile", goal_modal_errors=goal_modal_errors)
            )
    else:
        crypto_goal = 0
        forex_goal = 0
        stock_goal = 0

    add_goals = Goals(
        user_id=current_user.id,
        monthly_goal=monthly_goal,
        crypto_goal=crypto_goal,
        forex_goal=forex_goal,
        stock_goal=stock_goal,
    )
    db.session.add(add_goals)
    db.session.commit()
    flash("Goals successfully updated.", category="success")
    return redirect(url_for("views.profile"))
