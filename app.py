from flask import Flask, render_template, url_for, redirect, request, jsonify, redirect
from sqlalchemy import select
from db import db
from db_models import User, Post
import uuid
import requests
import folium
import os
import json
import xyzservices.providers as xyz #Can use this to change map type
from temp_data import *
from urllib.parse import quote
# from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Email, InputRequired, Length, ValidationError, EqualTo
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer as Serializer
from db_models import db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '4a0a3f65e0186d76a7cef61dd1a4ee7b'

EBIRD_API_RECENT_BIRDS_URL = 'https://api.ebird.org/v2/data/obs/geo/recent' 
EBIRD_API_KEY = os.environ['EBIRD_API_KEY']
GOOGLE_MAPS_API_KEY = os.environ['GOOGLE_MAPS_API_KEY']


db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class SignUpForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(max=120)], render_kw={"placeholder": "Email"})  
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField(validators=[InputRequired(), Length(min=4, max=20), EqualTo('password')], render_kw={"placeholder": "Confirm_Password"})
    submit = SubmitField("Sign Up")

def validate_username(self, username):
    exists_user = User.query.filter_by(username=username.data).first()
    if exists_user:
        raise ValidationError("Username already exists. Select a new username.")

def validate_email(self, email):
    exists_email = User.query.filter_by(email=email.data).first()
    if exists_email:
        raise ValidationError("Email already exists. Use another email address.")
        
class SignInForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(max=120)], render_kw={"placeholder": "Email"})  
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"}) 
    remember = BooleanField('Remember Me')
    submit = SubmitField("Login")     

    def validate_username(self, username):
        exists_user = User.query.filter_by(
            username=username.data).first()
        if not exists_user:
            raise ValidationError("Username does not exist.")
    
    def validate_email(self, email):
        exists_email = User.query.filter_by(email=email.data).first()
        if not exists_email:
            raise ValidationError("Email does not exist.")



@app.route('/')
def index():
    return render_template("index.html")

