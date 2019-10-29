#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
import pytz

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

import models
from models import Venue, Artist, Show

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  results = db.session.query(Venue).order_by(Venue.city, Venue.state).all()
  currentCity = ''
  areas = []
  count = -1
  for current in results:
    if current.city != currentCity:
      currentCity = current.city
      count += 1
      areas.append({
        "city": current.city,
        "state": current.state,
        "venues": []
      })
    shows = 0
    for show in current.shows:
      if show.start_time.astimezone(pytz.UTC) > datetime.now().astimezone(pytz.UTC):
        shows += 1
    areas[count]["venues"].append({
        "id": current.id,
        "name": current.name,
        "num_upcoming_shows": shows
      })
      
  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_value = request.form.get('search_term', '')
  result = db.session.query(Venue).filter(Venue.name.ilike('%{0}%'.format(search_value)))
  venues = result.all()
  count = result.count()
  response = {
    "count": count,
    "data": []
  }

  for current in venues:
    shows = 0
    for show in current.shows:
      if show.start_time.astimezone(pytz.UTC) > datetime.now().astimezone(pytz.UTC):
        shows += 1
    response["data"].append({
        "id": current.id,
        "name": current.name,
        "num_upcoming_shows": shows
      })

  return render_template('pages/search_venues.html', results=response, search_term=search_value)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  result = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()
  past_shows = []
  upcoming_shows = []

  for show in shows:
    artist = {
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    }
    if show.start_time.astimezone(pytz.UTC) > datetime.now().astimezone(pytz.UTC):
      upcoming_shows.append(artist)
    else:
      past_shows.append(artist)

  venue = {
    "id": result.id,
    "name": result.name,
    "genres": result.genres,
    "address": result.address,
    "city": result.city,
    "state": result.state,
    "phone": result.phone,
    "website": result.website,
    "facebook_link": result.facebook_link,
    "seeking_talent": result.seeking_talent,
    "seeking_description": result.seeking_description,
    "image_link": result.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

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
  form = VenueForm(request.form)
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website.data
    genres = form.genres.data
    venue = Venue(name=name,city=city,state=state,address=address,phone=phone,image_link=image_link,facebook_link=facebook_link,website=website,genres=genres)
    db.session.add(venue)
    db.session.commit()
  except exc.IntegrityError as e:
    error = True
    db.session.rollback()
    print(e.orig.args)
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  else:
    flash('Venue ' + form.name.data + ' was successfully listed!')
  
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
  artists = db.session.query(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_value = request.form.get('search_term', '')
  result = db.session.query(Artist).filter(Artist.name.ilike('%{0}%'.format(search_value)))
  artists = result.all()
  count = result.count()
  response = {
    "count": count,
    "data": []
  }

  for current in artists:
    shows = 0
    for show in current.shows:
      if show.start_time.astimezone(pytz.UTC) > datetime.now().astimezone(pytz.UTC):
        shows += 1
    response["data"].append({
        "id": current.id,
        "name": current.name,
        "num_upcoming_shows": shows
      })

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  result = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()
  past_shows = []
  upcoming_shows = []

  for show in shows:
    venue = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    }
    if show.start_time.astimezone(pytz.UTC) > datetime.now().astimezone(pytz.UTC):
      upcoming_shows.append(venue)
    else:
      past_shows.append(venue)

  artist = {
    "id": result.id,
    "name": result.name,
    "genres": result.genres,
    "city": result.city,
    "state": result.state,
    "phone": result.phone,
    "website": result.website,
    "facebook_link": result.facebook_link,
    "seeking_venue": result.seeking_venue,
    "seeking_description": result.seeking_description,
    "image_link": result.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=artist)

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
  error = False
  form = ArtistForm(request.form)
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website.data
    genres = form.genres.data
    artist = Artist(name=name,city=city,state=state,phone=phone,image_link=image_link,facebook_link=facebook_link,website=website,genres=genres)
    db.session.add(artist)
    db.session.commit()
  except exc.IntegrityError as e:
    error = True
    db.session.rollback()
    print(e.orig.args)
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  else:
    flash('Artist ' + form.name.data + ' was successfully listed!')
  
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  result = db.session.query(Show).all()
  shows = []
  for item in result:
    shows.append({
      "venue_id": item.venue_id,
      "venue_name": item.venue.name,
      "artist_id": item.artist_id,
      "artist_name": item.artist.name,
      "artist_image_link": item.artist.image_link,
      "start_time": str(item.start_time)
    })
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  form = ShowForm(request.form)
  try:
    venue_id = form.venue_id.data
    artist_id = form.artist_id.data
    start_time = form.start_time.data
    show = Show(venue_id=venue_id,artist_id=artist_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except exc.IntegrityError as e:
    error = True
    db.session.rollback()
    print(e.orig.args)
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

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
