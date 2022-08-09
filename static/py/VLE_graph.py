# ***************************************************************************
# * Distillation Column Calculation - VLE_graph.py 
# * Spencer Wagner
# *
# * Draws a Vapor-Liquid Equilibrium graph, returns it along with the number
# * of stages that are optimal for cost
# ***************************************************************************

#Import required packages
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as poly
from matplotlib import cm
from pandas.core.base import DataError
import numpy as np
import pandas as pd
import math
import io
import base64

# Import data
def get_data(vle_data):
	"""
	Imports Vapor-Liquid equilibrium curve data from source
	"""
	# Grab the first and second columns of data separately
	x_sep = vle_data.loc[:, 0]
	y_sep = vle_data.loc[:, 1]

	coefs = poly.polyfit(x_sep, y_sep, 10)
	x_new = [1 / 5000 * i for i in range(5000)]
	ffit = poly.polyval(x_new, coefs)
	return x_new, ffit


# Function to set up the graph
def init_graph(x_sep, y_sep):
	"""
	Draws the plot with the separation data of the two components at
	vapor-liquid equilibrium
	"""
	# Plot x_sep and y_sep
	plt.plot(x_sep, y_sep)
	plt.plot(x_sep, x_sep)
	plt.xlim([0, 1])
	plt.ylim([0, 1])

	# Label graph
	plt.xlabel('Mole Fraction of X in Liquid', fontsize=18, fontname='Liberation Serif')
	plt.ylabel('Mole Fraction of X in Vapor', fontsize=18, fontname='Liberation Serif')
	plt.xticks(fontsize=12)
	plt.yticks(fontsize=12)



# Function to solve for and draw the q line
def draw_q(q, xF):
	"""
	Solve for and draw the q line (q is the mole fraction of liquid in the
	feed)
	"""

	#Solve for the q line
	q_pntx = [xF, xF + 0.025]
	q_pnty = [xF, q / (q - 1) * (xF + 0.025) - xF / (q - 1)]
	q_line = np.polyfit(q_pntx, q_pnty, 1)

	# Add q line to the plot
	plt.plot(q_pntx, q_pnty)

	# Return q line for drawing the enriching/stripping lines
	return q_line


def enriching_stripping(R, q_line, xD, xB):
	"""
	Solves for and draws the enriching and stripping lines on the plot
	"""

	# Solve for the enriching line
	enr_x = [0, xD]
	enr_y = [xD / (R + 1), xD]
	enr_line = np.polyfit(enr_x, enr_y, 1)

	# Find the point where the enriching line and q line intersect
	intersect = np.roots(q_line - enr_line)[0]
	enr_x = [intersect, xD]
	enr_y = [np.polyval(enr_line, intersect), xD]

	# Plot enriching line
	plt.plot(enr_x, enr_y)

	# Calculate stripping line 
	strip_x = [xB, intersect]
	strip_y = [xB, np.polyval(enr_line, intersect)]
	strip_line = np.polyfit(strip_x, strip_y, 1)

	# Plot stripping line
	plt.plot(strip_x, strip_y)

	# Return enriching and stripping line for future calcs
	return enr_line, strip_line


def distillation_stages(x_sep, y_sep, xB, xD, enr_line, strip_line):
	"""
	This performs the McCabe-Thiele method for drawing the number of stages
	required to meet the process requirements. 
	"""
	# Initialize information for drawing lines
	nstage = 0
	x_current = xD
	y_current = xD

	while True:
	
		for x_index, x_frac in enumerate(x_sep):
			y_frac = y_sep[x_index]
		
			if y_frac >= y_current:
				plt.plot([x_sep[x_index], x_current], [y_current, y_current], 'k-')
				x_current = x_sep[x_index]
				break
	
		nstage += 1

		# Break out of calculation if number of stages is too high
		if nstage > 100:
			return nstage
		# Exit condition: the stages have been drawn past the point where
		# process requirements are met, return number of stages needed
		if x_current < xB:
			return nstage

		y_enr_check = np.polyval(enr_line, x_current)
		y_strip_check = np.polyval(strip_line, x_current)

		
		if y_enr_check < y_strip_check:
			plt.plot([x_current, x_current], [y_current, y_enr_check], 'k-')
			y_current = y_enr_check

		else:
			plt.plot([x_current, x_current], [y_current, y_strip_check], 'k-')
			y_current = y_strip_check


def serve_graph():
	"""
	Returns a base64 encoded image of the plot to the user
	"""
	img = io.BytesIO()
	plt.savefig(img, format='png')
	img.seek(0)

	# Encodes png graph as 64 bit image
	plot_url = base64.b64encode(img.getvalue()).decode()

	return plot_url


def calc_nstages(nstage, efficiency):
	"""
	Calculates the number of stages needed considering efficiency of each tray
	"""
	return math.ceil(nstage/efficiency)


def do_graph(vle_data, xF, xD, xB, R, q):
	"""
	Performs the VLE calculations using the VLE data and parameters provided
	"""
	# Get the x and y component separation data
	x_sep, y_sep = get_data(vle_data)

	# Initialize the graph
	init_graph(x_sep, y_sep)

	# Draw the q line and get the equation for said line
	plt.figure(1)
	q_line = draw_q(q, xF)

	# Draw the enriching and stripping lines and the equation for both
	plt.figure(1)
	enr_line, strip_line = enriching_stripping(R, q_line, xD, xB)

	# Draw the number of distillation stages required and get the number of stages
	plt.figure(1)
	nstage = distillation_stages(x_sep, y_sep, xB, xD, enr_line, strip_line)

	# Return the encoded graph and the number of stages required to the user
	if nstage < 100:
		return serve_graph(), nstage
	# Something is wrong with the parameters, return an error
	else:
		return "Error", "Error"
