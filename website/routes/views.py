from flask import Blueprint

views = Blueprint("views", __name__)

# import functions
from .forex import *
from .stock import *
from .cryptocurrency import *
from .dashboard import *
from .exchanges import *
from .cryptocurrencies import *
from .currencies import *
from .profile import *
from .stocks import *
