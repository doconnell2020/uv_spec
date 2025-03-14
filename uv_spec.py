#!/usr/bin/env python3
import argparse
import sys

import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import linregress

import pre_proc


# Plot spectra
def plot_spec(df: pd.DataFrame) -> plt.axes:
    return df.copy().T.plot(
        xlabel="Wavelength (nm)",
        ylabel="Absorbance (au)",
        title="Calibration Spectra",
        figsize=(15, 9),
    )


def get_calibration_data(df: pd.DataFrame) -> tuple:
    procd_data = df.T
    max_idx = procd_data[[1]].idxmax().values[0]
    max_abs = procd_data.loc[max_idx].values
    conc = [50 / i for i in procd_data.columns]
    slope = linregress(conc, max_abs)[0]
    return slope, max_idx


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Process spectroscopy data for calibration and sample analysis."
    )

    parser.add_argument(
        "--calibration", "-c", type=str, help="Path to calibration data CSV file"
    )
    parser.add_argument(
        "--sample", "-s", type=str, help="Path to unknown sample data CSV file"
    )
    parser.add_argument(
        "--calibration-normalize",
        "-cn",
        action="store_true",
        help="Normalize the calibration data",
    )
    parser.add_argument(
        "--sample-normalize",
        "-sn",
        action="store_true",
        help="Normalize the sample data",
    )
    parser.add_argument(
        "--repeats",
        "-r",
        type=int,
        default=3,
        help="Number of replicates performed (default: 3)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demonstration mode with default files",
    )

    args = parser.parse_args()

    if args.demo:
        calib_df = pd.read_csv("data/calibration.csv")
        spl_df = pd.read_csv("data/sample.csv")
        cali_norm = True
        spl_norm = False
        num_repeats = 3
    else:
        if not args.calibration or not args.sample:
            parser.error(
                "Both calibration and sample files are required unless using --demo"
            )

        calib_df = pd.read_csv(args.calibration)
        spl_df = pd.read_csv(args.sample)
        cali_norm = args.calibration_normalize
        spl_norm = args.sample_normalize
        num_repeats = args.repeats

    if cali_norm:
        calib_df = pre_proc.norm_samples(calib_df, num_repeats)
    else:
        calib_df = pre_proc.simple_samples(calib_df, num_repeats)

    if spl_norm:
        spl_df = pre_proc.norm_samples(spl_df, num_repeats)
    else:
        spl_df = pre_proc.simple_samples(spl_df, num_repeats)

    # Plot and analyze
    plot_spec(calib_df)
    plt.show()

    slope, max_idx = get_calibration_data(calib_df)
    spl_abs_max = spl_df[max_idx].loc[:num_repeats].mean()
    concentration = spl_abs_max / slope

    print(f"The unknown sample concentration is {round(concentration, 1)}\u00b10.5mg")


if __name__ == "__main__":
    main()
