# 3rd party
from flask import request, flash, redirect, url_for, render_template, session,\
                  abort, Blueprint, json, g, current_app
from flask_login import login_required, current_user, logout_user, login_user
# Local
from app.tools import *
from app.model import *
from app.forms import *

bp = Blueprint('sample', __name__)

@bp.route("/")
def index():
    return 'yes!'
