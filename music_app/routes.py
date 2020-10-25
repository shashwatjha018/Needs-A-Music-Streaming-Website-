from flask import render_template, request, flash, redirect, url_for, abort
#from music_app.form import RegistrationForm, LoginForm, ArtistForm, UpdateAccountForm, PostForm, SongForm, UploadPodcastForm
from music_app.form import *
from music_app.models import *
from music_app import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image


@app.route('/')
def landing_page():
    return render_template("landing_page.html")

@app.route('/home')
@login_required
def home():
    search = request.args.get('search')
    if search:
        artist = Artist.query.filter_by(name = search).first()
        if artist:
            songs = Song.query.filter(Song.artist_id.contains(artist.id))
            return render_template("home.html", songs = songs)
        else:
            songs = Song.query.filter(Song.name.contains(search)|Song.genre.contains(search))
            return render_template("home.html", songs = songs)
    else:
        user = User.query.filter_by(id =current_user.id).first_or_404(description = "No such user")
        song = Song.query.all()
        my_playlist = Playlist.query.get(user.playlist_id)
        songs = Song.query.all()
    return render_template("home.html", songs = songs, user = user, my_playlist = my_playlist)

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name = form.fn.data, lname = form.ln.data,username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        if form.check_artist.data == True:
            return redirect(url_for('artist_registration'))
        else:
            flash(f'Account created for {form.username.data}! You can now login', 'success')
            return redirect(url_for('login'))
    return render_template("register.html", title='Registration', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'You have been logged in successfully {form.email.data}!', 'success')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Incorrect username or password', 'danger')
    return render_template("login.html", title = 'Login', form=form )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('landing_page'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8) #a random txt is generated from secrets module so that no two file has the same name
    _, f_ext = os.path.splitext(form_picture.filename)# (os mod)os.path.splitext splits the filename into two parts: filename and extention so that extention do not get lost
    picture_fn = random_hex + f_ext #joins the random txt and the ext to make the new file name
    picture_path = os.path.join(app.root_path, 'static/profile_pic', picture_fn) #(os mod) to save the path extention start from home directory
    output_size = (125, 125) #(pil mod) to resize the image
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    #form_picture.save(picture_path)
    
    return picture_fn

@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()  #instantizing update account form
    if form.picture.data and form.validate_on_submit():       #checking if there is picture to be uploaded 
        picture_file = save_picture(form.picture.data)  #calls the save_picture fn so go to that fn and the image uploaded is passed into the fn
        current_user.image_file = picture_file
        
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        if form.check_artist.data == True:
            return redirect(url_for('artist_registration'))
        else:
            flash('Your Account has been updated!', 'success')
            return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    
    image_file = url_for('static', filename ='profile_pic/'+current_user.image_file)
    return render_template('account.html', title='Account', 
                            image_file = image_file, form = form)

@app.route('/artist_registration', methods=["GET", "POST"])
def artist_registration():
    form = Artist_Label_Form()
    if form.validate_on_submit():
        artist = Artist(name = form.name.data, email = form.email.data)
        label = Label(name = form.label_name.data, types = form.type.data, insi = form.insi.data)
        current_user.user_art = artist
        db.session.add(artist)
        db.session.add(label)
        db.session.commit()
        artist.label_id = label.id
        db.session.commit()
        current_user.artist_id = artist.id
        db.session.commit()
        flash(f'Account created for {form.name.data}! You can now login', 'success')
        return redirect(url_for('login'))
    return render_template("artist_registration.html", title='Artist Registration', form=form)


@app.route('/post')
@login_required
def post_landing():
    search = request.args.get('search')
    if search:
        user = User.query.filter_by(username = search).first()
        if user:
            posts = Post.query.filter(Post.user_id.contains(user.id))
            return render_template("post_landing.html",  posts = posts)
        else:
            posts = Post.query.filter(Post.title.contains(search)|
                                    Post.content.contains(search))
            return render_template("post_landing.html",  posts = posts)
    else:
        posts = Post.query.all()
    return render_template("post_landing.html", posts = posts)


