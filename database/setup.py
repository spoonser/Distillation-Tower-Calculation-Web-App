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


def upload_component(component):
	"""
	Upload a component of binary distillation to the database
	"""
	component_upload = Component(
        name=component
    )
    # Commit new user to the database
	db.session.add(component_upload)
	db.session.commit()


def upload_vle(vle_data, component1, component2, user_id):
	"""
 	Upload the VLE data to the vle_data table
 	"""
	# Upload each data point to the database
	for key, val in vle_data['points'].iteritems():
		# Associate a user id to the data if it exists
		if user_id:
			datum = VleData(
				component1_id=component1,
				component2_id=component2,
				point=val,
				user_id=user_id
			)
		else:
			datum = VleData(
				component1_id=component1,
				component2_id=component2,
				point=val
			)
		# Add individual datum
		db.session.add(datum)
	# Commit rows
	db.session.commit()