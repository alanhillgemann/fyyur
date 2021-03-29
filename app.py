#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


from datetime import timezone
import babel
import dateutil.parser
from enum import Enum
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_migrate import Migrate
from flask_moment import Moment
from flask_wtf import Form
from flask_sqlalchemy import SQLAlchemy
from forms import *
import json
import logging
from logging import Formatter, FileHandler
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import cast
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(500))
    artists = db.relationship("Show", back_populates="venue", cascade='delete')

    def __repr__(self):
        return str(self.__dict__)

    def as_dict(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'address': self.address,
        'phone': self.phone,
        'genres': self.genres,
        'facebook_link': self.facebook_link,
        'image_link': self.image_link,
        'website': self.website,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description
      }


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(500))
    venues = db.relationship("Show", back_populates="artist", cascade='delete')

    def __repr__(self):
        return str(self.__dict__)

    def as_dict(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres,
        'facebook_link': self.facebook_link,
        'image_link': self.image_link,
        'website': self.website,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description
      }


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    venue = db.relationship("Venue", back_populates="artists")
    artist = db.relationship("Artist", back_populates="venues")

    def __repr__(self):
        return str(self.__dict__)

    def as_dict(self):
      return {
        'id': self.id,
        'artist_id': self.artist_id,
        'venue_id': self.venue_id,
        'start_time': self.start_time
      }


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    error = 0
    try:
        areas = []
        for state, city in Venue.query.with_entities(Venue.state, Venue.city).distinct().order_by(Venue.state, Venue.city).all():
            area = {'city': city, 'state': state, 'venues': []}
            for id, name in Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.state==state, Venue.city==city).order_by(Venue.name).all():
                num_upcoming_shows = Show.query.filter(Show.venue_id==id, Show.start_time>=datetime.now()).count()
                venue = {'id': id, 'name': name, 'num_upcoming_shows': num_upcoming_shows}
                area['venues'].append(venue)
            areas.append(area)
        return render_template('pages/venues.html', areas=areas)
    except:
        error = 500
        print(sys.exc_info())
    handle_error(error)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    error = 0
    try:
        results = {'count': 0, 'data': []}
        search_term = request.form.get('search_term', '')
        for id, name in Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.ilike(f'%{search_term}%')).all():
            num_upcoming_shows = Show.query.filter(Show.venue_id==id, Show.start_time>=datetime.now()).count()
            venue = {'id': id, 'name': name, 'num_upcoming_shows': num_upcoming_shows}
            results['data'].append(venue)
        results['count'] = len(results['data'])
        return render_template('pages/search_venues.html', results=results, search_term=search_term)
    except:
        error = 500
        print(sys.exc_info())
    handle_error(error)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    error = 0
    try:
        venue = Venue.query.get(venue_id)
        if venue is not None:
            venue_with_shows = venue.as_dict()
            past_shows, upcoming_shows = [], []
            for show in venue.artists:
                show_details = {
                    'artist_id': show.artist_id,
                    'artist_name': show.artist.name,
                    'artist_image_link': show.artist.image_link,
                    'start_time': show.start_time
                }
                if show.start_time < datetime.now():
                    past_shows.append(show_details)
                else:
                    upcoming_shows.append(show_details)
            venue_with_shows['past_shows'] = past_shows
            venue_with_shows['upcoming_shows'] = upcoming_shows
            venue_with_shows['past_shows_count'] = len(past_shows)
            venue_with_shows['upcoming_shows_count'] = len(upcoming_shows)
            return render_template('pages/show_venue.html', venue=venue_with_shows)
        else:
            error = 404
    except:
        error = 500
        print(sys.exc_info())
    handle_error(error, 'Venue', venue_id)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = 0
    try:
        form = VenueForm()
        if form.validate_on_submit():
            venue = Venue()
            form.populate_obj(venue)
            db.session.add(venue)
            db.session.flush()
            db.session.refresh(venue)
            venue_id = venue.id
            db.session.commit()
            flash(f'Venue {venue_id} was successfully listed.')
            return render_template('pages/home.html')
        else:
            error = 400
            print(form.errors)
    except:
        error = 500
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    handle_error(error)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = 0
    try:
        venue = Venue.query.get(venue_id)
        if venue is not None:
            db.session.delete(venue)
            db.session.commit()
            flash(f'Venue {venue_id} was successfully deleted.')
            return render_template('pages/home.html')
        else:
            error = 404
    except:
        error = 500
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    handle_error(error, 'Venue', venue_id)

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    error = 0
    try:
        artists = []
        for name, id in Artist.query.with_entities(Artist.name, Artist.id).order_by(Artist.name).all():
            artist = {'id': id, 'name': name}
            artists.append(artist)
        return render_template('pages/artists.html', artists=artists)
    except:
        error = 500
        print(sys.exc_info())
    handle_error(error)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    error = 0
    try:
        results = {'count': 0, 'data': []}
        search_term = request.form.get('search_term', '')
        for id, name in Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.ilike(f'%{search_term}%')).all():
            num_upcoming_shows = Show.query.filter(Show.artist_id==id, Show.start_time>=datetime.now()).count()
            artist = {'id': id, 'name': name, 'num_upcoming_shows': num_upcoming_shows}
            results['data'].append(artist)
        results['count'] = len(results['data'])
        return render_template('pages/search_artists.html', results=results, search_term=search_term)
    except:
        error = 500
        print(sys.exc_info())
    handle_error(error)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    error = 0
    try:
        artist = Artist.query.get(artist_id)
        if artist is not None:
            artist_with_shows = artist.as_dict()
            past_shows, upcoming_shows = [], []
            for show in artist.venues:
                show_details = {
                    'venue_id': show.venue_id,
                    'venue_name': show.venue.name,
                    'venue_image_link': show.venue.image_link,
                    'start_time': show.start_time
                }
                if show.start_time < datetime.now():
                    past_shows.append(show_details)
                else:
                    upcoming_shows.append(show_details)
            artist_with_shows['past_shows'] = past_shows
            artist_with_shows['upcoming_shows'] = upcoming_shows
            artist_with_shows['past_shows_count'] = len(past_shows)
            artist_with_shows['upcoming_shows_count'] = len(upcoming_shows)
            return render_template('pages/show_artist.html', artist=artist_with_shows)
        else:
            error = 404
    except:
        error = 500
        print(sys.exc_info())
    handle_error(error, 'Artist', artist_id)