@app.route('/post/new', methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('post_landing'))
    return render_template('create_post.html', title = 'New Post', form = form, legend = 'New Post')
    
@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template("post.html", title='post.title', post = post)

@app.route('/post/<int:post_id>/update', methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    print(post.author)
    print(current_user)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title = 'Update Post', form = form, legend = 'Update Post')

@app.route('/post/<int:post_id>/delete', methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))



def save_cover(form_picture):
    random_hex = secrets.token_hex(8) #a random txt is generated from secrets module so that no two file has the same name
    _, f_ext = os.path.splitext(form_picture.filename)# (os mod)os.path.splitext splits the filename into two parts: filename and extention so that extention do not get lost
    picture_fn = random_hex + f_ext #joins the random txt and the ext to make the new file name
    picture_path = os.path.join(app.root_path, 'static/covers', picture_fn) #(os mod) to save the path extention start from home directory
    output_size = (125, 125) #(pil mod) to resize the image
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    #form_picture.save(picture_path)
    return picture_fn
    


def save_song(form_song):
    random_hex = secrets.token_hex(8) 
    _, f_ext = os.path.splitext(form_song.filename)
    song_fn = random_hex + f_ext 
    song_path = os.path.join(app.root_path, 'static/song_dir', song_fn) 
    
    form_song.save(song_path)
    return song_fn


@app.route('/song/new', methods=["GET", "POST"])
@login_required
def new_song():
    form = SongForm()
    if form.song_file.data and form.validate_on_submit():     
        song_file1 = save_song(form.song_file.data)  
        #current_user.song_file = song_file
        artist = form.singer.data
        artist = Artist.query.filter_by(name=artist).first()
        if artist:
            artist_id = artist.id
            print(artist_id)
            song = Song(name = form.name.data, genre=form.genre.data, album = form.album.data, song_file = song_file1, artist_id = artist.id)
            if form.picture.data:
                picture_file = save_cover(form.picture.data)
                print(picture_file) 
                song.image_file = picture_file
            print(song.image_file)
            db.session.add(song)
            db.session.commit()
            statement = listened.insert().values(user_id=current_user.id, song_id = song.id)
            db.session.execute(statement)
            db.session.commit()
            song.image_file = url_for('static', filename ='covers/'+ song.image_file)
            flash('Your song has been uploaded', 'success')
            return redirect(url_for('home'))
        else:
            flash('Entered artist does not exist', 'danger')
            return redirect(url_for('new_song'))
    return render_template('create_song.html', title = 'New Song', form = form, legend = 'New Song')

@app.route('/song/<int:song_id>')
def song(song_id):
    song = Song.query.get_or_404(song_id)
    return render_template("song.html", title=song.name, song = song)

@app.route('/song/<int:song_id>/update', methods=["GET", "POST"])
@login_required
def update_song(song_id):
    song = Song.query.get_or_404(song_id)

    #print(song.singer)
    #print(current_user)
    if song.singer != current_user:
        abort(403)
    form = SongForm()
    if form.validate_on_submit():
        song.name = form.name.data
        song.genre = form.genre.data
        song_file1 = save_song(form.song_file.data)
        song.song_file = song_file1
        #song.image_file = form.picture.data
        if form.picture.data:
            picture_file = save_cover(form.picture.data)
            print(picture_file) 
            song.image_file = picture_file
        #song.image_file = url_for('static', filename ='covers/'+ song.image_file)
        db.session.commit()
        song.image_file = url_for('static', filename ='covers/'+ song.image_file)
        flash('Your song has been updated!', 'success')
        return redirect(url_for('song', song_id = song.id))
    elif request.method == 'GET':
        form.name.data = song.name
        form.genre.data = song.genre
        form.album.data = song.album
        form.singer.data = song.singer.name
        form.song_file.data = song.song_file
        form.picture.data = song.image_file
    return render_template('create_song.html', title = 'Update Song', form = form, legend = 'Update Song')


