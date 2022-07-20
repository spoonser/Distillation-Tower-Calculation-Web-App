# Specifications for the design memo. Solves for costs, etc.

# Import the required python libraries: matplotlib for plotting, numpy to create arrays,
# pandas to import VLE data from ChemSep, and math for the ceiling function
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import math

#######################################
# Store important project variables

# Store important values for ethanol (A)
MW_A = 46.07  # lbm/lbmol
rho_A = 49.59  # lbm/ft^3

# Store important values for water (B)
MW_B = 18.02  # lbm/lbmol
rho_B = 62.16  # lbm/ft^3

# Store important feed (F) values
FA_vol_perc = 0.13  # Volume percent

# Store important distillate (D) values
D_rate = 48000  # lbm/day
D_rate_3yrs = 48000 * 360 * 3  # lbm/3yrs
DA_vol_perc = 0.95  # Volume percent`

# Store important bottoms (W) values
WA_wt_perc = 0.03  # Weight percent

# Store the value for tray efficiency
tray_efficiency = 0.671


#######################################

################################################################
# Section to solve for the mole fractions and specified distillate, bottoms, and feed flow rates

# Function to solve for the mole fraction given volume percent
def vol_to_mol(vol_perc, rho_A, rho_B, MW_A, MW_B):
    vol_A = vol_perc
    vol_B = (1 - vol_perc)

    mol_A = vol_A * rho_A / MW_A
    mol_B = vol_B * rho_B / MW_B

    total_mol = mol_A + mol_B

    mol_perc_A = mol_A / total_mol
    return mol_perc_A


# Function to solve for mole fraction given mass percent
def mass_to_mol(mass_perc, MW_A, MW_B):
    mol_A = mass_perc / MW_A
    mol_B = (1 - mass_perc) / MW_B

    total_mol = mol_A + mol_B

    mol_perc_A = mol_A / total_mol
    return mol_perc_A


# Store mole percentage of ethanol in D, W and F
xD = vol_to_mol(DA_vol_perc, rho_A, rho_B, MW_A, MW_B)
zF = vol_to_mol(FA_vol_perc, rho_A, rho_B, MW_A, MW_B)
xW = mass_to_mol(WA_wt_perc, MW_A, MW_B)

# Solve for D, F, and W
D = D_rate / (MW_A * xD + MW_B * (1 - xD)) / 24  # lbmol/hr
W = D * (zF - xD) / (xW - zF)  # lbmol/hr
F = D + W  # lbmol/hr
###################################################################

###################################################################
# Section to solve for q

# Store heat capacity, heat of vaporization of ethanol & water, TF & TB
CP_A = 0.548 * MW_A  # BTU/lbmolF
CP_B = 1 * MW_B  # BTU/lbmolF
Hvap = 17000  # BTU/lbmol
TF = 140  # Degrees F
TB = 197.3  # Degrees F

# Solve for q and generate the qline, plot it
q = 1 + (zF * CP_A + (1 - zF) * CP_B) * (TB - TF) / Hvap
q_pntx = [zF, zF + 0.025]
q_pnty = [zF, q / (q - 1) * (zF + 0.025) - zF / (q - 1)]
q_line = np.polyfit(q_pntx, q_pnty, 1)


# plt.plot(q_pntx, q_pnty, 'g-')

###################################################################

####################################################################
# Functions for calculating the costs of various parts of the tower

# Tray price for carbon steel sieve trays & one mist eliminator
def tray_price(nstage):
    ntrays = nstage - 1

    if ntrays < 20 and ntrays > 9:
        price = 1.2 * 4750.53 * (ntrays + 0.8333)

    else:
        valve_factor = 1.2
        price = valve_factor * 3167.02 * (ntrays + 0.8333)

    return price


# Tower Shell price as a function of trays
def shell_price(nstage):
    ntrays = nstage - 1

    price = 39187.47 * (0.60 * ntrays) ** 0.87

    return price


