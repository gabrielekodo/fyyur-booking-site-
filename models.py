# imports
# from flask import Flask
# from flask_migrate import Migrate
# from flask_moment import Moment
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()
# app configs
# app = Flask(__name__)
# moment = Moment(app)
# app.config.from_object('config')
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)


def db_setup(app):
    app.config.from_object('config')
    
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))

    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='Artist',
                            cascade="all, delete", lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'))
    start_time = db.Column(db.DateTime(), nullable=False,
                           default=datetime.now())

    def __repr__(self):
        return '<Show {} {}>'.format(self.artist_id, self.venue_id)
