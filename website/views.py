from unicodedata import category
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user

# from .models import Transaction
from . import db
import json

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        pass
        # description = request.form.get("description")
        # transaction_amount = request.form.get("transaction_amount")

        # if len(description) < 1:
        #     flash("Note is too short", category="error")
        # elif transaction_amount == 0:
        #     flash("Please enter an amount", category="error")
        # else:
        #     new_description = Transaction(
        #         description=description,
        #         user_id=current_user.id,
        #         amount=transaction_amount,
        #     )
        #     db.session.add(new_description)
        #     db.session.add()
        #     db.session.commit()
        #     flash("Transaction successfully added.", category="success")
    else:
        pass
    return render_template("dashboard.html", user=current_user)


@views.route("/delete-transaction", methods=["POST"])
def delete_transaction():
    # transaction = json.loads(request.data)
    # transactionId = transaction["transactionId"]
    # transaction = Transaction.query.get(transactionId)
    # if transaction:
    #     if transaction.user_id == current_user.id:
    #         db.session.delete(transaction)
    #         db.session.commit()

    return jsonify({})
