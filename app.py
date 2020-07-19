#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Artist Model
class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.Text())
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    artist_shows = db.relationship('Show', backref='artist', cascade="all, delete-orphan", passive_deletes=True, lazy='joined')

    def __repr__(self):
        return f'<Artist id: {self.id}, name: {self.name}>'

# Venue Model
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.Text())
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    venue_shows = db.relationship('Show', backref='venue', cascade="all, delete-orphan", passive_deletes=True, lazy='joined')

    def __repr__(self):
        return f'<Venue id: {self.id}, name: {self.name}>'

# Show Model
class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f'<Show id: {self.id}, Artist id: {self.artist_id}, Venue id: {self.venue_id}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

#  Home
#  ----------------------------------------------------------------


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    # Define Variables
    current_date = datetime.now()

    data = []

    # Group areas by city and state
    areas = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
       
    # Loop throw each area
    for area in areas:
        data_venues = []

        # Get venues by area
        venues = Venue.query.filter_by(city=area.city, state=area.state).all()
        
        # Loop throw each venue
        for venue in venues:
            # Get upcoming shows by venue
            upcoming_shows = Show.query.filter(Show.venue_id==venue.id, Show.start_date > current_date).all()
                    
            # Map venues
            data_venues.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(upcoming_shows)
            })

        # Map areas
        data.append({
            'city': area.city,
            'state': area.state,
            'venues': data_venues
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')
    search_result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))

    response = {
        'count': search_result.count(),
        'data': search_result,
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    # Fetch required data from database
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()

    # Define some helper variables
    finished_shows = []
    upcoming_shows = []
    current_date = datetime.now()

    # Loop throw shows to set finished_shows and upcoming_shows
    for show in shows:

        # set default image if show.artist.image_link is empty so that the image won't break
        default_image = 'https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80'

        if show.artist.image_link:
            artist_image_link = show.artist.image_link
        else:
            artist_image_link = default_image

        data = {
            'artist_id': show.artist_id,
            'venue_id': show.venue_id,
            'artist_name': show.artist.name,
            'artist_image_link': artist_image_link,
            'start_time': format_datetime(str(show.start_date))
        }

        if show.start_date > current_date:
            upcoming_shows.append(data)
        else:
            finished_shows.append(data)

    # Get all required data for venue
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": finished_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(finished_shows),
        "upcoming_shows_count": len(upcoming_shows)
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # Define Variables
    error = False
    form = VenueForm(request.form)
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_talent = form.seeking_talent.data
    seeking_description = request.form.get('seeking_description')

    try:
        # Pass Variables to Venue model
        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            genres=genres,
            image_link=image_link,
            facebook_link=facebook_link,
            website=website,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description
        )
        # Insert into Database
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('Sorry! Something went wrong, Venue: ' +
              name + ' Could not be added..', 'danger')
        abort(500)
    else:
        # on successful db insert, flash success
        flash('Venue ' + name + ' has been added successfully :)', 'success')

    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    try:
        venue = Venue.query.get(venue_id)
        venue_name = venue.name
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue_name +
            ' has been removed successfully', 'success')
    except:
        flash('Sorry! Something went wrong, Venue ' + venue_name + ' Could not be removed', 'danger')
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    data = []

    artists = Artist.query.order_by(Artist.id).all()

    for artist in artists:
        # mapping artists into data list
        data.append({
            'id': artist.id,
            'name': artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    # Define Variables
    search_term = request.form.get('search_term', '')
    search_result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))

    response = {
        'count': search_result.count(),
        'data': search_result,
    }

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    # Fetch required data from database
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id).all()

    # Define some helper variables
    finished_shows = []
    upcoming_shows = []
    current_date = datetime.now()

    # Loop throw shows to set finished_shows and upcoming_shows
    for show in shows:

        # set default image if show.venue.image_link is empty so that the image won't break
        default_image = 'https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80'

        if show.venue.image_link:
            venue_image_link = show.venue.image_link
        else:
            venue_image_link = default_image

        data = {
            'artist_id': show.artist_id,
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': venue_image_link,
            'start_time': format_datetime(str(show.start_date))
        }

        if show.start_date > current_date:
            upcoming_shows.append(data)
        else:
            finished_shows.append(data)

    # set default image if show.artist.image_link is empty so that the image won't break
    default_artist_image = 'https://cdn3.vectorstock.com/i/thumb-large/80/82/person-gray-photo-placeholder-man-vector-22808082.jpg'

    if artist.image_link:
        artist_image_link = artist.image_link
    else:
        artist_image_link = default_artist_image
    # Get all required data for venue
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist_image_link,
        "past_shows": finished_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(finished_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    form.state.data = artist.state
    form.genres.data = artist.genres
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    # Define Variables
    error = False
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    
    try:
        # updating database
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state= form.state.data
        artist.phone= form.phone.data
        artist.genres= form.genres.data
        artist.image_link= form.image_link.data
        artist.facebook_link= form.facebook_link.data
        artist.website= form.website.data
        artist.seeking_venue= form.seeking_venue.data
        artist.seeking_description= form.seeking_description.data
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('Artist could not updated', 'danger')
        abort(500)
    else:
        flash('Artist has been updated successfully !', 'success')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    form.state.data = venue.state
    form.genres.data = venue.genres
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    # Define Variables
    error = False
    form  = VenueForm()
    venue = Venue.query.get(venue_id)
    
    try:
        # updating database
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state= form.state.data
        venue.address= form.address.data
        venue.phone= form.phone.data
        venue.genres= form.genres.data
        venue.image_link= form.image_link.data
        venue.facebook_link= form.facebook_link.data
        venue.website= form.website.data
        venue.seeking_talent= form.seeking_talent.data
        venue.seeking_description= form.seeking_description.data
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('Venue could not updated', 'danger')
        abort(500)
    else:
        flash('Venue has been updated successfully !', 'success')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Artist record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # Define Variables
    error = False
    form = ArtistForm(request.form)
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_venue = form.seeking_venue.data
    seeking_description = request.form.get('seeking_description')

    try:
        # Pass Variables to Artist model
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            image_link=image_link,
            facebook_link=facebook_link,
            website=website,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )
        # Insert into Database
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('Sorry! Something went wrong, Artist ' +
              name + ' Could not be listed..', 'danger')
        abort(500)
    else:
        # on successful db insert, flash success
        flash('Artist ' + name + ' has been listed successfully :)', 'success')

    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


