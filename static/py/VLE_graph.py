# ***************************************************************************
# * Distillation Column Calculation - VLE_graph.py 
# * Spencer Wagner
# *
# * Draws a Vapor-Liquid Equilibrium graph, returns it along with the number
# * of stages that are optimal for cost
# ***************************************************************************

#Import required packages
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math


# Import data
def import_data(data):
	"""
	Imports Vapor-Liquid equilibrium curve data from source
	"""
	# Grab data from csv file
	VLE_Data = pd.read_csv(data)
	VLE_Data = VLE_Data.values

	# 
	x_sep = VLE_Data[:, 0]
	y_sep = VLE_Data[:, 1]

	return x_sep, y_sep


# Function to set up the graph
def graph_init(x_sep, y_sep):
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
	plt.xlabel('Mole Fraction of Lighter Component in Liquid', fontsize=18, fontname='Liberation Serif')
	plt.ylabel('Mole Fraction of Lighter Component in Vapor', fontsize=18, fontname='Liberation Serif')
	plt.xticks(fontsize=15, fontname='Liberation Serif')
	plt.yticks(fontsize=15, fontname='Liberation Serif')



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


def enriching_stripping(R, q_line, xD, xW):
	"""
	Solves for and draws the enriching and stripping lines on the plot
	"""

	# Solve for the enriching line
	enr_x = [0, xD]
	enr_y = [xD / (R + 1), xD]
	enr_line = np.polyfit(enr_x, enr_y, 1)

	# Find the point where the enriching line and q line intersect
	intersect = np.roots(q_line - enr_line)
	enr_x = [intersect, xD]
	enr_y = [np.polyval(enr_line, intersect), xD]

	# Plot enriching line
	plt.plot(enr_x, enr_y)

	# Calculate stripping line 
	strip_x = [xW, intersect]
	strip_y = [xW, np.polyval(enr_line, intersect)]
	strip_line = np.polyfit(strip_x, strip_y, 1)

	# Plot stripping line
	plt.plot(strip_x, strip_y)

	# Return enriching and stripping line for future calcs
	return enr_line, strip_line


def distillation_stages(x_sep, y_sep, xW, xD, enr_line, strip_line):
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
		# Exit condition: the stages have been drawn past the point where
		# process requirements are met, return number of stages needed
		if x_current < xW:
			return nstage

		y_enr_check = np.polyval(enr_line, x_current)
		y_strip_check = np.polyval(strip_line, x_current)

		
		if y_enr_check < y_strip_check:
			plt.plot([x_current, x_current], [y_current, y_enr_check], 'k-')
			y_current = y_enr_check

		else:
			plt.plot([x_current, x_current], [y_current, y_strip_check], 'k-')
			y_current = y_strip_check


def calc_nstages(nstage, efficiency):
	"""
	Calculates the number of stages needed considering efficiency of each tray
	"""
	return math.ceil(nstage/efficiency)