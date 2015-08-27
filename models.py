import datetime
import os
from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *

# DATABASE = SqliteDatabase('social.db')
# DATABASE = MySQLDatabase("microtwitter", host="microtwitter.cvxlucsoypjt.us-west-2.rds.amazonaws.com",
#                          port=3306, user="microtwitter", passwd="microtwitter")

DATABASE = Proxy()
DEBUG = True


class User(UserMixin, Model):
	username = CharField(unique=True)
	email = CharField(unique=True)
	password = CharField(max_length=100)
	joined_at = DateTimeField(default=datetime.datetime.now)
	is_admin = BooleanField(default=False)

	class Meta:
		database = DATABASE
		order_by = ('-joined_at',)

	@classmethod
	def create_user(cls, username, email, password, admin=False):
		try:
			with DATABASE.transaction():
				cls.create(
					username=username,
					email=email,
					password=generate_password_hash(password),
					is_admin=admin)
		except IntegrityError:
			raise ValueError("User already exists")


class Parkingsigns(Model):
	content = TextField(null=True)
	lat = FloatField(null=True)
	lng = FloatField(null=True)
	signid = PrimaryKeyField()

	class Meta:
		database = DATABASE
		db_table = 'parkingsigns'


if 'HEROKU' in os.environ:
	import urlparse, psycopg2
	urlparse.uses_netloc.append('postgres')
	url = urlparse.urlparse(os.environ["DATABASE_URL"])
	db = PostgresqlDatabase(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
	DATABASE.initialize(db)
	DEBUG = False
else:
	db = SqliteDatabase('nyc-parking-app-backend.db')
	DATABASE.initialize(db)


def initialize():
	DATABASE.connect()
	DATABASE.create_tables([User, ], safe=True)
	DATABASE.close()
