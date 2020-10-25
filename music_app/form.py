from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from music_app.models import *
from flask_login import current_user

class RegistrationForm(FlaskForm):
    fn = StringField("First Name",
                            validators = [DataRequired(), Length(min=2, max=20)])
    ln = StringField("Last Name",
                            validators = [DataRequired(), Length(min=2, max=20)])
    
    username = StringField("Username",
                            validators = [DataRequired(), Length(min=2, max=20)])
    username = StringField("Username",
                            validators = [DataRequired(), Length(min=2, max=20)])
    email = StringField("E-mail",
                            validators = [DataRequired(), Email()])
    password = PasswordField("Password",
                            validators = [DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                            validators = [DataRequired(), EqualTo("password")])
    check_artist = BooleanField("Are you an artist")
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("This username is already taken. Please choose a different username")
    
    def validate_email(self,email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("This email is already taken. Please choose a different email")

class LoginForm(FlaskForm):
    email = StringField("E-mail",
                        validators = [DataRequired(), Email()])
    password = PasswordField("Password",
                            validators = [DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField('Login')

class Artist_Label_Form(FlaskForm, UserMixin):
    name = StringField("Name",
                            validators = [DataRequired(), Length(max=20)])
    email = StringField("E-mail",
                            validators = [DataRequired(), Email()])
    label_name = StringField("Label Name",
                            validators = [DataRequired(), Length(max=20)])
    type = StringField("Type",
                            validators = [DataRequired(), Length(max=20)])
    insi = StringField("INSI Number",
                            validators = [DataRequired(), Length(max=20)])
    
    submit = SubmitField('Sign Up')


class UpdateAccountForm(FlaskForm):
    username = StringField("Username",
                            validators = [DataRequired(), Length(min=2, max=20)])
    email = StringField("E-mail",
                            validators = [DataRequired(), Email()])
    
    picture = FileField('Update Profile Pictures', validators=[FileAllowed(['jpg', 'png'])])
    check_artist = BooleanField("Do you want to be a artist")
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError("This username is already taken. Please choose a different username")
    
    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError("This email is already taken. Please choose a different email")

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Add Post')

class SongForm(FlaskForm):
    name = StringField('Song Name', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    album = StringField('Album', validators=[DataRequired()])
    song_file = FileField('Upload Song', validators=[FileAllowed(['mp3'])])
    picture = FileField('Upload Cover', validators=[FileAllowed(['jpg', 'png'])])
    singer =  StringField('Artist', validators=[DataRequired()])
    submit = SubmitField('Add Song')

class UploadPodcastForm(FlaskForm):
    title = StringField("Title",
                        validators=[DataRequired()])
    description = TextAreaField("Description",
                        validators=[DataRequired()])
    name = StringField("Podcast Name",
                        validators=[DataRequired()])
    category = StringField("Category",
                        validators=[DataRequired()])
    artist = StringField("Artist Name",
                        validators=[DataRequired()])
    pod_file = FileField('Upload Podcast', validators=[FileAllowed(['mp3'])])
    picture = FileField('Upload Cover', validators=[FileAllowed(['jpg', 'png'])])
    
    submit = SubmitField("Add Podcast")

class PlaylistName(FlaskForm):
    name = StringField("Playlist Name", validators=[DataRequired()])
    submit = SubmitField("Add Name")

class EventForm(FlaskForm, UserMixin):
    name = StringField("Event Name",
                            validators = [DataRequired(), Length(max=20)])
    time = StringField("Time",
                            validators = [DataRequired()])
    begin_date = StringField("Begin Date",
                            validators = [DataRequired(), Length(max=20)])
    end_date = StringField("End Date",
                            validators = [DataRequired(), Length(max=20)])
    status = StringField("Status",
                            validators = [DataRequired(), Length(max=20)])
    place_name = StringField("Place Name",
                            validators = [DataRequired(), Length(max=20)])
    address = StringField("Address",
                            validators = [DataRequired(), Length(max=20)])
    pincode = StringField("Pincode",
                            validators = [DataRequired(), Length(max=20)])
    city_name = StringField("City Name",
                            validators = [DataRequired(), Length(max=20)])
    state = StringField("State",
                            validators = [DataRequired(), Length(max=20)])
    submit = SubmitField('Register Event')


