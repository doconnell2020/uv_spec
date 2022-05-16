import pre_pros 

import pandas as pd 
import sys 

blank_required = input("Does this data require normalisation?\nYes[1], No[0]")

df = pd.read_csv("data/calibration.csv")


def main():
    if blank_required:
        pre_pros.norm_samples(df).T.plot(xlabel="Wavelength (nm)", ylabel="Absorbance (au)", title="Calibration Spectra", figsize=(15,9))

if __name__ == '__main__':
    main()