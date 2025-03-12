from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        #query db by email, returns the first (and only) one if a user with that email exists
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password): # compares stored password with input password
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True) # remembers the user is logged in
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email is not associated with any account.', category='error')
    return render_template("login.html", user = current_user)


@auth.route('/logout')
@login_required #ensures this route can only be accessed if a user is logged in
def logout():
    logout_user()
    return redirect(url_for('auth.login')) # returns to log in page when user logs out


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('There is already an account with this email.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match/', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='scrypt')) #sha256 excryption
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True) # remembers the user is logged in
            flash('Account created!', category='success')
            return redirect(url_for('views.home')) # redirect to the homepage after creating user

    return render_template("sign_up.html", user = current_user)
