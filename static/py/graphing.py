# ***************************************************************************
# * CS361 Project - Analytics Application 
# * Spencer Wagner
# * Graphing functions for Analytics application
# ***************************************************************************

import matplotlib.pyplot as plt
from matplotlib import cm
from pandas.core.base import DataError
import numpy as np
import pandas as pd
import io
import base64


# ***************************************************************************
# * PLOTTING FUNCTIONS - Bar, Line, Scatter, Pie charts
# ***************************************************************************

# Create a barchart
def bar_plot(data, specs):
	# Plot figure
	img = io.BytesIO()

	cmap = cm.get_cmap(specs[1])(np.linspace(0.2, 0.7, len(data)))

	data.plot(kind='bar', x=specs[2], y=specs[3], legend=False, color=cmap, rot=0)

	# Plot formatting
	if specs[4]:
		plt.subplots_adjust(bottom=0.15)
	plt.title(specs[6])
	plt.xlabel(specs[4])
	plt.ylabel(specs[5])
	plt.savefig(img, format='png')
	img.seek(0)

	plot_url = base64.b64encode(img.getvalue()).decode()	

	return plot_url


def line_plot(data, specs):
	# Plot figure
	img = io.BytesIO()

	cmap = cm.get_cmap(specs[1])(np.linspace(0.2, 0.7, len(data)))

	data.plot(kind='line', x=specs[2], y=specs[3], legend=False, color=cmap, rot=0)
	
	# Plot formatting
	if specs[4]:
		plt.subplots_adjust(bottom=0.15)
	plt.title(specs[6])
	plt.xlabel(specs[4])
	plt.ylabel(specs[5])
	plt.legend('')
	plt.savefig(img, format='png')
	img.seek(0)

	plot_url = base64.b64encode(img.getvalue()).decode()	

	return plot_url


def scatter_plot(data, specs):
	# Plot figure
	img = io.BytesIO()

	cmap = cm.get_cmap(specs[1])(np.linspace(0.2, 0.7, len(data)))
	
	# Create separate ticks if the x axis is a string
	if type(data.loc[0, specs[2]]) == str:
		ticks = [i for i in range(1, data.shape[0]+1)]
		plt.scatter(ticks, data[specs[3]], s=120, c=cmap)
		ax = plt.gca()
		ax.legend_ = None
		plt.xticks(ticks, data[specs[2]], rotation=30)

	else:	
		data.plot.scatter(specs[2], specs[3], legend=False, s=120, c=cmap, rot=30)

	# Plot formatting
	if specs[2]:
		plt.subplots_adjust(bottom=0.15)
	plt.title(specs[6])
	plt.xlabel(specs[2])
	plt.ylabel(specs[3])
	plt.legend('')
	plt.savefig(img, format='png')
	img.seek(0)

	plot_url = base64.b64encode(img.getvalue()).decode()	

	return plot_url


def pie_plot(data, specs):
	# Plot figure
	img = io.BytesIO()

	cmap = cm.get_cmap(specs[1])(np.linspace(0.2, 0.7, len(data)))
	labels = ['']*len(data)

	data.set_index(specs[2], inplace=True)
	
	data.plot.pie(y=specs[3], autopct='%.0f', legend=False, labels=labels, colors=cmap)
	plt.xlabel('')
	plt.ylabel('')
	plt.legend(loc=3, labels=data.index)
	plt.title(specs[6])
	plt.savefig(img, format='png')
	img.seek(0)

	# Encodes png graph as 64 bit image
	plot_url = base64.b64encode(img.getvalue()).decode()

	return plot_url


# ***************************************************************************
# * Plot selector - Returns one of the above function returns depending
# * on input
# ***************************************************************************

def get_plot(data, specs):
	if specs[0] == 'bar':
		return bar_plot(data, specs)
	
	if specs[0] == 'line':
		return line_plot(data, specs)

	if specs[0] == 'scatter':
		return scatter_plot(data, specs)

	if specs[0] == 'pie':
		return pie_plot(data, specs)

	return 'Graph generation failed'

def get_graph_specs(data):
	"""
	Return relevant data from user requests for graph params
	"""
	graph_type = data['graph_type']
	colors = data['colors']
	xaxis, yaxis = data['xaxis'], data['yaxis']
	xlabel, ylabel = data['xlabel'], data['ylabel']
	title = data['title']
 
	return [graph_type, colors, xaxis, yaxis, xlabel, ylabel, title]