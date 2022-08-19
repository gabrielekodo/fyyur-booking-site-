#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db_setup, Venue, Show, Artist
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased

# import json

# import dateutil.parser
# import babel
# from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
# from flask_moment import Moment
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import func
# from flask_wtf import Form
# from forms import *
# import logging
import collections


# from logging import Formatter, FileHandler
# from flask_wtf import Form

# from models import *
from config import *
# from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config['SECRET_KEY'] = SECRET_KEY
db = db_setup(app)
# app = Flask(__name__)
# moment = Moment(app)

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
# TODO: connect to a local postgresql database


ENV = 'prod'

if ENV == 'dev':
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = DEBUG
    app.debug = True
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pcomcamhrqkpnd:77c423643c0ae216b9f338ed6b35b61569e0680c3e02726d30fe306feb0e34d3@ec2-34-193-44-192.compute-1.amazonaws.com:5432/dfki6t2esqesil'
    app.debug = False
    
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
collections.Callable = collections.abc.Callable


def format_datetime(value, format='medium'):
    # date = dateutil.parser.parse(value)
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
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

    data = []

    # get all venues
    venues = Venue.query.all()

    # setting unique venues
    unique_locations = set()

    for venue in venues:
        # add city/state tuples
        unique_locations.add((venue.city, venue.state))

    # for each unique city/state, add venues
    for location in unique_locations:
        data.append({
            "city": location[0],
            "state": location[1],
            "venues": []
        })

    for venue in venues:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(venue_id=venue.id).all()

        # get current date to filter num_upcoming_shows
        current_date = datetime.now()

        for show in shows:

            if show.start_time > current_date:
                num_upcoming_shows += 1

        for venue_location in data:
            if venue.state == venue_location['state'] and venue.city == venue_location['city']:
                venue_location['venues'].append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming_shows
                })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_string = '%'+request.form.get('search_term', '')+'%'
    venues_searched = Venue.query.filter(Venue.name.ilike(search_string)).all()

    response = {
        "count": len(venues_searched),
        "data": venues_searched
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)

    current_time = datetime.now()
