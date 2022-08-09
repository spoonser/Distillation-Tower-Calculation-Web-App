# ***************************************************************************
# * Distillation Column Calculation - create.py
# * Spencer Wagner
# *
# * Create database tables function
# ***************************************************************************
import click
import pandas as pd
from flask.cli import with_appcontext
from copy import deepcopy

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


def upload_vle(vle_data, component1_id, component2_id, user_id):
	"""
 	Upload the VLE data to the vle_data table
 	"""
	# Swap component ids so the lower id is always component 1
	if component2_id < component1_id:
		temp1 = deepcopy(component1_id)
		temp2 = deepcopy(component2_id)
		component1_id = temp2
		component2_id = temp1

	# Upload each data point to the database
	for key, val in vle_data['points'].iteritems():
		# Associate a user id to the data if it exists
		if user_id:
			datum = VleData(
				component1_id=component1_id,
				component2_id=component2_id,
				point=val,
				user_id=user_id
			)
		else:
			datum = VleData(
				component1_id=component1_id,
				component2_id=component2_id,
				point=val
			)
		# Add individual datum
		db.session.add(datum)
	# Commit rows
	db.session.commit()


###############################################################################
def get_vle(component1_id, component2_id):
	"""
	Get VLE for component combination
	"""
	# Swap component ids so the lower id is always component 1
	if component2_id < component1_id:
		temp1 = deepcopy(component1_id)
		temp2 = deepcopy(component2_id)
		component1_id = temp2
		component2_id = temp1
	
	# Query for data
	dataset = VleData.query.filter_by(component1_id=component1_id).\
		filter_by(component2_id=component2_id).order_by(VleData.id).all()

	# Convert and return the dataframe to user	
	return point_to_dataframe(dataset)

# Helper function to convert VleData point data in postgresql to a dataframe
def point_to_dataframe(dataset):
	"""
	Converts the point data from the VleData formatted as "x,y" to floats
	in two dataframe columns
	"""
	# Initialize 2d array that will be converted to a dataframe
	data = []

	# Convert point formatted as "x,y" into two floats and insert to array
	for item in dataset:
		points = item.point.split(',')
		points = [float(i) for i in points]
		data.append(points)

	return pd.DataFrame(data)

	# Convert to dataframe


###############################################################################