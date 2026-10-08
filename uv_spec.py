#!/usr/bin/env python3
import argparse
import csv
from datetime import date
from pathlib import Path
from statistics import fmean, linear_regression
from typing import TYPE_CHECKING

from pre_proc import Spectra, read_spectra

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def plot_spec(spectra: Spectra) -> "Axes":
    """Plot each dilution's spectrum; load the plotting stack only when needed."""
    from matplotlib import pyplot as plt

    _, axes = plt.subplots(figsize=(15, 9))
    for dilution, absorbances in spectra.samples.items():
        axes.plot(spectra.wavelengths, absorbances, label=f"{dilution:g}")
    axes.set(
        xlabel="Wavelength (nm)",
        ylabel="Absorbance (au)",
        title=f"Calibration Spectra {date.today()}",
    )
    axes.legend(title="Dilution")
    return axes


def get_calibration_data(spectra: Spectra) -> tuple[float, float]:
    """Fit absorbance against 50 / dilution at dilution 1's peak wavelength.

    Preserve the original ordinary least-squares fit (including its intercept),
    while returning only the slope used by the toy concentration calculation.
    Equal maxima select the first wavelength in file order.
    """
    try:
        reference = spectra.samples[1]
    except KeyError as exc:
        raise ValueError("Calibration requires a dilution 1 reference") from exc
    peak = max(range(len(reference)), key=reference.__getitem__)
    concentrations = [50 / dilution for dilution in spectra.samples]
    absorbances = [values[peak] for values in spectra.samples.values()]
    slope, _ = linear_regression(concentrations, absorbances)
    if slope == 0:
        raise ValueError("Calibration slope must be nonzero")
    return slope, spectra.wavelengths[peak]


def get_concentration(calibration: Spectra, sample: Spectra, num_repeats: int) -> float:
    """Preserve the original mean over sample dilution labels <= num_repeats."""
    slope, wavelength = get_calibration_data(calibration)
    try:
        peak = sample.wavelengths.index(wavelength)
    except ValueError as exc:
        raise ValueError(
            f"Sample is missing calibration wavelength {wavelength:g}"
        ) from exc
    absorbance = fmean(
        values[peak]
        for dilution, values in sample.samples.items()
        if dilution <= num_repeats
    )
    return absorbance / slope


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Process spectroscopy data for calibration and sample analysis."
    )

    parser.add_argument(
        "--calibration", "-c", type=Path, help="Path to calibration data CSV file"
    )
    parser.add_argument(
        "--sample", "-s", type=Path, help="Path to unknown sample data CSV file"
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
        data_dir = Path(__file__).resolve().parent / "data"
        calibration_path = data_dir / "calibration.csv"
        sample_path = data_dir / "sample.csv"
        cali_norm, spl_norm, num_repeats = True, False, 3
    else:
        if not args.calibration or not args.sample:
            parser.error(
                "Both calibration and sample files are required unless using --demo"
            )
        calibration_path, sample_path = args.calibration, args.sample
        cali_norm = args.calibration_normalize
        spl_norm = args.sample_normalize
        num_repeats = args.repeats

    try:
        calibration = read_spectra(calibration_path, num_repeats, normalize=cali_norm)
        sample = read_spectra(sample_path, num_repeats, normalize=spl_norm)
        concentration = get_concentration(calibration, sample, num_repeats)
    except (OSError, ValueError, csv.Error) as exc:
        parser.error(str(exc))

    plot_spec(calibration)
    from matplotlib import pyplot as plt

    plt.show()

    print(f"The unknown sample concentration is {round(concentration, 1)}\u00b10.5mg")


if __name__ == "__main__":
    main()
