from flask import Blueprint

views = Blueprint("views", __name__)

# import functions
from website.forex import *
from website.stock import *
from website.cryptocurrency import *
from website.dashboard import *
from website.exchanges import *
from website.cryptocurrencies import *
from website.currencies import *
