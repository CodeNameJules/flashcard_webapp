from flask import Blueprint, render_template, request, flash,  redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Deck, Flashcard
from . import db

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST']) # sub URL leads to home
@login_required # this route is only accessible if logged in
def home():
    if request.method == 'POST':
        deck_title = request.form.get('deck')  # Get the deck title from the form

        if len(deck_title) < 1:
            flash('Deck title is too short!', category='error')
        else:
            new_deck = Deck(title=deck_title, user_id=current_user.id)  # Create a new deck
            db.session.add(new_deck)
            db.session.commit()
            flash('Deck created!', category='success')
            return redirect(url_for('views.home'))
    return render_template("home.html", user = current_user)


@views.route('/deck/<int:deck_id>', methods=['GET', 'POST'])
@login_required
def deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)  # Get the deck or return 404 if not found

    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')

        if len(question) < 1 or len(answer) < 1:
            flash('Question and answer cannot be empty!', category='error')
        else:
            new_flashcard = Flashcard(question=question, answer=answer, deck_id=deck.id)
            db.session.add(new_flashcard)
            db.session.commit()
            flash('Flashcard added!', category='success')
            return redirect(url_for('views.deck', deck_id=deck.id))

    return render_template("deck.html", deck=deck, user=current_user)


@views.route('/delete-deck/<int:deck_id>', methods=['DELETE'])
@login_required
def delete_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)

    if deck.user_id != current_user.id:
        flash('You do not have permission to delete this deck.', category='error')
    else:
        db.session.delete(deck)
        db.session.commit()
        flash('Deck deleted!', category='success')

    return '', 204  # Return empty response for successful DELETE request

@views.route('/delete-flashcard/<int:flashcard_id>', methods=['DELETE'])
@login_required
def delete_flashcard(flashcard_id):
    flashcard = Flashcard.query.get_or_404(flashcard_id)

    if flashcard.deck.user_id != current_user.id:
        return jsonify({"error": "You do not have permission to delete this flashcard."}), 403
    else:
        db.session.delete(flashcard)
        db.session.commit()
        flash('Flashcard deleted!', category='success')

    return '', 204  # Return empty response for successful DELETE request