@app.route('/song/<int:song_id>/delete', methods=["GET", "POST"])
@login_required
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    if song.singer != current_user:
        abort(403)
    db.session.delete(song)
    db.session.commit()
    flash('Your song has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route('/podcast')
@login_required
def pod_landing():
    search = request.args.get('search')
    if search:
        artist = Artist.query.filter_by(name = search).first()
        if artist:
            podcasts = Podcast.query.filter(Podcast.artist_id.contains(artist.id))
            return render_template("pod_landing.html", podcasts = podcasts)
        else:
            podcasts = Podcast.query.filter(Podcast.name.contains(search)|Podcast.title.contains(search)
            |Podcast.category.contains(search)|Podcast.description.contains(search))
            return render_template("pod_landing.html", podcasts = podcasts)
    else:
        podcasts = Podcast.query.all()
    return render_template("pod_landing.html", podcasts = podcasts, title='podcasts.title')


@app.route('/podcast/new', methods=["GET", "POST"])
@login_required
def new_podcast():
    form = UploadPodcastForm()
    if form.pod_file.data and form.validate_on_submit():
        print('form.pod_file.name')     
        podcast_file1 = save_song(form.pod_file.data)  
        #current_user.song_file = song_file
        artist = form.artist.data
        artist = Artist.query.filter_by(name=artist).first()
        if artist:
            artist_id = artist.id
            print(artist_id)
            podcast = Podcast(title = form.title.data, description = form.description.data, 
                            name = form.name.data, category=form.category.data, pod_file = podcast_file1, artist_id = artist.id)
            if form.picture.data:
                picture_file = save_cover(form.picture.data)
                print(picture_file) 
                podcast.image_file = picture_file
            print(podcast.image_file)
            db.session.add(podcast)
            db.session.commit()
            statement = subscribed.insert().values(user_id=current_user.id, podcast_id = podcast.id)
            db.session.execute(statement)
            db.session.commit()
            podcast.image_file = url_for('static', filename ='covers/'+ podcast.image_file)
            flash('Your podcast has been uploaded', 'success')
            return redirect(url_for('pod_landing'))
        else:
            flash('Entered artist does not exist', 'danger')
            return redirect(url_for('new_podcast'))
    return render_template('create_podcast.html', title = 'New Podcast', form = form, legend = 'New Podcast')

@app.route('/podcast/<int:podcast_id>')
def podcast(podcast_id):
    podcast = Podcast.query.get_or_404(podcast_id)
    return render_template("podcast.html", title='podcast.title', podcast = podcast)

@app.route('/podcast/<int:podcast_id>/update', methods=["GET", "POST"])
@login_required
def update_podcast(podcast_id):
    podcast = Podcast.query.get_or_404(podcast_id)
    if podcast.podcast != current_user:
        abort(403)
    form = UploadPodcastForm()
    if form.validate_on_submit():
        artist = form.artist.data
        artist = Artist.query.filter_by(name=artist).first()
        if artist:
            podcast.artist_id = artist.id
            podcast.name = form.name.data
            podcast.title = form.title.data
            podcast.description = form.description.data
            podcast.category = form.category.data
            podcast_file1 = save_song(form.pod_file.data)
            podcast.pod_file = podcast_file1
            if form.picture.data:
                picture_file = save_cover(form.picture.data)
                print(picture_file) 
                podcast.image_file = picture_file
            db.session.commit()
            podcast.image_file = url_for('static', filename ='covers/'+ podcast.image_file)
            flash('Your podcast has been updated!', 'success')
            return redirect(url_for('podcast', podcast_id = podcast.id))
    elif request.method == 'GET':
        form.name.data = podcast.name
        form.title.data = podcast.title
        form.description.data = podcast.description
        form.category.data = podcast.category
        form.artist.data = podcast.podcast.name
        form.pod_file.data = podcast.pod_file
        form.picture.data = podcast.image_file
    return render_template('create_podcast.html', title = 'Update Podcast', form = form, legend = 'Update Podcast')

@app.route('/podcast/<int:podcast_id>/delete', methods=["GET", "POST"])
@login_required
def delete_podcast(podcast_id):
    podcast = Podcast.query.get_or_404(podcast_id)
    if podcast.podcast != current_user:
        abort(403)
    db.session.delete(podcast)
    db.session.commit()
    flash('Your podcast has been deleted!', 'success')
    return redirect(url_for('pod_landing'))

@app.route('/home/playlist/<int:user_id>', methods=["GET", "POST"])
@login_required
def playlist(user_id):
    form = PlaylistName()
    #print(current_user.id)
    user = User.query.filter_by(id =current_user.id).first_or_404(description = "No such user found")
    #print(user)
    if user.playlist_id == None:
        print('not working')
        if form.validate_on_submit():
            print('working')
            playlist = Playlist(name = form.name.data)
            db.session.add(playlist)
            try:
                db.session.commit()
            except:
                db.session.rollback()
            current_user.playlist_id = playlist.id
            db.session.commit()
            flash("Playlist name set successfully", 'success')
            return redirect('/home')
    else:
        songs = Song.query.all()
        artists = Artist.query.all()
        my_playlist = Playlist.query.get(user.playlist_id)
        print(my_playlist)

        contains = Contains.query.filter_by(playlist_id = my_playlist.id)
        return render_template('playlist.html', form = form, user = user, my_playlist = my_playlist, contains = contains, artists = artists)
    return render_template('playlist.html', form = form, user = user)

def exists(contains, playlist):
    for i in playlist:
        if i.song_id == contains.song_id:
            return True
    return False

@app.route('/add_song/<int:user_id>/<int:song_id>/<int:playlist_id>')
def add_song(user_id, song_id, playlist_id):
    new_contain = Contains(song_id = song_id, playlist_id = playlist_id )
    user = User.query.filter_by(id = current_user.id).first_or_404(description = "No such user found")
    my_playlist = Playlist.query.filter_by(id = user.playlist_id).first()
    if not exists(new_contain, my_playlist.contains):
        song = Song.query.get(song_id)
        db.session.add(new_contain)
        try:
            db.session.commit()
        except:
            db.session.rollback()
    return redirect(url_for('playlist', user_id = current_user.id))


@app.route('/add_song/<int:user_id>/<int:contains_id>')
def remove_song(user_id, contains_id):
    remove_contain = Contains.query.get(contains_id)
    db.session.delete(remove_contain)
    try:
        db.session.commit()
    except:
        db.session.rollback() 
    return redirect(url_for('playlist', user_id = current_user.id))

@app.route('/home/playlist')
def global_playlist():
    playlists = Playlist.query.all()
    contains = Contains.query.all()
    users = User.query.all()
    artists =Artist.query.all()
    return render_template("global_playlist.html", title = 'Playlists', playlists = playlists, contains = contains, users = users,  artists=artists) 

@app.route('/event/new', methods=["GET", "POST"])
@login_required
def new_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(name = form.name.data, time=form.time.data)
        event_status = EventStatus(time = form.time.data, begin_date=form.begin_date.data, end_date=form.end_date.data, status = form.status.data)
        place = Place(name = form.place_name.data, address = form.address.data, pincode = form.pincode.data)
        city = City(name = form.city_name.data, pincode = form.pincode.data, state = form.state.data)
        db.session.add(event)
        db.session.add(event_status)
        db.session.add(place)
        db.session.add(city)
        db.session.commit()
        flash('Your event has been created', 'success')
        return redirect(url_for('event_landing'))
    return render_template("event.html", form = form)

@app.route('/event')
@login_required
def event_landing():
    search = request.args.get('search')
    if search:
        events = Event.query.filter(Event.name.contains(search)|
                                    Event.time.contains(search))
        places = Place.query.filter(Place.name.contains(search)|
                                    Place.pincode.contains(search))
        return render_template("event_landing.html",  events = events, places = places)
    else:
        events = Event.query.all()
        places = Place.query.all()
        cities= City.query.all()
        event_status = EventStatus.query.all()
    return render_template("event_landing.html", events = events, places = places, cities = cities, event_status=event_status)

