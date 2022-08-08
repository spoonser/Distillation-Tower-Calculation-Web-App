# ***************************************************************************
# * Distillation Tower - Cost Minimization Project
# * Spencer Wagner
# * Server-Side functionality for Distillation Tower project
# ***************************************************************************

# Basic Flask functionality, importing modules for parsing results and accessing MySQL. 

from flask import Flask, render_template, request, json, flash, redirect, url_for
from flask_login import login_user, logout_user
import matplotlib.pyplot as plt
import static.py.VLE_graph as vle
import os

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from database.extensions import db, login_manager
from database.setup import drop_and_create_tables
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
    return None

# -------------------------------------------------------------------------------------------------
# Main Index page 
# -------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        xF = 0.044504
        xB = 0.0119526405
        xD = 0.855676706
        q = 1.0618231177199156

        vle_plot_url, nstage = vle.do_graph('ethanol-water.csv', xF, xD, xB, 3, q) 
        if vle_plot_url == "Error":
            return index()
        else:
            plot = '<img class="img-responsive" src="data:image/png;base64,{}">'.format(vle_plot_url)
            return render_template('index.html', plot=plot, graph_requested=True, nstage=nstage)

    # Load page normally
    return render_template('index.html')   


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
            error_message = 'Could not login'

        if not error_message:
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html')   

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