@app.route('/artists/<int:artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
    
    try:
        artist = Artist.query.get(artist_id)
        artist_name = artist.name
        db.session.delete(artist)
        db.session.commit()
        flash('Artist ' + artist_name +
            ' has been removed successfully', 'success')
    except:
        flash('Sorry! Something went wrong, Venue ' + artist_name + ' Could not be removed', 'danger')
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    shows = Show.query.order_by(db.desc(Show.start_date)).all()

    data = []

    for show in shows:
        # set default image if show.artist.image_link is empty so that the image won't break
        default_image = 'https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80'

        if show.artist.image_link:
            artist_image_link = show.artist.image_link
        else:
            artist_image_link = default_image

        # mapping shows into data list
        data.append({
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': artist_image_link,
            'start_time': format_datetime(str(show.start_date))
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    # Define Variables
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_date = request.form.get('start_time')

    try:
        # Pass Variables to Artist model
        show = Show(
            artist_id=artist_id,
            venue_id=venue_id,
            start_date=start_date,
        )
        # Insert into Database
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('Sorry! Something went wrong, Show could not be listed', 'danger')
        abort(500)
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!', 'success')

    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/shows/search', methods=['POST'])
def search_shows():
    # Search shows by venue or artist name

    # Define Variables
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    if len(venues) > 0:
        for venue in venues:
            search_result = Show.query.filter_by(venue_id=venue.id).all()
    else:
        artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
        if len(artists) > 0:
            for artist in artists:
                search_result = Show.query.filter_by(artist_id=artist.id).all()
        else:
            search_result = ''

    response = {
        'count': len(search_result),
        'data': search_result,
    }

    return render_template('pages/show.html', results=response, search_term=search_term)
    
#----------------------------------------------------------------------------#
# Handle Error Pages.
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

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
