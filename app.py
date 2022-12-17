#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
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


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False, primary_key=True)
    start_time = db.Column(db.DateTime)

    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time

    def format(self):
        return {
            "venue_id": self.venue_id,
            "artist_id": self.artist_id,
            "start_time": self.start_time
        }


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(255))
    image_link = db.Column(db.String(500))
    artists = db.relationship('Show', backref=db.backref('venue', lazy=True))

    def __init__(self, name, genres, address, city, state, phone, website, facebook_link, seeking_talent, seeking_description, image_link):
        self.name = name
        self.genres = genres
        self.address = address
        self.city = city
        self.state = state
        self.phone = phone
        self.website = website
        self.facebook_link = facebook_link
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description
        self.image_link = image_link

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
        }


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(255))
    image_link = db.Column(db.String(500))

    def __init__(self, name, genres, city, state, phone, website, facebook_link, seeking_venue, seeking_description, image_link):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.website = website
        self.facebook_link = facebook_link
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description
        self.image_link = image_link

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link
        }
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
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
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venues_list = Venue.query.all()
    areas = []
    venues = []
    # write num_upcoming_shows function
    # sort venue data like below, don't need all fields

    for venue in venues_list:
        print(venue)
        venue_data = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 1,
        }
        area_data = {
            "city": venue.city,
            "state": venue.state,
            "venues": []
        }
        if not areas:
            areas.append(area_data)
        else:
            for area in areas:
                city = area['city']
                if venue.city == city:
                    print(city)
                    area['venues'].append(venue_data)
                else:
                    # venues.append(venue_data)
                    areas.append(area_data)
                    # area['venues'].append(venue_data)
    print(areas)

    data = [{
        "city": "San Francisco",
        "state": "CA",
        "venues": [{
            "id": 1,
            "name": "The Musical Hop",
            "num_upcoming_shows": 0,
        }, {
            "id": 3,
            "name": "Park Square Live Music & Coffee",
            "num_upcoming_shows": 1,
        }]
    }, {
        "city": "New York",
        "state": "NY",
        "venues": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }]
    return render_template('pages/venues.html', areas=areas)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)

    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = VenueForm()
    try:
        name = form.name.data
        venue = Venue(
            name=name, genres=form.genres.data, address=form.address.data, city=form.city.data,
            state=form.state.data, phone=form.phone.data, website=form.website_link.data,
            facebook_link=form.facebook_link.data, seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data, image_link=form.image_link.data
        )
        db.session.add(venue)
        db.session.commit()
        if form.is_submitted():
            flash('Venue ' + name + ' was successfully listed!')
            return redirect('/venues')
        else:
            flash('An error occurred. Venue ' + name + ' could not be listed.')
            return render_template('pages/home.html')
    except ():
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists_query = Artist.query.all()
    return render_template('pages/artists.html', artists=artists_query)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    artist = Artist.query.get(artist_id)
    form = ArtistForm(request.form, obj=artist)
    try:
        name = form.name.data
        form.populate_obj(artist)
        db.session.commit()
        if form.is_submitted():
            flash('Artist ' + name + ' was successfully updated!')
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            flash('An error occurred. Artist ' +
                  name + ' could not be updated.')
            return redirect(url_for('show_artist', artist_id=artist_id))
    except ():
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Artist ' + request.form['name'] + ' was successfully updated!')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form, obj=venue)
    try:
        name = form.name.data
        form.populate_obj(venue)
        db.session.commit()
        if form.is_submitted():
            flash('Venue ' + name + ' was successfully updated!')
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            flash('An error occurred. Venue ' +
                  name + ' could not be updated.')
            return redirect(url_for('show_venue', venue_id=venue_id))
    except ():
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully updated!')

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    form = ArtistForm()
    try:
        name = form.name.data
        artist = Artist(
            name=name, genres=form.genres.data, city=form.city.data,
            state=form.state.data, phone=form.phone.data, website=form.website_link.data,
            facebook_link=form.facebook_link.data, seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data, image_link=form.image_link.data
        )
        db.session.add(artist)
        db.session.commit()
        if form.is_submitted():
            flash('Artist ' + name + ' was successfully listed!')
            return redirect('/artists')
        else:
            flash('An error occurred. Artist ' +
                  name + ' could not be listed.')
            return render_template('pages/home.html')
    except ():
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows_query = Show.query.all()
    shows = []
    for show in shows_query:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        format = "%b %d %Y %r"
        start_time = show.start_time.strftime(format)
        show_data = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": start_time
        }
        shows.append(show_data)

    return render_template('pages/shows.html', shows=shows)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    form = ShowForm()
    try:
        show = Show(venue_id=form.venue_id.data,
                    artist_id=form.artist_id.data, start_time=form.start_time.data)
        db.session.add(show)
        db.session.commit()
        if form.is_submitted():
            flash('Show was successfully listed!')
            return redirect('/shows')
        else:
            flash('An error occurred. Show could not be listed.')
            return render_template('pages/home.html')
    except ():
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Show was successfully listed!')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
