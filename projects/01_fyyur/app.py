#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import re
from flask import (Flask,
                  render_template,
                  request,
                  Response,
                  flash,
                  redirect,
                  url_for,
                  abort,
                  jsonify)
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

# Connect to local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres@localhost:5432/fyyur'
initial_app = app

# Import models
from models import db

# Instantiate migration object
migrate = Migrate(app, db)

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
  search_term = request.get_json()['search_term']
  matches = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  match_count = len(matches)
  match_details = []
  for match in matches:
    current_time = datetime.now()
    upcoming_shows = []
    shows = match.shows
    for show in shows:
      show_datetime = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
      if show_datetime > current_time:
        upcoming_shows.append(show)
    count_upcoming_shows = len(upcoming_shows)
    match_details.append({
      'id': match.id,
      'name': match.name,
      'num_upcoming_shows': count_upcoming_shows
    })
  response = {
    'count': match_count,
    'data': match_details
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
    # Add new venue record to db
    db.session.add(new_venue)
    db.session.commit()
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
  error = False
  body = {}
  try:
    venue_to_delete = Venue.query.get(venue_id)
    # Delete venue
    db.session.delete(venue_to_delete)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(400)
    flash('Sorry, this venue could not be deleted.')
  else:
    flash('Venue was successfully deleted.')
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.order_by('id').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.get_json()['search_term']
  matches = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  match_count = len(matches)
  match_details = []
  for match in matches:
    current_time = datetime.now()
    upcoming_shows = []
    shows = match.shows
    for show in shows:
      show_datetime = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
      if show_datetime > current_time:
        upcoming_shows.append(show)
    count_upcoming_shows = len(upcoming_shows)
    match_details.append({
      'id': match.id,
      'name': match.name,
      'num_upcoming_shows': count_upcoming_shows
    })
  response = {
    'count': match_count,
    'data': match_details
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

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  body = {}
  try:
    new_artist_name = request.get_json()['name']
    new_artist_city = request.get_json()['city']
    new_artist_state = request.get_json()['state']
    new_artist_phone = request.get_json()['phone']
    new_artist_genres = request.get_json()['genres']
    new_artist_facebook_link = request.get_json()['facebook-link']
    db.session.query(Artist).filter(Artist.id == artist_id).update(
      {
        'name': new_artist_name,
        'city': new_artist_city,
        'state': new_artist_state,
        'phone': new_artist_phone,
        'genres': new_artist_genres,
        'facebook_link': new_artist_facebook_link
      }
    )
    db.session.commit()
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
    flash('Artist ' + new_artist_name + ' was successfully updated!')
    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  body = {}
  try:
    new_venue_name = request.get_json()['name']
    new_venue_city = request.get_json()['city']
    new_venue_state = request.get_json()['state']
    new_venue_phone = request.get_json()['phone']
    new_venue_genres = request.get_json()['genres']
    new_venue_facebook_link = request.get_json()['facebook-link']
    db.session.query(Venue).filter(Venue.id == venue_id).update(
      {
        'name': new_venue_name,
        'city': new_venue_city,
        'state': new_venue_state,
        'phone': new_venue_phone,
        'genres': new_venue_genres,
        'facebook_link': new_venue_facebook_link
      }
    )
    db.session.commit()
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
    flash('Artist ' + new_venue_name + ' was successfully updated!')
    return render_template('pages/home.html')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
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
    return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False
  body = {}
  try:
    artist_to_delete = Artist.query.get(artist_id)
    # Delete artist
    db.session.delete(artist_to_delete)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(400)
    flash('Sorry, this artist could not be deleted.')
  else:
    flash('Artist was successfully deleted.')
    return render_template('pages/home.html')


#  Shows
#----------------------------------------------------------------------------#
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

#----------------------------------------------------------------------------#
# Error handlers
#----------------------------------------------------------------------------#
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
