#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, or_
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
  if result == None:
    return render_template('errors/404.html'), 404
  past_shows = []
  upcoming_shows = []

  for show in result.shows:
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
  #To correctly validate errors, had to check if there was more than one.
  #This is due to wtforms csrf validation token being missing.
  if not form.validate_on_submit():
    if len(form.errors) > 1:
      flash('Errors creating Venue')
      return render_template('forms/new_venue.html', form=form)
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
  success = False
  try:
    db.session.query(Show).filter_by(venue_id=venue_id).delete()
    db.session.query(Venue).filter_by(id=venue_id).delete()
    db.session.commit()
  except exc.IntegrityError as e:
    db.session.rollback()
    print(e.orig.args)
    flash('An error occurred. Venue could not be deleted.')
  else:
    success = True
    flash('Venue was deleted.')
  finally:
    db.session.close()

  return jsonify({ 'success': success })

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
  if result == None:
    return render_template('errors/404.html'), 404
  past_shows = []
  upcoming_shows = []

  for show in result.shows:
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
  result = Artist.query.get(artist_id)
  if result == None:
    return render_template('errors/404.html'), 404
  form = ArtistForm()
  form.name.data = result.name
  form.genres.data = result.genres
  form.city.data = result.city
  form.state.data = result.state
  form.phone.data = result.phone
  form.facebook_link.data = result.facebook_link
  form.website.data = result.website
  form.image_link.data = result.image_link
  form.seeking_venue.data = result.seeking_venue
  form.seeking_description.data = result.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=result)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  try:
    db.session.query(Artist).filter_by(id=artist_id).update({
      "name": form.name.data,
      "city": form.city.data,
      "state": form.state.data,
      "phone": form.phone.data,
      "genres": form.genres.data,
      "facebook_link": form.facebook_link.data,
      "website": form.website.data,
      "image_link": form.image_link.data,
      "seeking_venue": form.seeking_venue.data,
      "seeking_description": form.seeking_description.data
    })
    db.session.commit()
  except exc.IntegrityError as e:
    db.session.rollback()
    print(e.orig.args)
    flash('Error updating Artist!')
  else:
    flash('Artist was updated!')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  result = Venue.query.get(venue_id)
  if result == None:
    return render_template('errors/404.html'), 404
  form = VenueForm()
  form.name.data = result.name
  form.city.data = result.city
  form.state.data = result.state
  form.address.data = result.address
  form.phone.data = result.phone
  form.genres.data = result.genres
  form.facebook_link.data = result.facebook_link
  form.website.data = result.website
  form.image_link.data = result.image_link
  form.seeking_talent.data = result.seeking_talent
  form.seeking_description.data = result.seeking_description
  
  return render_template('forms/edit_venue.html', form=form, venue=result)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  try:
    db.session.query(Venue).filter_by(id=venue_id).update({
      "name": form.name.data,
      "city": form.city.data,
      "state": form.state.data,
      "address": form.address.data,
      "phone": form.phone.data,
      "genres": form.genres.data,
      "facebook_link": form.facebook_link.data,
      "website": form.website.data,
      "image_link": form.image_link.data,
      "seeking_talent": form.seeking_talent.data,
      "seeking_description": form.seeking_description.data
    })
    db.session.commit()
  except exc.IntegrityError as e:
    db.session.rollback()
    print(e.orig.args)
    flash('Error updating Venue!')
  else:
    flash('Venue was updated!')
  finally:
    db.session.close()

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
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data
    artist = Artist(name=name,city=city,state=state,phone=phone,image_link=image_link,facebook_link=facebook_link,website=website,genres=genres,seeking_venue=seeking_venue,seeking_description=seeking_description)
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

@app.route('/shows/search', methods=['POST'])
def search_shows():
  search_value = request.form.get('search_term', '')
  result = db.session.query(Show).join(Show.venue).join(Show.artist).filter(or_(Venue.name.ilike('%{0}%'.format(search_value)),Artist.name.ilike('%{0}%'.format(search_value))))
  shows = result.all()
  count = result.count()
  response = {
    "count": count,
    "data": []
  }

  for current in shows:
    response["data"].append({
      "venue_id": current.venue_id,
      "venue_name": current.venue.name,
      "artist_id": current.artist_id,
      "artist_name": current.artist.name,
      "artist_image_link": current.artist.image_link,
      "start_time": str(current.start_time)
    })

  return render_template('pages/search_shows.html', results=response, search_term=search_value)

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
