from flask import render_template
from flask_login import current_user, login_required
from website.views import views


@views.route("/stock-wallet", methods=["GET", "POST"])
@login_required
def stock_wallet():
    return render_template("stock_wallet.html", user=current_user)
