#Code for testing the costs for reboiler based on temperature
#Import needed Python libraries
from matplotlib import pyplot as plt
import numpy as np
import math

#######################################
#Store important values for ethanol (A)
MW_A = 46.07	#lbm/lbmol
rho_A = 49.59	#lbm/ft^3

#Store important values for water (B)
MW_B = 18.02	#lbm/lbmol
rho_B = 62.16	#lbm/ft^3


#Store important feed (F) values
FA_vol_perc = 0.13	#Volume percent

#Store important distillate (D) values
D_rate = 48000	#lbm/day
D_rate_3yrs = 48000*360*3	#lbm/3yrs
DA_vol_perc = 0.95	#Volume percent`

#Store important bottoms (W) values
WA_wt_perc = 0.03	#Weight percent

#Store the value for tray efficiency
tray_efficiency = 0.65
#######################################

################################################################
#Section to solve for the mole fractions and specified distillate, bottoms, and feed flow rates

#Function to solve for the mole fraction given volume percent
def vol_to_mol(vol_perc, rho_A, rho_B, MW_A, MW_B):
	
	vol_A = vol_perc
	vol_B = (1 - vol_perc)

	mol_A = vol_A*rho_A / MW_A
	mol_B = vol_B*rho_B / MW_B

	total_mol = mol_A + mol_B

	mol_perc_A = mol_A / total_mol
	return mol_perc_A

#Function to solve for mole fraction given mass percent
def mass_to_mol(mass_perc, MW_A, MW_B):
	
    mol_A = mass_perc / MW_A
    mol_B = (1 - mass_perc) / MW_B
    total_mol = mol_A + mol_B

    mol_perc_A = mol_A / total_mol
    return mol_perc_A
 
#Store mole percentage of ethanol in D, W and F
xD = vol_to_mol(DA_vol_perc, rho_A, rho_B, MW_A, MW_B)
zF = vol_to_mol(FA_vol_perc, rho_A, rho_B, MW_A, MW_B)
xW = mass_to_mol(WA_wt_perc, MW_A, MW_B)

#Solve for D, F, and W
D = D_rate / (MW_A*xD + MW_B*(1 - xD)) / 24 #lbmol/hr
W = D*(zF - xD) /  (xW - zF)    #lbmol/hr
F = D + W   #lbmol/hr
###################################################################

###################################################################
#Section to solve for q
 
#Store heat capacity, heat of vaporization of ethanol & water, TF & TB
CP_A = 0.548*MW_A   #BTU/lbmolF
CP_B = 1*MW_B       #BTU/lbmolF
Hvap = 17000    #BTU/lbmol
TB = 197.3  #Degrees F
 
#Function to solve for q
def q_val(zF, CP_A, CP_B, TB, TS):
	
	q = 1 + (zF*CP_A + (1 - zF)*CP_B)*(TB - TS) / Hvap

	return q

#Cost of the feed HX
def feed_HX_price(TS, F, zF, CP_A, CP_B):
	
	if TS <= 86:
		price = 0
	
	else:
		Q_HX = F*(CP_A*zF + CP_B*(1 - zF))*(TS - 86.0)

		delta_T1 = 173.1 - TS
		delta_T2 = 173.1 - 86
		delta_Tlm = (delta_T1 - delta_T2) / (np.log((delta_T1 / delta_T2)))

		price = 10000 * (Q_HX / (625 * 100 * delta_Tlm))**0.7

	return price

#Function to solve for Q_condenser	
def reboiler_price(D, F, R, q, Hvap):
 
	G_bar = (q - 1)*F + D*(R + 1)   #lbmol/hr
	Q_reboiler = G_bar * Hvap   #BTU/hr 

	price = 10000*(Q_reboiler / 9978750)**0.7

	return Q_reboiler, price

 #Condenser price (and heat load)
def condenser_price(D, R, Hvap):
	 
    G = D*(R + 1)   #lbmol/hr
    Q_condenser = G * Hvap  #BTU/hr

    price = 10000*(Q_condenser / 1822425)**0.7
 
    return Q_condenser, price
 
 
#Steam price (over 3 years)
def steam_price(Q_reboiler):
 
    S = (Q_reboiler*24*360*3 / 858.09)  #lbm/3yrs

    price  = S * (5 / 1000) #Dollars/3yrs

    return price
 
 
#Cooling water price (over 3 years)
def cooling_water_price(Q_condenser, CP_B):

    CW = (Q_condenser*24*360*3) / (CP_B * 35)   #lb/3yrs

    price = CW * 0.012  #Dollars/3yrs

    return price
 

#Feed price (over 3 years)
def feed_price(F, zF, MW_A, MW_B):

	F_lb = (F*24*360*3)*(zF*MW_A + (1 - zF)*MW_B)

	price = F_lb * 0.020    #Dollars/3yrs

	return price


def tray_price(nstage):

    ntrays = nstage - 1

    if ntrays < 20 and ntrays > 9:
        price = 1.2 * 4750.53*(ntrays + 0.8333)

    else:
        price = 1.2 * 3167.02*(ntrays + 0.8333)

    return price


#Tower Shell price
def shell_price(nstage):

    ntrays = nstage - 1

    price = 39187.47*(0.60*ntrays)**0.87

    return price



######################################################
#Generate a series of TS from 86 to 173 (in fahrenheit)
TS = np.linspace(86, 173, 1000)

#Store base case R, cost arrays at T
R = 4
operational_cost_at_T = []
capital_cost_at_T = []
break_even_cost_at_T = []


#Loop through the TS to calculate the costs for the tower
for temp in TS:

	q = q_val(zF, CP_A, CP_B, TB, temp)
	tray_cost = tray_price(40)
	shell_cost = shell_price(40)
	Q_reboiler, reboiler_cost = reboiler_price(D, F, R, q, Hvap)
	Q_condenser, condenser_cost = condenser_price(D, R, Hvap)
	steam_cost = steam_price(Q_reboiler)
	cooling_water_cost = cooling_water_price(Q_condenser, CP_B)
	feed_cost = feed_price(F, zF, MW_A, MW_B)
	feed_HX_cost = feed_HX_price(temp, F, zF, CP_A, CP_B)

	#Calculate costs
	capital_cost = (tray_cost + shell_cost + reboiler_cost + condenser_cost + \
					feed_HX_cost) / D_rate_3yrs * 1000

	operational_cost = (steam_cost + cooling_water_cost + feed_cost) \
						/ D_rate_3yrs * 1000

	total_break_even_cost = capital_cost + operational_cost

	capital_cost_at_T.append(capital_cost)
	operational_cost_at_T.append(operational_cost)
	break_even_cost_at_T.append(total_break_even_cost)

#Find the minimum cost and the T associated with that cost
minimum_break_even = min(break_even_cost_at_T)
T_at_min_cost = (TS[break_even_cost_at_T.index(minimum_break_even)])
print(T_at_min_cost)

#plt.plot(TS, capital_cost_at_T, label='Capital Break Even Cost')
#plt.plot(TS, operational_cost_at_T, label='Operational Break Even Cost')
plt.plot(TS, break_even_cost_at_T, label='Total Break Even Cost')
plt.xlim([165, 173])
plt.ylim([300, 310])
plt.legend()
plt.show() 

