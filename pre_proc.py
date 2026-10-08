"""Read CLARIOstar exports and average spectra using the standard library."""

import csv
from collections import defaultdict
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from statistics import fmean


@dataclass
class Spectra:
    """Wavelengths in file order and averaged absorbances keyed by dilution."""

    wavelengths: tuple[float, ...]
    samples: dict[float, tuple[float, ...]]


def read_spectra(path: Path, num_repeats: int, *, normalize: bool = False) -> Spectra:
    """Read an export, excluding its final ``num_repeats`` blank rows.

    Replicates need not be adjacent: dilution identifies a sample. If requested,
    subtract the mean blank spectrum from each sample's mean spectrum.
    """
    if num_repeats < 1:
        raise ValueError("Number of replicates must be positive")

    # newline='' lets csv handle quoted newlines; utf-8-sig accepts BOM exports.
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        header = next(
            (row for row in reader if row[:3] == ["Well", "Sample", "Dilution"]),
            None,
        )
        if header is None:
            raise ValueError(f"{path}: missing Well,Sample,Dilution header")
        try:
            wavelengths = tuple(map(float, header[3:]))
        except ValueError as exc:
            raise ValueError(f"{path}: wavelengths must be numeric") from exc
        if (
            not wavelengths
            or not all(isfinite(w) and w > 0 for w in wavelengths)
            or len(set(wavelengths)) != len(wavelengths)
        ):
            raise ValueError(f"{path}: wavelengths must be unique, finite and positive")

        rows = []
        for row in reader:
            if not any(field.strip() for field in row):
                continue
            try:
                if len(row) != len(header):
                    raise ValueError(f"expected {len(header)} columns, got {len(row)}")
                values = tuple(map(float, row[2:]))
                if not all(map(isfinite, values)) or values[0] <= 0:
                    raise ValueError(
                        "values must be finite and dilution must be positive"
                    )
            except ValueError as exc:
                raise ValueError(f"{path}: line {reader.line_num}: {exc}") from exc
            rows.append(values)

    if len(rows) <= num_repeats:
        raise ValueError(
            f"{path}: need sample rows before the final {num_repeats} blanks"
        )

    groups = defaultdict(list)
    for dilution, *absorbances in rows[:-num_repeats]:
        groups[dilution].append(absorbances)
    samples = {
        dilution: tuple(map(fmean, zip(*groups[dilution], strict=True)))
        for dilution in sorted(groups)
    }
    if normalize:
        blanks = rows[-num_repeats:]
        if len({row[0] for row in blanks}) != 1:
            raise ValueError(f"{path}: blank rows must have a single dilution")
        blank_mean = tuple(map(fmean, zip(*(row[1:] for row in blanks), strict=True)))
        samples = {
            dilution: tuple(a - b for a, b in zip(values, blank_mean, strict=True))
            for dilution, values in samples.items()
        }
    return Spectra(wavelengths, samples)
