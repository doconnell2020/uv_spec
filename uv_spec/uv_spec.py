import pre_proc

from matplotlib import pyplot as plt
import pandas as pd
from scipy.stats import linregress
import sys

cali_norm = input("Does the calibration file require normalisation?\nYes[Y], No[N]\n: ")
sample_norm = input(
    "Does the unknown sample file require normalisation?\nYes[Y], No[N]\n: "
)

df = pd.read_csv("data/calibration.csv")
unknown_spl = pd.read_csv("data/sample.csv")


def plot_spec(df):
    return df.copy().T.plot(
        xlabel="Wavelength (nm)",
        ylabel="Absorbance (au)",
        title="Calibration Spectra",
        figsize=(15, 9),
    )


def get_calibration_data(df):
    procd_data = df.T
    max_idx = procd_data[[1]].idxmax().values[0]
    max_abs = procd_data.loc[max_idx].values
    conc = [50 / i for i in procd_data.columns]
    slope = linregress(conc, max_abs)[0]
    return slope, max_idx


def main():
    if cali_norm.lower() == "y":
        calib_df = pre_proc.norm_samples(df)
    else:
        calib_df = pre_proc.simple_samples(df)

    if sample_norm.lower() == "y":
        spl_df = pre_proc.norm_samples(unknown_spl)
    else:
        spl_df = pre_proc.simple_samples(unknown_spl)

    plot_spec(calib_df)
    plt.show()

    slope, max_idx = get_calibration_data(calib_df)
    spl_abs_max = spl_df[max_idx][:3].mean()
    concentration = spl_abs_max / slope

    print(
        "The unknown sample concentration is ", round(concentration, 1), "\u00B10.5mg"
    )


if __name__ == "__main__":
    main()
