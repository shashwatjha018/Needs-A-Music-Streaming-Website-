from datetime import datetime
from music_app import app, db, login_manager
from flask_login import UserMixin
#from flask_whooshalchemy import wa

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



listened = db.Table("Listened", 
        db.Column("song_id", db.Integer, db.ForeignKey("song.id")),
        db.Column("user_id", db.Integer, db.ForeignKey("user.id"))) 

subscribed = db.Table('subscribed',
            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
            db.Column('podcast_id', db.Integer, db.ForeignKey('podcast.id'))
)

performance = db.Table('performance',
            db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
            db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'))
)

held_in = db.Table('held_in',
            db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
            db.Column('place_id', db.Integer, db.ForeignKey('place.id'))
)



class User(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), nullable=True)
    lname = db.Column(db.String(75), nullable=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    image_file = db.Column(db.String(32), nullable=True, default='default.jpg')
    preflang = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(60), nullable=False)
    #searches = db.relationship('user_search_history', backref=db.backref('user'))
    #playlists = db.relationship('user_song_playlist', backref=db.backref('user'))
    #songs = db.relationship('Song', secondary=listened)
    posts = db.relationship('Post', backref='author', lazy=True)
    podcasts = db.relationship('Podcast', secondary=subscribed, backref = 'pod_art', lazy = True)
    listen = db.relationship('Song', secondary= listened, backref=db.backref('listener', 
                            lazy=True))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=True)
    #playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.name}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Song(db.Model, UserMixin):
    #__searchable__ = ['name', 'genre']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), nullable=False)
    album = db.Column(db.String(75), nullable=False)
    genre = db.Column(db.String(75), nullable=True)
    release_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    rating = db.Column(db.Integer, default=2)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    song_file = db.Column(db.String(200), nullable=False)
    image_file = db.Column(db.String(32), nullable=True, default='default.jpg')
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    contains = db.relationship('Contains', backref = 'contains', uselist = False)
#wa.whoosh_index(app, Song)
def __repr__(self):
        return f"Song('{self.name}')"

class Artist(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), nullable=False)
    email = db.Column(db.String(128), unique=True)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    rating = db.Column(db.Integer, default=2)
    song = db.relationship('Song', backref = 'singer', lazy = True)
    user = db.relationship('User', backref='user_art', uselist = False)
    podcast = db.relationship('Podcast', backref='podcast', lazy = True, uselist = False)
    label_id = db.Column(db.Integer, db.ForeignKey('label.id'))

   
def __repr__(self):
        return f"Aritst('{self.name}')"


class Podcast(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    title = db.Column(db.String(75), nullable=False)
    description = db.Column(db.String, default='No description')
    category = db.Column(db.String, nullable=False)
    release_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    pod_file = db.Column(db.String(200), nullable=False)
    image_file = db.Column(db.String(32), nullable=True, default='default.jpg')
    rating = db.Column(db.Integer, default=2)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))

def __repr__(self):
    return f"Podcast('{self.name}', '{self.category}', '{self.release_date}''{self.rating}')"

class Playlist(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True, default = "Your Playlist")
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    rating = db.Column(db.Integer, default=2)
    #user = db.relationship('User', backref = 'user', uselist = False)
    contains = db.relationship('Contains', backref = 'playlist', lazy = 'dynamic',
                                cascade = "all, delete, delete-orphan")
    user = db.relationship('User', backref='user_playlist', uselist = False)

    def __repr__(self):
        return f"Playlist('{self.id}', '{self.rating}')"

class Contains(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'))
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(75), nullable=False)
    mname = db.Column(db.String(75), nullable=True)
    lname = db.Column(db.String(75), nullable=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    

    def __repr__(self):
        return f"Admin('{self.fname}', '{self.lname}')"

class Label(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), nullable=False)
    types = db.Column(db.String(75), nullable=True)
    insi = db.Column(db.String(75), nullable=True, unique = True)
    artist = db.relationship('Artist', backref='artist', lazy = True)
   
    def __repr__(self):
        return f"Label('{self.name}', '{self.insi}')"

class Review(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    date_posted = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    suggestions = db.Column(db.Text, nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key = True)
    #__table_args__ = (
        #PrimaryKeyConstraint('field2', 'field1'),
        #{},
    #)
    def __repr__(self):
        return f"Label('{self.title})"

class Event(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    time = db.Column(db.Integer, nullable=True, default=datetime.utcnow)
    event = db.relationship('EventStatus', backref='events', uselist = False)
    review = db.relationship('Review', backref='review', lazy = "dynamic")
    art_perform = db.relationship('Artist', secondary=performance, backref = 'perform', lazy = "dynamic")
    place = db.relationship('Place', secondary=held_in, backref = 'places', lazy = "dynamic")
    def __repr__(self):
        return f"Event('{self.name})"

class EventStatus(db.Model, UserMixin):
    time = db.Column(db.Integer, db.ForeignKey('event.time'))
    begin_date = db.Column(db.String(100), primary_key = True)
    end_date = db.Column(db.String(100), primary_key = True)
    status = db.Column(db.String(100), nullable=True)
    def __repr__(self):
        return f"EventStatus('{self.status})"

class Place(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75), nullable=False)
    address = db.Column(db.String(75), nullable=True)
    pincode = db.Column(db.Integer, nullable=True, unique = True)
    place = db.relationship('City', backref='places', lazy ="dynamic")
   
    def __repr__(self):
        return f"Place('{self.name}', '{self.pincode}')"

class City(db.Model, UserMixin):
    pincode = db.Column(db.Integer, db.ForeignKey('place.pincode'), primary_key=True)
    name = db.Column(db.String(75), nullable=False)
    state = db.Column(db.String(75), nullable=True)
   
    def __repr__(self):
        return f"City('{self.name}', '{self.state}')"


class user_search_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    searchno = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))






