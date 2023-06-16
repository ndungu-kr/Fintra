from flask import render_template
from flask_login import current_user, login_required
from website.views import views


@views.route("/forex-wallet", methods=["GET", "POST"])
@login_required
def forex_wallet():
    return render_template("forex_wallet.html", user=current_user)
