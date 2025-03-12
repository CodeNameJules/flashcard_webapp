from . import db # importing from this package (website folder)
from flask_login import UserMixin # Flask module that makes login simpler
from sqlalchemy.sql import func # if i want auto populated date

class Flashcard(db.Model): # Model is like a blueprint for the class, ie that all flashcards need to look like this
    id = db.Column(db.Integer, primary_key=True) # default is that the id is auto incremented
    question = db.Column(db.String(300))
    answer = db.Column(db.String(300))
    score = db.Column(db.Integer)
    # date = db.Column(db.DateTime(timezone=True), default=func.now())
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))
    deck = db.relationship('Deck', back_populates='flashcards') # back-reference so I cana ccess Deck objects from Flashcard objects

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    # date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    flashcards = db.relationship('Flashcard', back_populates='deck') # creates a relationship with the Flashcard class, will store a list of all the cards
    user = db.relationship('User', back_populates='decks')

class User(db.Model, UserMixin): # inherit db model and UserMixin
    id = db.Column(db.Integer, primary_key=True) # db.Integer sets the type
    email = db.Column(db.String(150), unique=True) # number in db.String() is the char limit
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    decks = db.relationship('Deck', back_populates='user')  # creates a relationship with the Deck class, will store a list of all their decks
