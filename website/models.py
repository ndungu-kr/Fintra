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


class CryptocurrencyBuy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cryptocurrency_code = db.Column(
        db.String, db.ForeignKey("cryptocurrency.code"), nullable=False
    )
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    crypto_amount = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"CryptocurrencyBuy('{self.cryptocurrency_code}', '{self.crypto_amount}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class CryptocurrencySell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cryptocurrency_code = db.Column(
        db.String, db.ForeignKey("cryptocurrency.code"), nullable=False
    )
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    crypto_amount = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"CryptocurrencySell('{self.cryptocurrency_code}', '{self.crypto_amount}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class ForexBuy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String, db.ForeignKey("currency.code"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    currency_amount = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"ForexBuy('{self.currency_code}', '{self.currency_amount}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class ForexSell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String, db.ForeignKey("currency.code"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    currency_amount = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"ForexSell('{self.currency_code}', '{self.currency_amount}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class StockBuy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String, db.ForeignKey("stock.code"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    stock_amount = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"StockBuy('{self.stock_code}', '{self.stock_amount}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class StockSell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String, db.ForeignKey("stock.code"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    stock_amount = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"StockSell('{self.stock_code}', '{self.stock_amount}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class Cryptocurrency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    current_price = db.Column(db.DECIMAL, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    crytocurrency_purchased = db.relationship(
        "CryptocurrencyBuy", backref="crytocurrency_purchased", lazy=True
    )
    crytocurrency_sold = db.relationship(
        "CryptocurrencySell", backref="crytocurrency_sold", lazy=True
    )
    crytocurrency_asset_amounts = db.relationship(
        "CryptocurrencyAmount", backref="crytocurrency_asset_amounts", lazy=True
    )


class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    symbol = db.Column(db.String(5))
    current_price = db.Column(db.DECIMAL, default=0)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    forex_purchased = db.relationship("ForexBuy", backref="forex_purchased", lazy=True)
    forex_sold = db.relationship("ForexSell", backref="forex_sold", lazy=True)
    currency_asset_amounts = db.relationship(
        "CurrencyAmount", backref="currency_asset_amounts", lazy=True
    )


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5))
    name = db.Column(db.String(200), nullable=False)
    current_price = db.Column(db.DECIMAL, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    stock_purchased = db.relationship("StockBuy", backref="stock_purchased", lazy=True)
    stock_sold = db.relationship("StockSell", backref="stock_sold", lazy=True)
    stock_asstet_amounts = db.relationship(
        "StockAmount", backref="stock_asset_amounts", lazy=True
    )


class AssetLastUpdated(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset = db.Column(db.String(64), nullable=False, unique=True)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class CryptocurrencyAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cryptocurrency_code = db.Column(
        db.String, db.ForeignKey("cryptocurrency.code"), nullable=False
    )
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class CurrencyAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String, db.ForeignKey("currency.code"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class StockAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String, db.ForeignKey("stock.code"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
