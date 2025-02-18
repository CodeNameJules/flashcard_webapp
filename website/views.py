from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/') # sub URL leads to home
def home():
    return render_template("home.html")