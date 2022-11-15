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
    wallet_balances = db.relationship(
        "WalletBalance", backref="wallet_balances", lazy=True
    )
    crypto_wallet = db.relationship("CryptoWallet", backref="wallet", uselist=False)
    forex_wallet = db.relationship("ForexWallet", backref="wallet", uselist=False)
    stock_wallet = db.relationship("StockWallet", backref="wallet", uselist=False)


class WalletBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    balance = db.Column(db.DECIMAL, nullable=False, default=0)
    total_monetary_invested = db.Column(db.DECIMAL, nullable=False, default=0)
    total_monetary_withdrawn = db.Column(db.DECIMAL, nullable=False, default=0)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# class Cryptocurrency(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(200), nullable=False)


# class Currency(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(200), nullable=False)
#     symbol = db.Column(db.String(5), nullable=False)


# class Stock(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(200), nullable=False)


class CryptoWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(
        db.Integer, db.ForeignKey("wallet.id"), unique=True, nullable=False
    )
    crytocurrency_buys = db.relationship(
        "CryptocurrencyBuy", backref="crytocurrency_buys", lazy=True
    )
    crypto_wallet_balances = db.relationship(
        "CryptoWalletBalance", backref="crypto_wallet_balances", lazy=True
    )
    crytocurrency_sells = db.relationship(
        "CryptocurrencySell", backref="crytocurrency_sells", lazy=True
    )


class ForexWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(
        db.Integer, db.ForeignKey("wallet.id"), unique=True, nullable=False
    )
    forex_buys = db.relationship("ForexBuy", backref="forex_buys", lazy=True)
    forex_wallet_balances = db.relationship(
        "ForexWalletBalance", backref="forex_wallet_balances", lazy=True
    )
    forex_sells = db.relationship("ForexSell", backref="forex_sells", lazy=True)


class StockWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(
        db.Integer, db.ForeignKey("wallet.id"), unique=True, nullable=False
    )
    stock_buys = db.relationship("StockBuy", backref="stock_buys", lazy=True)
    stock_wallet_balances = db.relationship(
        "StockWalletBalance", backref="stock_wallet_balances", lazy=True
    )
    stock_sells = db.relationship("StockSell", backref="stock_sells", lazy=True)


class CryptocurrencyBuy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cryptocurrency_code = db.Column(db.String, nullable=False)
    crypto_wallet_id = db.Column(
        db.Integer, db.ForeignKey("crypto_wallet.id"), nullable=False
    )
    crypto_amount_bought = db.Column(db.NUMERIC, nullable=False)
    monetary_amount_invested = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rate = db.Column(db.NUMERIC, nullable=False)

    def __repr__(self):
        return f"CryptocurrencyBuy('{self.cryptocurrency_code}', '{self.crypto_amount_bought}', '{self.monetary_amount_invested}', '{self.description}', '{self.date}')"


class CryptoWalletBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crypto_wallet_id = db.Column(
        db.Integer, db.ForeignKey("crypto_wallet.id"), nullable=False
    )
    balance = db.Column(db.DECIMAL, nullable=False, default=0)
    total_monetary_invested = db.Column(db.DECIMAL, nullable=False, default=0)
    total_monetary_withdrawn = db.Column(db.DECIMAL, nullable=False, default=0)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class CryptocurrencySell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cryptocurrency_code = db.Column(db.String, nullable=False)
    crypto_wallet_id = db.Column(
        db.Integer, db.ForeignKey("crypto_wallet.id"), nullable=False
    )
    crypto_amount_sold = db.Column(db.NUMERIC, nullable=False)
    monetary_amount_withdrawn = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rate = db.Column(db.NUMERIC, nullable=False)

    def __repr__(self):
        return f"CryptocurrencySell('{self.cryptocurrency_code}', '{self.crypto_amount_sold}', '{self.monetary_amount_withdrawn}', '{self.description}', '{self.date}')"


class ForexBuy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String, nullable=False)
    forex_wallet_id = db.Column(
        db.Integer, db.ForeignKey("forex_wallet.id"), nullable=False
    )
    currency_amount_bought = db.Column(db.NUMERIC, nullable=False)
    monetary_amount_invested = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rate = db.Column(db.NUMERIC, nullable=False)

    def __repr__(self):
        return f"ForexBuy('{self.currency_code}', '{self.currency_amount_bought}', '{self.monetary_amount_invested}', '{self.description}', '{self.date}')"


class ForexWalletBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forex_wallet_id = db.Column(
        db.Integer, db.ForeignKey("forex_wallet.id"), nullable=False
    )
    balance = db.Column(db.DECIMAL, nullable=False, default=0)
    total_monetary_invested = db.Column(db.DECIMAL, nullable=False, default=0)
    total_monetary_withdrawn = db.Column(db.DECIMAL, nullable=False, default=0)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class ForexSell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String, nullable=False)
    forex_wallet_id = db.Column(
        db.Integer, db.ForeignKey("forex_wallet.id"), nullable=False
    )
    currency_amount_sold = db.Column(db.NUMERIC, nullable=False)
    monetary_amount_withdrawn = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rate = db.Column(db.NUMERIC, nullable=False)

    def __repr__(self):
        return f"ForexSell('{self.currency_code}', '{self.currency_amount_sold}', '{self.monetary_amount_withdrawn}', '{self.description}', '{self.date}')"


class StockBuy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String, nullable=False)
    stock_wallet_id = db.Column(
        db.Integer, db.ForeignKey("stock_wallet.id"), nullable=False
    )
    stock_amount_bought = db.Column(db.NUMERIC, nullable=False)
    monetary_amount_invested = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rate = db.Column(db.NUMERIC, nullable=False)

    def __repr__(self):
        return f"StockBuy('{self.stock_code}', '{self.stock_amount_bought}', '{self.monetary_amount_invested}', '{self.description}', '{self.date}')"


class StockWalletBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_wallet_id = db.Column(
        db.Integer, db.ForeignKey("stock_wallet.id"), nullable=False
    )
    balance = db.Column(db.DECIMAL, nullable=False, default=0)
    total_monetary_invested = db.Column(db.DECIMAL, nullable=False, default=0)
    total_monetary_withdrawn = db.Column(db.DECIMAL, nullable=False, default=0)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class StockSell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String, nullable=False)
    stock_wallet_id = db.Column(
        db.Integer, db.ForeignKey("stock_wallet.id"), nullable=False
    )
    stock_amount_sold = db.Column(db.NUMERIC, nullable=False)
    monetary_amount_withdrawn = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rate = db.Column(db.NUMERIC, nullable=False)

    def __repr__(self):
        return f"StockSell('{self.stock_code}', '{self.stock_amount_sold}', '{self.monetary_amount_withdrawn}', '{self.description}', '{self.date}')"