# -------------------------

    past_shows_query = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()

    past_shows = []
    for show in past_shows_query:
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_image_link": Artist.query.get(show.artist_id).image_link,
            "start_time": format_datetime(str(show.start_time), format='full')
        })
    # SImilarly for the upcoming_shows

    upcoming_shows_query = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id).filter(Show. start_time > datetime.now()).all()
    upcoming_shows = []
    for show in upcoming_shows_query:
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_image_link": Artist.query.get(show.artist_id).image_link,

            "start_time": format_datetime(str(show.start_time), format='full')
        })

    print(upcoming_shows)

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
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    print(data)
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    try:

        form = VenueForm()
        if form.validate_on_submit():
            data = Venue(name=form.name.data,
                         city=form.city.data, state=form.state.data, address=form.address.data, phone=form.phone.data, genres=form.genres.data, image_link=form.image_link.data, facebook_link=form.facebook_link.data, website=form.website_link.data, seeking_talent=form.seeking_talent.data, seeking_description=form.seeking_description.data,)
            db.session.add(data)
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')

        else:
            for field, message in form.errors.items():
                flash(field + ' - ' + str(message), 'danger')

    except:
        db.session.rollback()

        flash('An error occurred. Venue ' +
              data.name + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        # Getting venue by ID
        venue = Venue.query.get(venue_id)
        venue_name = venue.name

        db.session.delete(venue)
        db.session.commit()

        flash('Venue ' + venue_name + ' was deleted')
    except:
        db.session.rollback()
        flash('an error occured and Venue ' + venue_name + ' was not deleted')
    finally:
        db.session.close()

    # return None
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_string = '%'+request.form.get('search_term', '')+'%'
    artist = Artist.query.filter(Artist.name.ilike(search_string)).all()

    response = {
        "count": len(artist),
        "data": artist
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    data = Artist.query.get(artist_id)

    current_time = datetime.now()
    past_shows_query = db.session.query(Show).join(Artist).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

    past_shows = []
    for show in past_shows_query:
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)
        past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    # SImilarly for the upcoming_shows

    upcoming_shows_query = db.session.query(Show).join(Artist).filter(
        Show.artist_id == artist_id).filter(Show. start_time > datetime.now()).all()
    upcoming_shows = []
    for show in upcoming_shows_query:
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)
        upcoming_shows.append(
            {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": format_datetime(str(show.start_time))
            }
        )

    # past_shows = []
    # upcoming_shows = []

    # shows = Show.query.filter_by(artist_id=artist_id)

    # for show in shows:
    #     artist = Artist.query.get(show.artist_id)
    #     venue = Venue.query.get(show.venue_id)

    #     if show.start_time < current_time:
    # #         past_shows.append({
    #             "venue_id": show.venue_id,
    #             "venue_name": venue.name,
    #             "venue_image_link": venue.image_link,
    #             "artist_id": show.artist_id,
    #             "artist_name": artist.name,
    #             "artist_image_link": artist.image_link,
    #             "start_time": format_datetime(str(show.start_time))
    #         })
    #     else:
    #         upcoming_shows.append({
    #             "venue_id": show.venue_id,
    #             "venue_name": venue.name,
    #             "venue_image_link": venue.image_link,
    #             "artist_id": show.artist_id,
    #             "artist_name": artist.name,
    #             "artist_image_link": artist.image_link,
    #             "start_time": format_datetime(str(show.start_time))
    #         })
    past_shows_count = len(past_shows)
    upcoming_shows_count = len(upcoming_shows)

    data.past_shows = past_shows
    data.upcoming_shows = upcoming_shows
    data.past_shows_count = past_shows_count
    data.upcoming_shows_count = upcoming_shows_count

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    artist_to_edit = Artist.query.get(artist_id)
    artist_to_edit.name = form.name.data
    artist_to_edit.city = form.city.data
    artist_to_edit.state = form.state.data
    artist_to_edit.phone = form.phone.data
    artist_to_edit.genres = form.genres.data
    artist_to_edit.image_link = form.image_link.data
    artist_to_edit.facebook_link = form.facebook_link.data
    artist_to_edit.website = form.website_link.data
    artist_to_edit.seeking_venue = form.seeking_venue.data
    artist_to_edit.seeking_description = form.seeking_description.data

    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue_to_edit = Venue.query.get(venue_id)
    venue_to_edit.name = form.name.data
    venue_to_edit.city = form.city.data
    venue_to_edit.state = form.state.data
    venue_to_edit.address = form.address.data
    venue_to_edit.phone = form.phone.data
    venue_to_edit.genres = form.genres.data
    venue_to_edit.image_link = form.image_link.data
    venue_to_edit.facebook_link = form.facebook_link.data
    venue_to_edit.website = form.website_link.data
    venue_to_edit.seeking_talent = form.seeking_talent.data
    venue_to_edit.seeking_description = form.seeking_description.data

    db.session.commit()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        form = ArtistForm()
        if form.validate_on_submit():
            data = Artist(name=form.name.data,
                          city=form.city.data, state=form.state.data,  phone=form.phone.data, genres=form.genres.data, image_link=form.image_link.data, facebook_link=form.facebook_link.data, website=form.website_link.data, seeking_venue=form.seeking_venue.data, seeking_description=form.seeking_description.data,)
            db.session.add(data)
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        else:
            for field, message in form.errors.items():
                flash(field + ' - ' + str(message), 'danger')

    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              data.name + ' could not be listed.')

    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    current_time = datetime.now()

    data = []

    shows = Show.query.all()

    for show in shows:
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)

        if show.start_time > current_time:
            data.append({
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                # "start_time": '2023-01-01 18:00:00'
                "start_time": format_datetime(str(show.start_time))
            })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()
    try:

        show_to_enlist = Show(artist_id=form.artist_id.data,
                              venue_id=form.venue_id.data, start_time=(form.start_time.data),)

        print(show_to_enlist.artist_id, show_to_enlist.venue_id,
              show_to_enlist.start_time)
        db.session.add(show_to_enlist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        db.session.rollback()
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

    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
