import pandas as pd
import numpy as np

VLE_Data = pd.read_csv('EthanolVLE_5000pts.csv')
VLE_Data = VLE_Data.values

x_sep = VLE_Data[:, 0]
y_sep = VLE_Data[:, 1]
for x in y_sep:
	print(x)


