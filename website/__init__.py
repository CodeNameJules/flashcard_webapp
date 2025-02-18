from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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

    return app
