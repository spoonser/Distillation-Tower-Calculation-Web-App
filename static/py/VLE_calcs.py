# ***************************************************************************
# * Distillation Column Calculation - VLE_graph.py 
# * Spencer Wagner
# *
# * Functions for calculting the vapor-liquid equilibrium data for a given
# * system, returned data is used for graphing, build costs, and heat duty
# ***************************************************************************


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
 