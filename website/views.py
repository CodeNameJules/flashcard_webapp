from flask import Blueprint, render_template, request, flash,  redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Deck, Flashcard
from . import db
from datetime import datetime, timedelta

views = Blueprint('views', __name__)


#  Create deck
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

#  Create Flashcard
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

# Delete deck
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

#  Delete flashcard
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

# Edit deck
@views.route('/edit-deck/<int:deck_id>', methods=['GET', 'POST'])
@login_required
def edit_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)

    # Ensure the current user owns the deck
    if deck.user_id != current_user.id:
        flash('You do not have permission to edit this deck.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        new_title = request.form.get('title')

        if len(new_title) < 1:
            flash('Deck title cannot be empty.', category='error')
        else:
            deck.title = new_title
            db.session.commit()
            flash('Deck title updated!', category='success')
            return redirect(url_for('views.home'))

    return render_template("edit_deck.html", deck=deck, user=current_user)


# Edit flashcard
@views.route('/edit-flashcard/<int:flashcard_id>', methods=['GET', 'POST'])
@login_required
def edit_flashcard(flashcard_id):
    flashcard = Flashcard.query.get_or_404(flashcard_id)

    # Ensure the current user owns the flashcard's deck
    if flashcard.deck.user_id != current_user.id:
        flash('You do not have permission to edit this flashcard.', category='error')
        return redirect(url_for('views.deck', deck_id=flashcard.deck.id))

    if request.method == 'POST':
        new_question = request.form.get('question')
        new_answer = request.form.get('answer')

        if len(new_question) < 1 or len(new_answer) < 1:
            flash('Question and answer cannot be empty.', category='error')
        else:
            flashcard.question = new_question
            flashcard.answer = new_answer
            db.session.commit()
            flash('Flashcard updated!', category='success')
            return redirect(url_for('views.deck', deck_id=flashcard.deck.id))

    return render_template("edit_flashcard.html", flashcard=flashcard, user=current_user)

# Practice flashcards 
@views.route('/practice/<int:deck_id>', methods=['GET', 'POST'])
@login_required
def practice(deck_id):
    deck = Deck.query.get_or_404(deck_id)

    # Ensure the current user owns the deck
    if deck.user_id != current_user.id:
        flash('You do not have permission to practice this deck.', category='error')
        return redirect(url_for('views.home'))

    # Get flashcards due for review
    now = datetime.now()
    due_flashcards = Flashcard.query.filter(
        Flashcard.deck_id == deck_id,
        Flashcard.next_review <= now
    ).all()

    if request.method == 'POST':
        flashcard_id = request.form.get('flashcard_id')
        rating = int(request.form.get('rating'))  # 1 = Again, 2 = Hard, 3 = Good, 4 = Easy

        flashcard = Flashcard.query.get_or_404(flashcard_id)

        # Update the flashcard based on the rating (Based on Anki's SM-2 alogorithm)
        if rating == 1:  # Again
            flashcard.interval = 1 # reset the interval to be shown within a day
            flashcard.ease_factor = max(1.3, flashcard.ease_factor - 0.2) # reduce the interval so that if they do well next time it doesn't wait too long, but not below 1.3
        elif rating == 2:  # Hard
            flashcard.interval = max(1, int(flashcard.interval * 1.2)) # interval is minimum one day, else increase current interval by 20% (rounding down)
        elif rating == 3:  # Good
            flashcard.interval = max(1, int(flashcard.interval * flashcard.ease_factor)) # interval is minimum one day, or increase current interval with the ease factor (default: 2.5x) (rounding down)
        elif rating == 4:  # Easy
            flashcard.interval = max(1, int(flashcard.interval * flashcard.ease_factor * 1.5)) # interval is minimum one day, or increase current interval with the ease factor (default: 2.5x) and the bonus of 1.5 (rounding down)

        # Update the next review date
        flashcard.next_review = now + timedelta(days=flashcard.interval) # timedelta calculate dates and times
        flashcard.score = rating # update the new score
        db.session.commit()

        return redirect(url_for('views.practice', deck_id=deck_id))

    return render_template("practice.html", deck=deck, flashcards=due_flashcards, user=current_user)