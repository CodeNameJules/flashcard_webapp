from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/') # sub URL leads to home
@login_required # this route is only accessible if logged in
def home():
    return render_template("home.html", user = current_user)