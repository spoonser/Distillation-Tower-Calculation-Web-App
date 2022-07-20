# ***************************************************************************
# * CS361 Project - Analytics Application 
# * Spencer Wagner
# * Stats functions for analytics application
# ***************************************************************************

import matplotlib.pyplot as plt
from matplotlib import cm
from pandas.core.base import DataError
import numpy as np
import pandas as pd
import io
import base64


# ***************************************************************************
# * BASIC STATS - Mean, median, mode, standard deviation 
# ***************************************************************************

def get_mean(df, col):
	"""
	Returns mean of data set
	"""
	try:
		mean = df[col].mean()
	except:
		mean = 'Not calculable'
	return mean

def get_median(df, col):
	"""
	Returns median of data set
	"""
	try:
		median = df[col].median()
	except:
		median = 'Not calculable'
	return median

def get_mode(df, col):
	"""
	Returns mode of data set
	"""
	try:
		mode = df[col].mode().loc[0]
	except:
		mode = 'Not calculable'
	return mode

def get_stddev(df, col):
	"""
	Returns standard deviation of data set
	"""
	try:
		mode = df[col].stddev()
	except:
		mode = 'Not calculable'
	return mode