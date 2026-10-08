# UV Spec

## Overview

A simple commandline tool that takes some calibration data and an unknown
sample file and returns the spectra plot of the calibration data and
the concentration of the unknown sample.

The tool takes the form

```bash
    uv run uv_spec.py -c data.csv -s sample.csv -cn -r 5
```

Use `-cn` and/or `-sn` to enable calibration or sample normalisation
(blank subtraction). `-r` specifies the number of trailing blank replicates.

## Installation

To install and see a demo, run the following:

```bash
    git clone https://github.com/doconnell2020/uv_spec.git

    cd uv_spec

    uv run ./uv_spec.py --demo    
```

The `--demo` option uses the bundled data files relative to the script, so it
also works when invoked from another directory.

## Python's standard library

The analysis uses `csv.reader` for the instrument export, `collections.defaultdict`
for interleaved replicate groups, `statistics.fmean` for their column means, and
`statistics.linear_regression` for the calibration slope. `zip(..., strict=True)`
keeps paired spectra from silently losing columns. A small `Spectra` dataclass
carries wavelength labels alongside the dilution-to-absorbance mapping.
Matplotlib and its Qt backend remain for the plot; pandas and SciPy are no longer
needed. Importing the analysis or asking for `--help` does not load the plotting stack.

This applies the principle in [Nolan Lawson's “use the platform” article](https://nolanlawson.com/2026/10/03/why-dont-more-developers-use-the-platform/)
to this small dataset. Python already provides [CSV parsing](https://docs.python.org/3.11/library/csv.html)
and [simple linear regression](https://docs.python.org/3.11/library/statistics.html#statistics.linear_regression).

The input format is a CLARIOstar CSV export: optional metadata, then a
`Well,Sample,Dilution,<wavelengths...>` header. The final `-r` nonempty rows are
blanks. Samples are averaged by dilution, in sorted dilution order. Wavelengths
must be unique, positive numbers; dilutions must be positive; all measurements
must be finite. Empty lines are ignored; incomplete or malformed measurement
rows raise an error instead of silently disappearing. Blank subtraction requires
one blank dilution group.

The toy calculation is unchanged: find the first maximum of dilution 1, fit
absorbance against `50 / dilution` with an intercept, then divide mean sample
absorbance by the slope. As before, that sample mean includes dilution labels
less than or equal to `-r`; this is a label cutoff, not a replicate count.
The bundled demo prints `45.7±0.5mg`.

The internal DataFrame-based preprocessing helpers have been replaced by
`read_spectra(Path(...), repeats, normalize=True)` returning `Spectra`.
`plot_spec` and `get_calibration_data` now accept that object.

## Tests

The numerical and CLI tests run without any third-party packages (`-S` disables
site packages):

```bash
python3 -S -m unittest discover -s tests -v
```

To exercise the complete demo without opening a window:

```bash
MPLBACKEND=Agg uv run uv_spec.py --demo
```

## Disclaimer

This is a toy project intended for technical assessment purposes. Not for production or real lab use.