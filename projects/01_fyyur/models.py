from app import app
from flask_sqlalchemy import SQLAlchemy

# Instantiate SQLAlchemy db object
db = SQLAlchemy(app)

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(500), nullable=False)
    state = db.Column(db.String(500), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), default="https://cdn10.phillymag.com/wp-content/uploads/sites/3/2018/11/live-music-concert-venue-philadelphia-1024x683.jpg")
    facebook_link = db.Column(db.String(120), nullable=False, unique=True)
    genres = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(250))
    shows = db.relationship('Show', backref='Venue', lazy=True, cascade="save-update, merge, delete")
  
class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), unique=True)
    website = db.Column(db.String(500))
    seeking_venues = db.Column(db.Boolean, default=True)
    shows = db.relationship('Show', backref ='Artist', lazy=True, cascade="save-update, merge, delete")

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  artist = db.relationship('Artist', backref='Show', lazy=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  venue = db.relationship('Venue', backref='Show', lazy=True)
  start_time = db.Column(db.String(500), nullable=False)