@app.route('/map')
def map():
    return render_template("map.html", google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.get_json()
    latitude = data['latitude']
    longitude = data['longitude']
    
    page = data.get('page', 1)
    page_size = 3
    
    birds_near_user = getRecentBirds(latitude, longitude)

    m = folium.Map(location=[latitude, longitude], zoom_start=13)
    folium.Marker([latitude, longitude], tooltip='Your Location').add_to(m)

    for bird in birds_near_user:
        bird_name = bird.get('comName')
        bird_lat = bird.get('lat')
        bird_long = bird.get('lng')
        folium.Marker(
            location=[bird_lat, bird_long],
            tooltip=bird_name,
            icon=folium.Icon(color='red')
        ).add_to(m)

    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_birds = birds_near_user[start_index:end_index]

    bird_data = []
    
    for index, bird in enumerate(paginated_birds):
        bird_name = bird.get('comName')

        formatted_bird_name = formatBirdName(bird_name)
        image_url = getWikipediaImage(formatted_bird_name)
        description = f"{bird_name} is spotted near your location."

        bird_data.append({
            'imageUrl': image_url,
            'title': bird_name,
            'description': description,
            'url': f'/bird/{quote(bird_name)}'
        })

    # Get HTML of map
    map_html = m._repr_html_()

    return jsonify(mapHtml=map_html, birdData=bird_data)

def getRecentBirds(latitude, longitude):
    headers = {
        'X-eBirdApiToken': EBIRD_API_KEY
    }
    params = {
        'lat': latitude,
        'lng': longitude,
        'dist': 30  #Distance in km for observations
    }
    response = requests.get(EBIRD_API_RECENT_BIRDS_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return []
    
def formatBirdName(bird_name):
    bird_name = bird_name.replace(' ', '_')

    parts = bird_name.split('_')

    formatted_name = parts[0]

    if len(parts) > 1:
        formatted_name += '_' + '_'.join(part.lower() for part in parts[1:])

    return formatted_name

def getWikipediaImage(bird_name):
    formatted_bird_name = formatBirdName(bird_name)
    search_url = f'https://en.wikipedia.org/w/api.php?action=query&titles={formatted_bird_name}&prop=pageimages&format=json&pithumbsize=100'
    response = requests.get(search_url)

    if response.status_code == 200:
        data = response.json()
        pages = data.get('query', {}).get('pages', {})
        for page_id, page in pages.items():
            image_url = page.get('thumbnail', {}).get('source')
            if image_url:
                return image_url
    else:
        print(f"Failed to fetch data from Wikipedia. Status code: {response.status_code}")

    return None

def get_bird_info(bird_name):
    return {
        'imageUrl': getWikipediaImage(bird_name),
        'title': bird_name
    }

@app.route('/bird/<bird_name>')
def bird_page(bird_name):
    bird_info = get_bird_info(bird_name)
    return render_template('bird.html', bird=bird_info)

@app.route('/signin', methods=['GET','POST'])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data, email=form.email.data).first()
            if user:
                if not bcrypt.check_password_hash(user.password, form.password.data):
                    raise ValidationError("Incorrect password.")
                else:
                    login_user(user)
                    return redirect(url_for('profile'))
            else:
                raise ValidationError("Invalid username or email.")
        except ValidationError as e:
            form.username.errors.append(e.args[0])  
            return render_template("signin.html", form=form)
    return render_template("signin.html", form=form)


def signout():
    logout_user()
    return redirect(url_for('signin'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        hashed_passwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(email=form.email.data, username=form.username.data, password=hashed_passwd)
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('signin'))
    return render_template("signup.html", form=form)

# TODO: adjust when we have users & logged-in users in the DB
@app.route('/profile/<profile_id>', methods=['POST', 'GET'])
def profile_id(profile_id):
  
    profile_path = "/profile/" + profile_id

    # POST happens on "edit profile" submit
    if request.method == 'POST' and "edit_profile_name" in request.form:
        
        new_name = request.form["edit_profile_name"]
        new_profile = User(userID=uuid.uuid4(), username=profile_id, email=new_name, password=new_name, firstName=new_name)
        
        #add the profile to the database
        try:
            # try to get the current profile from the DB based on 
            selected_id = db.session.scalars(select(User.userID).where(User.username == profile_id)).first()
            if selected_id != None:
                current_profile = db.session.get(User, selected_id)
                current_profile.firstName = new_name
                db.session.commit()
                return redirect(profile_path)

            # it didn't exist, so add it to the DB
            else:
                db.session.add(new_profile)
                db.session.commit()
                return redirect(profile_path)
        
        #any additional errors
        except Exception as error:
            print(error)
            return "There was an issue editing your profile"

    # POST happens on Add Photo submit button
    elif request.method == 'POST' and "add_photo_caption" in request.form:
        
        new_caption = request.form["add_photo_caption"]

        #add the new post to the database
        try:
            # try to get the current user from the DB based on username
            selected_id = db.session.scalars(select(User.userID).where(User.username == profile_id)).first()

            if selected_id != None:

                new_post = Post(postID=uuid.uuid4(), caption=new_caption, userID=selected_id)
                db.session.add(new_post)
                db.session.commit()

                return redirect(profile_path)

            # the user didn't exist
            else:
                #TODO: post failed is a pop up
                return "User does not exist; Posting image failed"
        
        #any additional errors
        except Exception as error:
            print(error)
            return "There was an issue adding a photo"
    # page is loaded normally
    else:

        # get the profile by its id (primary key)
        selected_id = db.session.scalars(select(User.userID).where(User.username == profile_id)).first()
        if selected_id != None:
            user = db.session.get(User, selected_id)
            posts = user.to_dict()['posts']
            context = {
                "socialPosts": socialPosts,
                "events": events,
                "badges": badges,
                "id" : profile_id,
                "user": user,
                "userPosts": posts
            }
            return render_template("profile.html", **context)
        
        # nonexistent user
        else:
            
            return "User does not exist"

# TODO: delete me
@app.route('/profile')
def profile():
    context = {
        "socialPosts": socialPosts,
        "events": events,
        "badges": badges
    }
    return render_template("profile.html", **context)

  
@login_required
@app.route('/social')
def social():
    context = {
        "events": events,
    }
    return render_template("social.html", **context)

@app.route('/bird')
def bird():
    return render_template("bird.html")

if __name__ == "__main__":
    app.run(debug=True)