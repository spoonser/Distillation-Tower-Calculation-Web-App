# ***************************************************************************
# * Distillation Tower - Cost Minimization Project
# * Spencer Wagner
# * Server-Side functionality for Distillation Tower project
# ***************************************************************************

# Basic Flask functionality, importing modules for parsing results and accessing MySQL. 

from flask import Flask, render_template, request, json, flash, redirect, url_for, g
from flask_login import login_user, logout_user, current_user
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import static.py.VLE_graph as vle
import os

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from database.extensions import db, login_manager
from database.commands import upload_component, upload_vle, get_vle
from database.models import User, Component, VleData

# Set up application and the necessary environment variables
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///distillation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'NOT_A_SECRET'

# Connect to database
db.init_app(app)
# Initialize login manager for the application
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None

# -------------------------------------------------------------------------------------------------
# Main Index page 
# -------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    # Query for components list in alphabetical order
    components = Component.query.order_by(Component.name).all()
    
    if request.method == 'POST':
        # xF = 0.044504
        # xB = 0.0119526405
        # xD = 0.855676706
        # q = 1.0618231177199156

        # Get data from form
        xF = float(request.form['mole_frac_feed'])
        xD = float(request.form['mole_frac_dist'])
        xB = float(request.form['mole_frac_bot'])
        R = float(request.form['reflux_ratio'])
        q = float(request.form['quality'])

        # Get vle data and query for it
        component1_id = request.form['component1']
        component2_id = request.form['component2']
        VLE_data = get_vle(component1_id, component2_id)
        
        # Create plot based on inputs
        vle_plot_url, nstage = vle.do_graph(VLE_data, xF, xD, xB, R, q) 
        if vle_plot_url == "Error":
            return index()
        else:
            plot = '<img class="img-responsive" src="data:image/png;base64,{}">'.format(vle_plot_url)
            return render_template('index.html', plot=plot, graph_requested=True,
                                    nstage=nstage, components=components)

    # Load page normally
    return render_template('index.html', components=components)   


# -------------------------------------------------------------------------------------------------
# Register user
# -------------------------------------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        unhashed_password = request.form['password']

        # Get user information
        user = User(
            name=name,
            unhashed_password=unhashed_password
        )

        # Commit new user to the database
        db.session.add(user)
        db.session.commit()

        flash('Successfully created user {}'.format(name))
        return redirect(url_for('login'))

    return render_template('register.html')

# -------------------------------------------------------------------------------------------------
# Login page
# -------------------------------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        user = User.query.filter_by(name=name).first()

        error_message = ''

        if not user or not check_password_hash(user.password, password):
            error_message = "Could not login"
            flash(error_message)

        if not error_message:
            login_user(user)
            flash("User {} has logged in".format(name))

            return redirect(url_for('index'))

    return render_template('login.html')   


# -------------------------------------------------------------------------------------------------
# Logout
# -------------------------------------------------------------------------------------------------
@app.route('/logout')
def logout():
    logout_user()
    flash("Successfully logged out")
    return redirect(url_for('index'))


# -------------------------------------------------------------------------------------------------
# Upload data
# -------------------------------------------------------------------------------------------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':

        # Attempt to get files from user
        if request.files['user-file'].filename != '':
            component1 = request.form['component1']
            component2 = request.form['component2']
            
            # Don't bother querying if component1 and component2 aren't distinct
            # or they don't exist
            if component1 == component2 or component1 == '' or component2 == '':
                flash('Components must be different from eachother!')
                return render_template('upload.html')

            # Add components to the components table if they don't exist already
            if Component.query.filter_by(name=component1).count() == 0:
                upload_component(component1)

            if Component.query.filter_by(name=component2).count() == 0:
                upload_component(component2)          

            # Get and convert data to database-ready format
            data = pd.read_csv(request.files.get('user-file')) 
            # Add a new column to the data that has the two columns joined
            # so they can be uploaded to the database
            data = np.trunc(1000 * data) / 1000 # Truncate floating points
            
            # Create new column of strings
            data['points'] = data[data.columns[0:]].apply(
                lambda x: ','.join(x.dropna().astype(str)),
                axis=1
            ) 

            # Get component ids
            component1_id = Component.query.filter_by(name=component1).first().id
            component2_id = Component.query.filter_by(name=component2).first().id

            # Check that data for this combo of components does not exist
            if (VleData.query.filter_by(component1_id=component1_id).\
                filter_by(component2_id=component2_id).first()):
                flash('Data for this combination of components already exists')
                return render_template('upload.html')

            # Perform query to insert data to postgresql
            upload_vle(data, component1_id, component2_id, current_user.get_id())

            flash("Data successfully uploaded!")
            return redirect(url_for('upload'))


    return render_template('upload.html')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
