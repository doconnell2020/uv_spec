import plot_spec, pre_pros 

from matplotlib import pyplot as plt
import pandas as pd 
from scipy.stats import linregress
import sys 

#blank_required = input("Does this data require normalisation?\nYes[1], No[0]\n: ")

df = pd.read_csv("data/calibration.csv")

def calibrate(df):
    procd_data = pre_pros.norm_samples(df).T
    max_idx = procd_data[[1]].idxmax().values[0]
    max_abs = procd_data.loc[max_idx].values
    conc = [50/i for i in procd_data.columns]
    slope = linregress(conc, max_abs)[0]
    





def main():
    
    
    
    plot_spec.plot(pre_pros.norm_samples(df))
    plt.show()

if __name__ == '__main__':
    main()