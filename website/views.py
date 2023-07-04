from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

views = Blueprint("views", __name__)

# import functions
from website.forex import *
from website.stock import *
from website.cryptocurrency import *
from website.dashboard import *
