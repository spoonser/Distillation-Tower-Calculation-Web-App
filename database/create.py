# ***************************************************************************
# * Distillation Column Calculation - create.py
# * Spencer Wagner
# *
# * Create database tables function
# ***************************************************************************
import click
from flask.cli import with_appcontext

from .extensions import db
from .models import User, Component, VleData

@click.command(name='create_tables')
@with_appcontext
def create_tables():
	db.create_all()
