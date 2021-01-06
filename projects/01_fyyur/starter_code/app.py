#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from models import app, db, Venue, Artist, Show
from datetime import datetime
import json
import dateutil.parser
import babel
from flask_moment import Moment
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
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
  venues=Venue.query.all()
  data=[]
  for venue in venues:
    data[venue.state + '&' + venue.city].append({
      "id": venue.id,
      "name": venue.name
    })

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  venues = Venue.query.all()
  response={
    "count": 0,
    "data": []
  }

  response["data"].append({
    "id": venue.id,
    "name": venue.name,
    "num_upcoming_shows": num_upcoming_shows,
  })

  response["count"] = len(response["data"])

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.filter_by(id=venue_id).first_or_404()

  past_shows = db.session.query(Venue.id).join(Artist.id)
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    )

  pcoming_shows = db.session.query(Venue.id).join(Artist.id)
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    )
  
  
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": [venue.genres],
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    'past_shows': [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
        'upcoming_shows': [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }
  }


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission(): 
  form = VenueForm(request.form)
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
   
    
  try:
    venue = Venue( 
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      genres=genres,
      facebook_link=facebook_link
    ) 

    db.session.add(venue)
    db.session.commit()  
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
      

  except:
    db.session.rollback()
    error=True
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')

  finally:
    db.session.close()

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
 
  venue_id=Venue.query.get(venue_id)
  try:
    Venue.query.filter_by(venue_id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })
 


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  artists=Artist.query.all()
  for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  artists = Artist.query.all()
  response={
    "count": 0,
    "data": []
  }

  response["data"].append({
    "id": artist.id,
    "name": artist.name,
    "num_upcoming_shows": num_upcoming_shows,
  })

  response["count"] = len(response["data"])
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  artists = Artist.query.filter_by(id=artist_id).first_or_404()
  past_shows = db.session.query(Artist.id).join(Venue.id)
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    )

  pcoming_shows = db.session.query(Artist.id).join(Venue.id)
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    )

  artist = {
    "id": artist.id,
    "name": artist.name,
    "genres": [artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    'past_shows': [{
            'venue_id': venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in past_shows],
        'upcoming_shows': [{
            'venue_id': venue.id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  data={
    "id": artist.artist_id,
    "name": artist.name,
    "genres": [artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  form.name.data = artist['name']
  form.name.data = artist["genres"]
  form.city.data = artist['city']
  form.state.data = artist['state']
  form.phone.data = artist['phone']
  form.facebook_link.data = artist['facebook_link']
  form.image_link.data = artist['image_link']

  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
 
  artists = Artist.query.get(artist_id)
  artist = {
    "id": artists.id,
    "name": artists.name,
    "genres": [artists.genres],
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website": artists.website,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description": artists.seeking_description,
    "image_link": artists.image_link,
  }

  form = request.form
  try:
    artists.name = form['name']
    artists.city = form['city']
    artists.state = form['state']
    artists.phone = form['phone']
    artists.facebook_link = form['facebook_link']
    artists.genres = form['genres']
    db.session.add(artists)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except: 
    error=True
    db.session.rollback()
    flash('An error occurred. Artist ' + form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venues = Venue.query.get(venue_id)
  venue={
    "id": venues.id,
        "name": venues.name,
        "genres": [venues.genres],
        "city": venues.city,
        "state": venues.state,
        "phone": venues.phone,
        "website": venues.website,
        "facebook_link": venues.facebook_link,
        "seeking_venue": venues.seeking_venue,
        "seeking_description": venues.seeking_description,
        "image_link": venues.image_link,
  }
  form.address.data = venue["address"]
  form.name.data = venue['name']
  form.genres.data = venue["genres"]
  form.city.data = venue['city']
  form.state.data = venue['state']
  form.phone.data = venue['phone']
  form.facebook_link.data = venue['facebook_link']
  form.image_link.data = venue['image_link']
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
 
  venue = Venue.query.get(venue_id)
  try:
    form = request.form
    venue.name = form['name']
    venue.city = form['city']
    venue.state = form['state']
    venue.address = form['address']
    venue.phone = form['phone']
    venue.facebook_link = form['facebook_link']
    venue.genres = form['genres']
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error=True
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
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
  form = ArtistForm(request.form)
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  seeking_venue = request.form.get('seeking_venue')
  seeking_description =  request.form.get('seeking_description')
  image_link = request.form.get('image_link')
  past_shows=request.form.get(['past_shows'])
  upcoming_shows=request.form.get(['upcoming_shows'])
  past_shows_count=len(past_shows)
  upcoming_shows_count=len(future_shows)

  try:
    artist = Artist( 
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      genres=genres,
      facebook_link=facebook_link,
      seeking_venue=seeking_venue,
      seeking_description=seeking_description,
      image_link=image_link,
      past_shows=past_shows,
      upcoming_shows=upcoming_shows,
      past_shows_count=past_shows,
      upcoming_shows_count=future_shows
    ) 

    db.session.add(artist)
    db.session.commit()  
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
      

  except:
    db.session.rollback()
    error=True
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')

  finally:
    db.session.close()
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
 
  shows = Show.query.all()
  data=[]
  for show in shows:
     data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "start_time": show.start_time
        })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
 
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')

  try:
    show = Show(
      artist_id=artist_id,
      venue_id=venue_id,
      start_time=start_time
    )

    db.session.add(show)
    db.session.commit()  
    flash('Show was successfully listed!')
  
   
  except:
    db.session.rollback
    error=True
    flash('An error occurred. Show could not be listed.')

 
  finally:
    db.session.close()

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
