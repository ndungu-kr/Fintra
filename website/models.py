from email.policy import default
from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.orm import backref
from datetime import datetime

# from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.email}')"


class CryptocurrencyBuy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, db.ForeignKey("cryptocurrency.code"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"CryptocurrencyBuy('{self.code}', '{self.quantity}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class CryptocurrencySell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, db.ForeignKey("cryptocurrency.code"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"CryptocurrencySell('{self.code}', '{self.quantity}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class ForexBuy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, db.ForeignKey("forex.code"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"ForexBuy('{self.code}', '{self.quantity}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class ForexSell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, db.ForeignKey("forex.code"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"ForexSell('{self.code}', '{self.quantity}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class StockBuy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, db.ForeignKey("stock.code"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"StockBuy('{self.code}', '{self.quantity}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class StockSell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, db.ForeignKey("stock.code"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    monetary_amount = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"StockSell('{self.code}', '{self.quantity}', '{self.monetary_amount}', '{self.description}', '{self.date}')"


class Cryptocurrency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    current_price = db.Column(db.DECIMAL, nullable=False, default=0)
    market_cap = db.Column(db.DECIMAL, nullable=False, default=0)
    circulating_supply = db.Column(db.DECIMAL, nullable=False, default=0)
    total_supply = db.Column(db.DECIMAL, nullable=False, default=0)
    max_supply = db.Column(db.DECIMAL, nullable=False, default=0)
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


class Forex(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    symbol = db.Column(db.String(5))
    current_price = db.Column(db.DECIMAL, default=0)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    forex_purchased = db.relationship("ForexBuy", backref="forex_purchased", lazy=True)
    forex_sold = db.relationship("ForexSell", backref="forex_sold", lazy=True)
    currency_asset_amounts = db.relationship(
        "ForexAmount", backref="currency_asset_amounts", lazy=True
    )


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.DECIMAL)
    usd_price = db.Column(db.DECIMAL)
    exchange = db.Column(db.String(200))
    market_cap = db.Column(db.DECIMAL)
    country = db.Column(db.String(200))
    currency = db.Column(db.String(200))
    sector = db.Column(db.String(200))
    price_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)
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
    code = db.Column(db.String, db.ForeignKey("cryptocurrency.code"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class ForexAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, db.ForeignKey("forex.code"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class StockAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, db.ForeignKey("stock.code"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quantity = db.Column(db.NUMERIC, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Exchange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    suffix = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(200), nullable=False)
