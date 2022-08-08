# ***************************************************************************
# * Distillation Column Calculation - create.py
# * Spencer Wagner
# *
# * Create database tables function
# ***************************************************************************
import click
import os
from flask.cli import with_appcontext

from .models import User, Component, VleData
from .extensions import db

# Set up connection to database
def setup_db(app):
	"""
	Set up the database in app.py
	""" 
	database_name ='distillation'
	default_database_path= "postgresql://{}:{}@{}/{}".format('postgres', 'password', 'localhost:5432', database_name)
	database_path = os.getenv('DATABASE_URL', default_database_path)
	app.config["SQLALCHEMY_DATABASE_URI"] = database_path
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
	db.app = app
	db.init_app(app)


@click.command(name='create_tables')
@with_appcontext
def drop_and_create_tables():
	db.drop_all()
	db.create_all()
