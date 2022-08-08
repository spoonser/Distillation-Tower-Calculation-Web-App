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

from database.extensions import db
from database.create import create_tables

# Set up application and the necessary environment variables
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connect to database
db.init_app(app=app)

# -------------------------------------------------------------------------------------------------
# Main Index page 
# -------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')   

@app.route('/', methods=['POST'])
def upload_file():
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


# -------------------------------------------------------------------------------------------------
# Register user
# -------------------------------------------------------------------------------------------------
@app.route('/register')
def register():
    create_tables()
    return render_template('register.html')   


# -------------------------------------------------------------------------------------------------
# Login page
# -------------------------------------------------------------------------------------------------
@app.route('/login')
def login():
    return render_template('login.html')   

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
