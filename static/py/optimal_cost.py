# ***************************************************************************
# * Distillation Column Calculation - optimal_cost.py
# * Spencer Wagner
# *
# * Holds functions for calculating costs of building a distillation column
# ***************************************************************************

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


