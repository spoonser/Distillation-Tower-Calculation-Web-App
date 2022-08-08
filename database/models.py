from flask_login import UserMixin
from werkzeug.security import generate_password_hash
import os

from .extensions import db

# User model
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	password = db.Column(db.String(150))

	@property
	def unhashed_password(self):
		raise AttributeError('Cannot view unhashed password!')

	@unhashed_password.setter
	def unhashed_password(self, unhashed_password):
		self.password = generate_password_hash(unhashed_password)
	

# Molecular component database model
class Component(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))


# VLE data table
class VleData(db.Model):
	__table_args__ = (
		db.CheckConstraint('component1_id != component2_id'),
	)
	component1_id = db.Column(db.Integer, db.ForeignKey('component.id'))
	component2_id = db.Column(db.Integer, db.ForeignKey('component.id'))
	point = db.Column(db.String(50), primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

