#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import re
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from flask_migrate import Migrate
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)

# Connect to local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres@localhost:5432/fyyur'

# Instantiate migration object
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Implement association table between artists and venues
show_components = db.Table('show_components', 
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key = True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key = True),
    db.Column('show_id', db.Integer, db.ForeignKey('Show.id'), primary_key = True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(500), nullable = False)
    state = db.Column(db.String(500), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), nullable = False)
    image_link = db.Column(db.String(500), default = "https://cdn10.phillymag.com/wp-content/uploads/sites/3/2018/11/live-music-concert-venue-philadelphia-1024x683.jpg")
    facebook_link = db.Column(db.String(120), nullable = False)
    genres = db.Column(db.String(120), nullable = False)
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default = True)
    seeking_description = db.Column(db.String(250))
    shows = db.relationship('Show', backref = 'Venue', lazy = True)
  
class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venues = db.Column(db.Boolean, default = True)
    shows = db.relationship('Show', backref = 'Artist', lazy=True)

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key = True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
  artist = db.relationship('Artist', backref = 'Show', lazy=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
  venue = db.relationship('Venue', backref='Show', lazy=True)
  start_time = db.Column(db.String(500), nullable = False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  data = []
  cities = []
  venues = db.session.query(Venue).all()
  shows = db.session.query(Show).all()
  for venue in venues:
    current_venue = Venue.query.get(venue.id)
    city = current_venue.city
    if city in cities:
      pass
    else:
      state = current_venue.state
      local_venues_list = []
      all_local_venues = Venue.query.filter_by(city=city).all()
      for local_venue in all_local_venues:
        local_venues_list.append(
          {
            "id": local_venue.id,
            "name": local_venue.name,
            "num_upcoming_shows": Show.query.filter_by(venue_id=local_venue.id).count()
          }
        )
      data.append(
        {
          "city": city,
          "state": state,
          "venues": local_venues_list
        }
      )
      cities.append(city)
  return render_template('pages/venues.html', areas = data)

@app.route('/venues/search', methods = ['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
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
  # Shows the venue page with the given venue_id
  data = Venue.query.get(venue_id)
  print(data)
  # Split into multiple discrete genres using a delimiter
  genres_concatenated = data.genres
  data.genres = re.split(',', genres_concatenated)
  # Append data on past and upcoming shows
  # shows = Show.query.filter_by(venue_id=venue_id).all()
  num_upcoming_shows = 0
  upcoming_shows = []
  past_shows = []
  current_time = datetime.now()
  for show in data.shows:
    show.artist_image_link = show.artist.image_link
    show.artist_name = show.artist.name
    show_datetime = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
    if show_datetime > current_time:
      num_upcoming_shows += 1
      upcoming_shows.append(show)
    elif show_datetime <= current_time:
      past_shows.append(show)
  data.past_shows = past_shows
  data.upcoming_shows = upcoming_shows
  data.upcoming_shows_count = num_upcoming_shows
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: Make sure data validates properly
  # TODO: Add responses for success and error
    # e.g., flash('An error occurred. Venue could not be created.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error = False
  body = {}
  try:
    venue_name = request.get_json()['name']
    venue_city = request.get_json()['city']
    venue_state = request.get_json()['state']
    venue_address = request.get_json()['address']
    venue_phone = request.get_json()['phone']
    venue_genres = request.get_json()['genres']
    venue_facebook_link = request.get_json()['facebook_link']
    new_venue = Venue(name = venue_name, city = venue_city, state = venue_state, address = venue_address, phone = venue_phone, genres = venue_genres, facebook_link = venue_facebook_link)
    # Add new artist record to db
    db.session.add(new_venue)
    db.session.commit()
    # Return response object
    body['name'] = venue_name
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    flash('Venue ' + venue_name + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.order_by('id').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
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
  data = []
  current_artist = Artist.query.get(artist_id)
  # Convert genres to appropriately delimited values in a list
  current_artist_genres_list = re.split(',', current_artist.genres)
  # Initialize count of shows
  num_upcoming_shows = 0
  # Split shows into those in the future versus the past
  upcoming_shows = []
  past_shows = []
  current_time = datetime.now()
  shows = Show.query.filter_by(artist_id=artist_id).all()
  for show in shows:
    show_datetime = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
    if show_datetime > current_time:
      num_upcoming_shows += 1
      upcoming_shows.append({
        "id": show.id,
        "artist_id": show.artist_id,
        "artist": show.artist,
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time
      })
    elif show_datetime <= current_time:
      past_shows.append({
        "id": show.id,
        "artist_id": show.artist_id,
        "artist": show.artist,
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time
      })
  data.append(
    {
      "id": current_artist.id,
      "name": current_artist.name,
      "genres": current_artist_genres_list,
      "city": current_artist.city,
      "state": current_artist.state,
      "phone": current_artist.phone,
      "website": current_artist.website,
      "facebook_link": current_artist.facebook_link,
      "seeking_venue": current_artist.seeking_venues,
      "image_link": current_artist.image_link,
      "upcoming_shows_count": num_upcoming_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows": past_shows
    }
  )
  # Return the first list item rather than a list of multiple artists
  data = data[0]
  return render_template('pages/show_artist.html', artist = data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # Called upon submitting the new artist listing form
  # TODO: Make sure data validates properly
  # TODO: Add responses for success and error
  error = False
  body = {}
  try:
    new_artist_name = request.get_json()['name']
    new_artist_city = request.get_json()['city']
    new_artist_state = request.get_json()['state']
    new_artist_phone = request.get_json()['phone']
    new_artist_genres = request.get_json()['genres']
    new_artist_facebook_link = request.get_json()['facebook-link']
    new_artist = Artist(name = new_artist_name, city = new_artist_city, state = new_artist_state, genres = new_artist_genres, facebook_link = new_artist_facebook_link)
    # Add new artist record to db
    db.session.add(new_artist)
    db.session.commit()
    # Return response object
    body['name'] = new_artist.name
    body['city'] = new_artist.city
    body['state'] = new_artist.state
    body['phone'] = new_artist.phone
    body['genres'] = new_artist.genres
    body['facebook_link'] = new_artist.facebook_link
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Something went wrong. Please double-check your submission and try again.')
    abort(400)
  else:
    flash('Artist ' + new_artist_name + ' was successfully listed!')
    resp = jsonify(body)
    print(resp)
    # TODO flash message should render at this point, not after one additional route is requested
    return redirect(url_for('artists'))
    # return render_template('forms/new_artist.html')


#  Shows
#  ----------------------------------------------------------------
# Displays list of shows at /shows
@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    venue = db.session.query(Venue).filter_by(id=show.venue_id).first()
    artist = db.session.query(Artist).filter_by(id=show.artist_id).first()
    data.append(
      {
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time
      }
    )
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # Renders form. Do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # Called to create new shows in the db, upon submitting new show listing form
  # TODO: Make sure data validates properly
  # TODO: Add responses for success and error
    # e.g., flash('An error occurred. Show could not be listed.')
  error = False
  body = {}
  try:
    show_artist_id = request.get_json()['artist_id']
    show_venue_id = request.get_json()['venue_id']
    show_start_time = request.get_json()['start_time']
    new_show = Show(artist_id = show_artist_id, venue_id = show_venue_id, start_time = show_start_time)
    # Add new artist record to db
    db.session.add(new_show)
    db.session.commit()
    # Return response object
    body['artist_id'] = show_artist_id
    body['venue_id'] = show_venue_id
    body['start_time'] = show_start_time
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(400)
    flash('Something went wrong. Please double-check your submission and try again.')
  else:
    flash('Show was successfully listed!')
    return render_template('pages/home.html', error=error)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

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
