from flask import Flask, render_template, flash
from flask_googlemaps import GoogleMaps, Map
from geopy.geocoders import GoogleV3
import forms
import csv
import logging
import sys

app = Flask(__name__)
app.secret_key = '^tnm!&xvm!gor-l^jh$8jqmp^@q3dtwurv7nz*+j3tk=t%16dafadsfo0'
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

GoogleMaps(app)
geolocator = GoogleV3()


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


@app.route('/', methods=('GET', 'POST'))
def index():
	map_center = (40.7484284, -73.9856545199)
	form = forms.PostForm()
	locations, contents = get_signs_of_center()

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
			locations, contents = get_signs_of_center(map_center[0], map_center[1])

		return render_template('parking_signs.html', form=form,
		                       lat=map_center[0], lng=map_center[1],
		                       locations=locations, contents=contents)

	return render_template('parking_signs.html', form=form,
	                       lat=map_center[0], lng=map_center[1],
	                       locations=locations, contents=contents)


@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404


@app.route("/test", methods=('GET', 'POST'))
def mapview():
	mymap = Map(
		identifier="view-side",
		lat=37.4419,
		lng=-122.1419,
		markers=[(37.4419, -122.1419)]
	)
	sndmap = Map(
		identifier="sndmap",
		lat=37.4419,
		lng=-122.1419,
		markers={'http://maps.google.com/mapfiles/ms/icons/green-dot.png': [(37.4419, -122.1419)],
		         'http://maps.google.com/mapfiles/ms/icons/blue-dot.png': [(37.4300, -122.1400)]}
	)
	return render_template('example.html', mymap=mymap, sndmap=sndmap)


if __name__ == '__main__':
	# global sign_locations, sign_contents
	sign_locations, sign_contents = get_signs_of_center()
	print sign_locations
	print sign_contents,
	# GoogleMaps(app)
	print len(sign_locations), len(sign_contents)
	app.run(debug=True)
