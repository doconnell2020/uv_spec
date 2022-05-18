import plot_spec, pre_pros 

from matplotlib import pyplot as plt
import pandas as pd 
import sys 

#blank_required = input("Does this data require normalisation?\nYes[1], No[0]\n: ")

df = pd.read_csv("data/calibration.csv")



def main():
    
    
    
    plot_spec.plot(pre_pros.norm_samples(df))
    plt.show()

if __name__ == '__main__':
    main()