#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    error = 0
    try:
        artist = Artist.query.get(artist_id)
        if artist is not None:
            form = ArtistForm(obj=artist)
            return render_template('forms/edit_artist.html', form=form, artist=artist)
        else:
            error = 404
    except:
        error = 500
        print(sys.exc_info())
    handle_error(error, 'Artist', artist_id)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = 0
    try:
        artist = Artist.query.get(artist_id)
        if artist is not None:
            form = ArtistForm()
            if form.validate_on_submit():
                form.populate_obj(artist)
                db.session.commit()
                flash(f'Artist {artist_id} was successfully updated.')
                return redirect(url_for('show_artist', artist_id=artist_id))
            else:
                error = 400
                print(form.errors)
        else:
            error = 404
    except:
        error = 500
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    handle_error(error, 'Artist', artist_id)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    error = 0
    try:
        venue = Venue.query.get(venue_id)
        if venue is not None:
            form = VenueForm(obj=venue)
            return render_template('forms/edit_venue.html', form=form, venue=venue)
        else:
            error = 404
    except:
        error = 500
        print(sys.exc_info())
    handle_error(error, 'Venue', venue_id)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = 0
    try:
        venue = Venue.query.get(venue_id)
        if venue is not None:
            form = VenueForm()
            if form.validate_on_submit():
                form.populate_obj(venue)
                db.session.commit()
                flash(f'Venue {venue_id} was successfully updated.')
                return redirect(url_for('show_venue', venue_id=venue_id))
            else:
                error = 400
                print(form.errors)
        else:
            error = 404
    except:
        error = 500
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    handle_error(error, 'Venue', venue_id)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = 0
    try:
        form = ArtistForm()
        if form.validate_on_submit():
            artist = Artist()
            form.populate_obj(artist)
            db.session.add(artist)
            db.session.flush()
            db.session.refresh(artist)
            artist_id = artist.id
            db.session.commit()
            flash(f'Artist {artist_id} was successfully listed.')
            return render_template('pages/home.html')
        else:
            error = 400
            print(form.errors)
    except:
        error = 500
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    handle_error(error)


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    error = 0
    try:
        artist = Artist.query.get(artist_id)
        if artist is not None:
            db.session.delete(artist)
            db.session.commit()
            flash(f'Artist {artist_id} was successfully deleted.')
            return render_template('pages/home.html')
        else:
            error = 404
    except:
        error = 500
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    handle_error(error, 'Artist', artist_id)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    error = 0
    try:
        shows = []
        for show in Show.query.order_by(Show.start_time).all():
            venue = show.venue
            artist = show.artist
            show_details = {
                'venue_id': venue.id,
                'venue_name': venue.name,
                'artist_id': artist.id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': show.start_time.strftime('%Y-%m-%dT%H:%M')
            }
            shows.append(show_details)
        return render_template('pages/shows.html', shows=shows)
    except:
        error = 500
        print(sys.exc_info())
    handle_error(error)

    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = 0
    try:
        form = ShowForm()
        if form.validate_on_submit():
            show = Show()
            form.populate_obj(show)
            db.session.add(show)
            db.session.flush()
            db.session.refresh(show)
            show_id = show.id
            db.session.commit()
            flash(f'Show {show_id} was successfully listed.')
            return render_template('pages/home.html')
        else:
            error = 400
            print(form.errors)
    except:
        error = 500
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    handle_error(error)


@app.route('/shows/<show_id>', methods=['DELETE'])
def delete_show(show_id):
    error = 0
    try:
        show = Show.query.get(show_id)
        if show is not None:
            db.session.delete(show)
            db.session.commit()
            flash(f'Show {show_id} was successfully deleted.')
            return render_template('pages/home.html')
        else:
            error = 404
    except:
        error = 500
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    handle_error(error, 'Show', show_id)


@app.errorhandler(400)
def server_error(error):
    return render_template('errors/400.html'), 400


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


def handle_error(error, _type = '', _id = 0):
    if error == 400:
        flash('Bad request. Please try again.')
        abort (400)
    elif error == 404:
        flash(f'{_type} {_id} not found.')
        abort(404)
    elif error == 500:
        flash('Sorry, something went wrong. Please try again.')
        abort (500)


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')
