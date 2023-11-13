from flask import render_template
from flask_login import current_user, login_required
from website.views import views
from . import db
from website.models import Exchange


@views.route("/exchanges", methods=["GET", "POST"])
@login_required
def exchanges():
    exchanges = Exchange.query.all()

    # arrange exchanges in alphabetical order
    exchanges.sort(key=lambda x: x.country)

    return render_template("assets/exchanges.html", user=current_user, exchanges=exchanges)
