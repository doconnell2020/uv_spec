import plot_spec, pre_proc 

from matplotlib import pyplot as plt
import pandas as pd 
from scipy.stats import linregress
import sys 

#blank_required = input("Does this data require normalisation?\nYes[1], No[0]\n: ")

df = pd.read_csv("data/calibration.csv")
unknown_spl = pd.read_csv("data/sample.csv")

def get_calibration_data(df):
    procd_data = norm_samples(df).T
    max_idx = procd_data[[1]].idxmax().values[0]
    max_abs = procd_data.loc[max_idx].values
    conc = [50/i for i in procd_data.columns]
    slope = linregress(conc, max_abs)[0]
    return slope, max_idx


def main():
    #plot_spec.plot_spec(pre_proc.norm_samples(df))
    #plt.show()


    slope, max_idx = pre_proc.get_calibration_data(df)
    spl_df = pre_proc.restructure_data(unknown_spl)
    spl_abs_max = spl_df[max_idx][:3].mean()
    concentration = spl_abs_max/slope

    print("The unknown sample concentration is ", round(concentration, 1),"\u00B10.5mg")

if __name__ == '__main__':
    main()