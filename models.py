#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db = SQLAlchemy()


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
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
