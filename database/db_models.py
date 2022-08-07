import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy

conn = SQLAlchemy(DATABASE_URI)


cur = conn.cursor()