# Extra HX for feed preheating cost
def feed_HX_price(TF, F, zF, CP_A, CP_B, Hvap):
    if TF <= 86.0:
        price = 0
        G_cond = 0

    else:
        Q_HX = F * (CP_A * zF + CP_B * (1 - zF)) * (TF - 86.0)

        delta_T1 = 173.1 - TF
        delta_T2 = 173.1 - 86
        delta_Tlm = (delta_T1 - delta_T2) / (np.log((delta_T1 / delta_T2)))

        area = Q_HX / (100 * delta_Tlm)

        G_cond = Q_HX / Hvap
        cost_scaling = (535.5 / 355) * 5
        price = cost_scaling * 10000 * (Q_HX / (625 * 100 * delta_Tlm)) ** 0.7

    return G_cond, price


# Reboiler price (and heat load)
def reboiler_price(D, F, R, q, Hvap, Tw):
    Tw = (Tw - 273.15) * (9 / 5) + 32

    DTLM = 365.86 - Tw

    G_bar = (q - 1) * F + D * (R + 1)  # lbmol/hr
    Q_reboiler = G_bar * Hvap  # BTU/hr
    cost_scaling = (535.5 / 355) * 5

    area = Q_reboiler / (100 * DTLM)

    price = cost_scaling * 10000 * (area / 625) ** 0.7  # Dollars

    return Q_reboiler, price


# Condenser price (and heat load)
def condenser_price(D, G_cond, R, Hvap):
    G = D * (R + 1) - G_cond  # lbmol/hr
    Q_condenser = G * Hvap  # BTU/hr

    area = Q_condenser / (44 * 68.1)

    cost_scaling = (535.5 / 355) * 5

    price = cost_scaling * 10000 * (Q_condenser / 1872750) ** 0.7  # Dollars

    return Q_condenser, price


# Steam price (over 3 years)
def steam_price(Q_reboiler):
    # Shourly = (Q_reboiler/858.09)
    # dailyprice = Shourly*24*(5/1000)

    S = ((Q_reboiler * 24 * 360 * 3) / 858.09)  # lbm/3yrs
    price = S * (5 / 1000)  # Dollars/3yrs

    return price


# Cooling water price (over 3 years)
def cooling_water_price(Q_condenser):
    # CW_hourly = Q_condenser/(1 * 35)
    # daily_price = CW_hourly*24*0.000012

    CW = (Q_condenser * 24 * 360 * 3) / (1 * 35)  # lb/3yrs

    price = CW * 0.000012  # Dollars/3yrs

    return price


# Feed price (over 3 years)
def feed_price(F, zF, MW_A, MW_B):
    F_lb = (F * 24 * 360 * 3) * (zF * MW_A + (1 - zF) * MW_B)

    price = F_lb * 0.020  # Dollars/3yrs

    return price


###################################################################

###################################################################
# Import VLE  data from ChemSep
VLE_Data = pd.read_csv('EthanolVLE_5000pts.csv')
VLE_Data = VLE_Data.values

x_sep = VLE_Data[:, 0]
y_sep = VLE_Data[:, 1]
T_sep = VLE_Data[:, 2]

# Plot the ChemSep Data
# plt.plot(x_sep, y_sep)
# plt.plot(x_sep, x_sep)
# plt.xlim([0, 1])
# plt.ylim([0, 1])
# plt.show()
####################################################################

###################################################################
# McCabe-Thiele method for calculating ideal number of trays, and calculations for cost
# at various R

# Store a variety of R values to be tested, and initialize empty cost arrays, number of stages
R = np.linspace(2.8, 10, 100)
capital_cost_at_R = []
operational_cost_at_R = []
break_even_cost_at_R = []
nstages_at_R = []

