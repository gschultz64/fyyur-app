#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
import dateutil.parser
import datetime
import babel
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    abort
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
import models
from models import db, Show, Artist, Venue


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.getenv("APP_SETTINGS", "config.Config"))
    db.init_app(app)
    migrate.init_app(app, db)

    return app


app = create_app()
moment = Moment(app)


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


# datetime formatting article: https://www.programiz.com/python-programming/datetime/strftime

def format_date_string(value):
    format = "%b %d %Y %r"
    start_time = value.strftime(format)
    return start_time


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues_list = Venue.query.all()
    areas = {}

    for venue in venues_list:
        venue_data = {
            "id": venue.id,
            "name": venue.name,
        }

        if venue.city in areas:
            existing_area = areas[venue.city]
            existing_area["venues"].append(venue_data)
        else:
            area_data = {
                "city": venue.city,
                "state": venue.state,
                "venues": [venue_data]
            }
            areas.update({venue.city: area_data})

    return render_template('pages/venues.html', areas=areas.values())


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    matching = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
    count = len(matching)
    response = {
        "count": count,
        "data": matching
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        past_shows_query = db.session.query(Show).join(Venue).filter(
            Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
        upcoming_shows_query = db.session.query(Show).join(Venue).filter(
            Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

        venue.past_shows = past_shows_query
        venue.upcoming_shows = upcoming_shows_query

        for show in venue.past_shows:
            artist = Artist.query.get(show.artist_id)
            show.artist_name = artist.name
            show.artist_image_link = artist.image_link
            show.start_time = format_date_string(show.start_time)

        for show in venue.upcoming_shows:
            artist = Artist.query.get(show.artist_id)
            show.artist_name = artist.name
            show.artist_image_link = artist.image_link
            show.start_time = format_date_string(show.start_time)

        return render_template('pages/show_venue.html', venue=venue)
    except:
        error = True
    if error:
        abort(404)


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
    name = form.name.data
    try:
        if name is not None:
            venue = Venue(
                name=name, genres=form.genres.data, address=form.address.data, city=form.city.data,
                state=form.state.data, phone=form.phone.data, website=form.website_link.data,
                facebook_link=form.facebook_link.data, seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data, image_link=form.image_link.data
            )
            db.session.add(venue)
            db.session.commit()
            if form.is_submitted():
                flash('Your venue ' + name + ' was successfully listed!')
                return redirect('/venues')
            else:
                flash('An error occurred. Venue ' + name + ' could not be listed.')
                return render_template('pages/home.html')
        else:
            flash('An error occurred. Form data is missing from the request.')
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Your venue ' +
              request.form['name'] + ' was successfully listed!')


@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        Show.query.filter(Show.venue_id == venue_id).delete()
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Your venue was deleted!')
        return redirect('/')


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists_query = Artist.query.all()
    return render_template('pages/artists.html', artists=artists_query)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    matching = Artist.query.filter(
        Artist.name.ilike('%'+search_term+'%')).all()
    count = len(matching)
    response = {
        "count": count,
        "data": matching
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    error = False
    try:
        artist = Artist.query.get(artist_id)
        past_shows_query = db.session.query(Show).join(Artist).filter(
            Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
        upcoming_shows_query = db.session.query(Show).join(Artist).filter(
            Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

        artist.past_shows_count = len(past_shows_query)
        artist.upcoming_shows_count = len(upcoming_shows_query)
        artist.past_shows = past_shows_query
        artist.upcoming_shows = upcoming_shows_query

        for show in artist.past_shows:
            venue = Venue.query.get(show.venue_id)
            show.venue_name = venue.name
            show.venue_image_link = venue.image_link
            show.start_time = format_date_string(show.start_time)

        for show in artist.upcoming_shows:
            venue = Venue.query.get(show.venue_id)
            show.venue_name = venue.name
            show.venue_image_link = venue.image_link
            show.start_time = format_date_string(show.start_time)

        return render_template('pages/show_artist.html', artist=artist)
    except:
        error = True
    if error:
        abort(404)

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
            flash('Your artist ' + name + ' was successfully updated!')
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            flash('An error occurred. Artist ' +
                  name + ' could not be updated.')
            return redirect(url_for('show_artist', artist_id=artist_id))
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Your artist ' +
              request.form['name'] + ' was successfully updated!')


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
            flash('Your venue ' + name + ' was successfully updated!')
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            flash('An error occurred. Venue ' +
                  name + ' could not be updated.')
            return redirect(url_for('show_venue', venue_id=venue_id))
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Your venue ' +
              request.form['name'] + ' was successfully updated!')

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
    name = form.name.data
    try:
        if name is not None:
            artist = Artist(
                name=name, genres=form.genres.data, city=form.city.data,
                state=form.state.data, phone=form.phone.data, website=form.website_link.data,
                facebook_link=form.facebook_link.data, seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data, image_link=form.image_link.data
            )
            db.session.add(artist)
            db.session.commit()
            if form.is_submitted():
                flash('Your artist ' + name + ' was successfully listed!')
                return redirect('/artists')
            else:
                flash('An error occurred. Artist ' +
                    name + ' could not be listed.')
                return render_template('pages/home.html')
        else:
            flash('An error occurred. Form data is missing from the request.')
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Your artist ' +
              request.form['name'] + ' was successfully listed!')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows_query = Show.query.all()
    shows = []
    for show in shows_query:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        show_data = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": format_date_string(show.start_time)
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
        if (form.venue_id.data is None) or (form.artist_id.data is None):
            error = True
            flash('An error occurred. Form data is missing from the request.')
        else:
            show = Show(venue_id=form.venue_id.data,
                        artist_id=form.artist_id.data, start_time=form.start_time.data)
            db.session.add(show)
            db.session.commit()
            if form.is_submitted():
                flash('Your show was successfully listed!')
                return redirect('/shows')
            else:
                flash('An error occurred. Show could not be listed.')
                return render_template('pages/home.html')
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Your show was successfully listed!')


@app.errorhandler(400)
def not_found_error(error):
    return render_template('errors/400.html'), 400


@app.errorhandler(401)
def not_found_error(error):
    return render_template('errors/401.html'), 401


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(405)
def not_found_error(error):
    return render_template('errors/500.html'), 405


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
