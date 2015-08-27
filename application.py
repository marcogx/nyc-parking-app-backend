from flask import (Flask, g, render_template, flash,
                   redirect, url_for)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user, logout_user,
                             login_required, current_user)
from flask_googlemaps import GoogleMaps
from geopy.geocoders import GoogleV3
import forms
import models

import csv

PORT = 8004
HOST = '0.0.0.0'

application = Flask(__name__)
application.secret_key = '^tnm!&xvm!gor-l^jh$8jqmp^@q3dtwurv7nz*+j3tk=t%16o0'

GoogleMaps(application)
geolocator = GoogleV3()

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
	try:
		return models.User.get(models.User.id == userid)
	except models.DoesNotExist:
		return None


@application.before_request
def before_request():
	"""Connect to the database before each request."""
	g.db = models.DATABASE
	g.db.connect()
	g.user = current_user


@application.after_request
def after_request(response):
	"""Close the database connection after each request."""
	g.db.close()
	return response


@application.route('/register', methods=('GET', 'POST'))
def register():
	form = forms.RegisterForm()
	if form.validate_on_submit():
		flash("Yay, you registered!", "success")
		models.User.create_user(
			username=form.username.data,
			email=form.email.data,
			password=form.password.data
		)
		return redirect(url_for('index'))
	return render_template('register.html', form=form)


@application.route('/login', methods=('GET', 'POST'))
def login():
	form = forms.LoginForm()
	if form.validate_on_submit():
		try:
			user = models.User.get(models.User.email == form.email.data)
		except models.DoesNotExist:
			flash("Your email or password doesn't match!", "error")
		else:
			if check_password_hash(user.password, form.password.data):
				login_user(user)
				flash("You've been logged in!", "success")
				return redirect(url_for('index'))
			else:
				flash("Your email or password doesn't match!", "error")
	return render_template('login.html', form=form)


@application.route('/logout')
@login_required
def logout():
	logout_user()
	flash("You've been logged out! Come back soon!", "success")
	return redirect(url_for('index'))


def get_signs_of_center(center_lat=40.7484284, center_lng=-73.9856545199, zoom=18):
	with open('parkingsigns.csv') as f:
		signs_reader = csv.reader(f)
		locations, contents = [], []
		for row in signs_reader:
			lat, lng = float(row[0]), float(row[1])
			if abs(lat - center_lat) + abs(lng - center_lng) <= (0.05 / zoom):
				locations.append((lat, lng))
				contents.append(row[2])

		return locations, contents


map_center = (40.7484284, -73.9856545199)
global sign_locations, sign_contents


@application.route('/', methods=('GET', 'POST'))
def index():
	global map_center, sign_locations, sign_contents
	form = forms.PostForm()

	if form.validate_on_submit():
		addr = form.content.data.strip()
		location = None
		try:
			location = geolocator.geocode(addr)
			if not location:
				flash("Something wrong with your address typed or your network problem ", "error")
		except:
			flash("Something wrong with your address typed or your network problem ", "error")
		if location:
			map_center = location.latitude, location.longitude
			sign_locations, sign_contents = get_signs_of_center(location.latitude, location.longitude)
	return render_template('parking_signs.html', form=form,
	                       lat=map_center[0], lng=map_center[1],
	                       locations=sign_locations, contents=sign_contents)


@application.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404


if __name__ == '__main__':
	models.initialize()
	try:
		models.User.create_user(
			username='TestClient',
			email='t@t.com',
			password='123456',
			admin=False
		)
	except ValueError:
		pass
	global sign_locations, sign_contents
	sign_locations, sign_contents = get_signs_of_center()
	print sign_locations
	print sign_contents,
	print len(sign_locations), len(sign_contents)
	application.run(debug=models.DEBUG)