# Series of loops that take the R values, calculates the number of ideal stages, and returns cost
for R_value in R:

    # Initialize the current points for mole fractions of ethanol in vapor and water phase
    # reset xW from previous loop
    x_current = xD
    y_current = xD
    xW = mass_to_mol(WA_wt_perc, MW_A, MW_B)

    # Solve for the enriching line, find the intersection point, and re-solve for the
    # two enriching line points
    enr_x = [0, xD]
    enr_y = [xD / (R_value + 1), xD]
    enr_line = np.polyfit(enr_x, enr_y, 1)

    intersection = np.roots(q_line - enr_line)

    enr_x = [intersection, xD]
    enr_y = [np.polyval(enr_line, intersection), xD]

    # Solve for the stripping line given the intersection point
    strip_x = [xW, intersection]
    strip_y = [xW, np.polyval(enr_line, intersection)]
    strip_line = np.polyfit(strip_x, strip_y, 1)

    # Solve for the number of stages, first initialize number of stages
    nstage = 0

    while True:

        for x_index, x_frac in enumerate(x_sep):
            y_frac = y_sep[x_index]

            if y_frac >= y_current:
                x_current = x_sep[x_index]
                T_bot = T_sep[x_index]

                break

        nstage += 1
        if x_current < xW:
            break

        y_enr_check = np.polyval(enr_line, x_current)
        y_strip_check = np.polyval(strip_line, x_current)

        if y_enr_check < y_strip_check:
            y_current = y_enr_check

        else:
            y_current = y_strip_check

    # Store the value for the composition at the bottom of the tower
    # and re-solve for W and F (bottoms and feed flow rate)
    # xW = x_current
    # W = D*(zF - xD) / (xW - zF)	#lbmol/hr
    # F = D + W

    # Store the number of stages by dividing by tray efficiency in the nstage_at_R array
    nstages_real = math.ceil(nstage / tray_efficiency)
    nstages_at_R.append(nstages_real)

    # Solve for costs related to the distillation tower at each R value
    tray_cost = tray_price(nstages_real)
    shell_cost = shell_price(nstages_real)
    G_condensed, feed_HX_cost = feed_HX_price(TF, F, zF, CP_A, CP_B, Hvap)
    Q_reboiler, reboiler_cost = reboiler_price(D, F, R_value, q, Hvap, T_bot)
    Q_condenser, condenser_cost = condenser_price(D, G_condensed, R_value, Hvap)
    steam_cost = steam_price(Q_reboiler)
    cooling_water_cost = cooling_water_price(Q_condenser)
    feed_cost = feed_price(F, zF, MW_A, MW_B)

    # Solve for capital and operational costs over 3 years, divided by the total
    # distillate produced and multiplied by 1000 for units of $/1000 lb distillate
    capital_cost = (tray_cost + shell_cost + reboiler_cost + condenser_cost + \
                    feed_HX_cost) / (D_rate_3yrs / 1000)  # $/1000lb distallate
    operational_cost = (steam_cost + cooling_water_cost + feed_cost) \
                       / (D_rate_3yrs / 1000)  # $/1000lb distillate

    total_break_even_cost = capital_cost + operational_cost  # $/1000lb distillate

    # Store capital, operational, and total cost in respective lists
    capital_cost_at_R.append(capital_cost)
    operational_cost_at_R.append(operational_cost)
    break_even_cost_at_R.append(total_break_even_cost)

# Find the minimum cost and the R associated with that cost, print value
minimum_break_even = min(break_even_cost_at_R)
R_at_min_cost = (R[break_even_cost_at_R.index(minimum_break_even)])
nstages_at_min_cost = (nstages_at_R[break_even_cost_at_R.index(minimum_break_even)])
print('Minimum R = ', R_at_min_cost)
print('Minimum break even cost = ', minimum_break_even)

# Plot Capital, Operational, and Total break even cost
plt.plot(R, capital_cost_at_R, label='Capital Break Even Cost')
plt.plot(R, operational_cost_at_R, label='Operational Break Even Cost')
plt.plot(R, break_even_cost_at_R, label='Total Break Even Cost')
plt.xlim([2.8, 10])
plt.ylim([0, 500])

# Format plot axes and legend
plt.rc('font', family='Liberation Serif')
plt.legend(fontsize=12)
plt.xlabel('Reflux Ratio, R', fontsize=18, fontname='Liberation Serif')
plt.ylabel(r'Break Even Cost   [$ per 1000 lb of Distillate]', fontsize=18, fontname= \
    'Liberation Serif')
plt.xticks(fontsize=15, fontname='Liberation Serif')
plt.yticks(fontsize=15, fontname='Liberation Serif')
plt.show()
