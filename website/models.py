from email.policy import default
from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import backref
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    wallet = db.relationship("Wallet", backref="user", uselist=False)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.email}')"


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    total_balance = db.Column(db.DECIMAL, nullable=False, default=0)
    # deposits = db.relationship("Deposit", backref="deposits", lazy=True)
    # withdrawals = db.relationship("Withdrawal", backref="withdrawals", lazy=True)
    crypto_wallet = db.relationship("CryptoWallet", backref="wallet", uselist=False)
    forex_wallet = db.relationship("ForexWallet", backref="wallet", uselist=False)
    stock_wallet = db.relationship("StockWallet", backref="wallet", uselist=False)


# class Deposit(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     amount = db.Column(db.DECIMAL, nullable=False)
#     date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     description = db.Column(db.Text, nullable=False)
#     wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)

#     def __repr__(self):
#         return f"Deposit('{self.id}', '{self.date}')"


# class Withdrawal(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     description = db.Column(db.Text, nullable=False)
#     wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
#     amount = db.Column(db.DECIMAL, nullable=False)

# def __repr__(self):
#     return f"Deposit('{self.id}', '{self.date}')"


class Cryptocurrency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    value = db.Column(db.DECIMAL, nullable=False)
    transactions = db.relationship(
        "CryptocurrencyTransaction", backref="cryptocurrency", lazy=True
    )


class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    value = db.Column(db.DECIMAL, nullable=False)
    symbol = db.Column(db.String(5), nullable=False)
    transactions = db.relationship("ForexTransaction", backref="currency", lazy=True)


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    value = db.Column(db.DECIMAL, nullable=False)
    transactions = db.relationship("StockTransaction", backref="stock", lazy=True)


class CryptoWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transactions = db.relationship(
        "CryptocurrencyTransaction", backref="transactions", lazy=True
    )
    wallet_id = db.Column(
        db.Integer, db.ForeignKey("wallet.id"), unique=True, nullable=False
    )
    balance = db.Column(db.DECIMAL, nullable=False, default=0)


class ForexWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transactions = db.relationship(
        "ForexTransaction", backref="transactions", lazy=True
    )
    wallet_id = db.Column(
        db.Integer, db.ForeignKey("wallet.id"), unique=True, nullable=False
    )
    balance = db.Column(db.DECIMAL, nullable=False, default=0)


class StockWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transactions = db.relationship(
        "StockTransaction", backref="transactions", lazy=True
    )
    wallet_id = db.Column(
        db.Integer, db.ForeignKey("wallet.id"), unique=True, nullable=False
    )
    balance = db.Column(db.DECIMAL, nullable=False, default=0)


class CryptocurrencyTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    crypto_wallet_id = db.Column(
        db.Integer, db.ForeignKey("crypto_wallet.id"), nullable=False
    )  # check here if relationships are messed up
    cryptocurrency_id = db.Column(
        db.Integer, db.ForeignKey("cryptocurrency.id"), nullable=False
    )
    crypto_amount = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    bos = db.Column(db.BOOLEAN, nullable=False)  # buy = 1 and sell = 0
    rate = db.Column(db.NUMERIC, nullable=False)

    def __repr__(self):
        return f"Deposit('{self.id}', '{self.date}')"


class ForexTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    forex_wallet_id = db.Column(
        db.Integer, db.ForeignKey("forex_wallet.id"), nullable=False
    )  # check here if relationships are messed up
    currency_id = db.Column(db.Integer, db.ForeignKey("currency.id"), nullable=False)
    currency_amount = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    bos = db.Column(db.BOOLEAN, nullable=False)  # buy = 1 and sell = 0
    rate = db.Column(db.NUMERIC, nullable=False)

    def __repr__(self):
        return f"Deposit('{self.id}', '{self.date}')"


class StockTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    stock_wallet_id = db.Column(
        db.Integer, db.ForeignKey("stock_wallet.id"), nullable=False
    )  # check here if relationships are messed up
    stock_id = db.Column(db.Integer, db.ForeignKey("stock.id"), nullable=False)
    stock_amount = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    bos = db.Column(db.BOOLEAN, nullable=False)  # buy = 1 and sell = 0
    rate = db.Column(db.NUMERIC, nullable=False)

    def __repr__(self):
        return f"Deposit('{self.id}', '{self.date}')"
