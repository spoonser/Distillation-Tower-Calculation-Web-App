# ***************************************************************************
# * Distillation Column Calculation - create.py
# * Spencer Wagner
# *
# * Create database tables function
# ***************************************************************************
from multiprocessing import synchronize
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

###############################################################################
# CREATE COMMANDS
###############################################################################
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
# GET COMMANDS
###############################################################################
# This section serves the requestor with the VLE data based on the components
# specified
def get_vle_from_components(component1_id, component2_id):
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

	#
	return pd.DataFrame(data)
###############################################################################

###############################################################################
# DELETE COMMANDS
###############################################################################
# This section serves the requestor with the list of vle components they've
# uploaded
def get_user_vle_dict(user_id):
	"""
	Based on user id, requests the rows inserted to the vle_data table by the
	user specified. Returns a dictionary that contains the id combos and the
	names
	"""
	# Query the vle_table table for all data uploaded by the current user
	user_vle = VleData.query.filter_by(user_id=user_id).all()
	# Initialize a dictionary to hold the component id combos uploaded by user
	component_combos = {}

	# Add a single instance of the component combos as a tuple key to the 
	# dictionary and have the value be a string with the component names 
	for row in user_vle:
		key = (row.component1_id, row.component2_id)
		if key not in component_combos:
			component_combos[key] = Component.query.filter_by(id=row.component1_id).first().name \
				+ " / " + Component.query.filter_by(id=row.component2_id).first().name

	return component_combos

# Delete user uploaded data from the database
def delete_user_data(component1_id, component2_id, user_id):
	"""
	Deletes the user data from vle_data where the component ids and user ids
	match the specified. Calls the helper function XXXXXXXX to delete
	components from the component table if there is no data associated with it
	"""
	# Query for all rows that match the 
	VleData.query.filter_by(component1_id=component1_id).\
        filter_by(component2_id=component2_id).filter_by(user_id=user_id).delete()
	db.session.commit()
	
	# Call delete_empty_component to possibly delete components if no data exists
	delete_empty_component(component1_id)
	delete_empty_component(component2_id)


def delete_empty_component(component_id):
	"""
	Deletes a component if no data is associated with it
	"""
	# Flag whether data for the component exists in col1 or col2 
	data_in_col1 = VleData.query.filter_by(component1_id=component_id).first()
	data_in_col2 = VleData.query.filter_by(component2_id=component_id).first()

	# Delete component from database if it does have associated data
	if data_in_col1 is None and data_in_col2 is None:
		Component.query.filter_by(id=component_id).delete()
		db.session.commit()