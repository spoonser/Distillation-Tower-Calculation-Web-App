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


@click.command(name='create_tables')
@with_appcontext
def drop_and_create_tables():
	db.drop_all()
	db.create_all()
