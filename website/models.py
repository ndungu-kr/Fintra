from email.policy import default
from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, default=0, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    transactions = db.relationship("Transaction")
    balance = db.relationship("Balance", back_populates="user")


class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="balance")
