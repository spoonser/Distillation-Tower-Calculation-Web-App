#Comparison of Ethanol and Water VLE Data using margules and ChemSep Data

#Import required packages
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math

#Import ethanol-water VLE data from ChemSep
VLE_Data = pd.read_csv('EthanolVLE_5000pts.csv')
VLE_Data = VLE_Data.values

x_sep = VLE_Data[:, 0]
y_sep = VLE_Data[:, 1]

#Plot x_sep and y_sep
plt.plot(x_sep, y_sep)
plt.plot(x_sep, x_sep)
plt.xlim([0, 1])
plt.ylim([0, 1])

################################################
#Portion to solve and graph the McCabe-Thiele diagram
#Store xF, xW, xD, D, q
xF = 0.044504
xW = 0.0119526405
xD = 0.855676706

#Solve for the q line
q = 1.0618231177199156
q_pntx = [xF, xF + 0.025]
q_pnty = [xF, q / (q - 1) * (xF + 0.025) - xF / (q - 1)]
q_line = np.polyfit(q_pntx, q_pnty, 1)
plt.plot(q_pntx, q_pnty)

#Initialize x and y current points, R
y_current = xD
x_current = xD

#for x in R:

	#Solve for the enriching and stripping lines
R = 4.43

enr_x = [0, xD]
enr_y = [xD / (R + 1), xD]
enr_line = np.polyfit(enr_x, enr_y, 1)

intersect = np.roots(q_line - enr_line)
enr_x = [intersect, xD]
enr_y = [np.polyval(enr_line, intersect), xD]
plt.plot(enr_x, enr_y)


strip_x = [xW, intersect]
strip_y = [xW, np.polyval(enr_line, intersect)]
strip_line = np.polyfit(strip_x, strip_y, 1)
plt.plot(strip_x, strip_y)

#Solve for and draw the number of stages
nstage = 0

while True:
	
	for x_index, x_frac in enumerate(x_sep):
		y_frac = y_sep[x_index]
		
		if y_frac >= y_current:
			plt.plot([x_sep[x_index], x_current], [y_current, y_current], 'k-')
			x_current = x_sep[x_index]
			break
	
	nstage += 1
	print(x_current)	
	if x_current < xW:
		break
	
	y_enr_check = np.polyval(enr_line, x_current)
	y_strip_check = np.polyval(strip_line, x_current)
	
		
	if y_enr_check < y_strip_check:
		plt.plot([x_current, x_current], [y_current, y_enr_check], 'k-')
		y_current = y_enr_check

	else:
		plt.plot([x_current, x_current], [y_current, y_strip_check], 'k-')
		y_current = y_strip_check


#Format outcoming plot then show it
plt.xlabel('Mole Fraction of Ethanol in Liquid', fontsize=18, fontname='Liberation Serif')
plt.ylabel('Mole Fraction of Ethanol in Vapor', fontsize=18, fontname='Liberation Serif')
plt.xticks(fontsize=15, fontname='Liberation Serif')
plt.yticks(fontsize=15, fontname='Liberation Serif')

plt.show()

nstage = math.ceil(nstage / 0.671)
print(nstage)

