from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models import Deck

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST']) # sub URL leads to home
@login_required # this route is only accessible if logged in
def home():
    # if request.method == 'POST': 
    #     deck = request.form.get('note')#Gets the note from the HTML 

    #     if len(deck) < 1:
    #         flash('Note is too short!', category='error') 
    #     else:
    #         new_deck = Deck(data=note, user_id=current_user.id)  #providing the schema for the note 
    #         db.session.add(new_note) #adding the note to the database 
    #         db.session.commit()
    #         flash('Note added!', category='success')
    return render_template("home.html", user = current_user)