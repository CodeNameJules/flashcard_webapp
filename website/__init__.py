from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy() # db will be used to interact with database
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__) # represents the name of the file that was ran(?)
    app.config['SECRET_KEY'] = 'superdupersecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app) # takes database to use with app

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Deck, Flashcard

    create_database(app)

    return app

def create_database(app): # checks if the db already exists so it doesn't get overwritten each time
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')