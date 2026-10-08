import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pre_proc import Spectra, read_spectra
from uv_spec import get_calibration_data, get_concentration

ROOT = Path(__file__).resolve().parents[1]


class ExportTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "spectra.csv"

    def export(self, rows, header=("Well", "Sample", "Dilution", "500", "534")):
        with self.path.open("w", encoding="utf-8-sig", newline="") as source:
            writer = csv.writer(source)
            writer.writerow(["User: USER"])
            writer.writerow([])
            writer.writerow(header)
            writer.writerows(rows)

    def test_interleaved_replicates_quoted_metadata_and_blank_subtraction(self):
        self.export(
            [
                ["A1", "sample, one\nreplicate", 2, 3, 7],
                ["A2", "sample two", 1, 5, 11],
                ["A3", "sample one", 2, 5, 9],
                ["A4", "sample two", 1, 7, 13],
                ["B1", "Blank", 1, 1, 2],
                ["B2", "Blank", 1, 3, 4],
                [],
                ["", "", "", "", ""],
            ]
        )
        simple = read_spectra(self.path, 2)
        normalized = read_spectra(self.path, 2, normalize=True)
        self.assertEqual(simple, Spectra((500, 534), {1: (6, 12), 2: (4, 8)}))
        self.assertEqual(normalized.samples, {1: (4, 9), 2: (2, 5)})
        self.assertEqual(list(simple.samples), [1, 2])

    def test_invalid_numeric_rows_report_file_and_line(self):
        for values in (
            [1, "", 2],
            [1, "NaN", 2],
            [1, "inf", 2],
            [0, 1, 2],
            [-1, 1, 2],
            [1, 2],
            [1, 2, 3, 4],
        ):
            with self.subTest(values=values):
                self.export([["A1", "sample", *values]])
                with self.assertRaisesRegex(ValueError, "spectra.csv: line 4:"):
                    read_spectra(self.path, 1)

    def test_invalid_headers(self):
        for wavelengths in ([], ["bad"], ["500", "500"], ["nan"], ["inf"], ["0"]):
            with self.subTest(wavelengths=wavelengths):
                self.export([], ["Well", "Sample", "Dilution", *wavelengths])
                with self.assertRaisesRegex(ValueError, "wavelengths"):
                    read_spectra(self.path, 1)
        self.path.write_text("metadata only\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing.*header"):
            read_spectra(self.path, 1)

    def test_invalid_repeats_and_no_samples(self):
        self.export([["B1", "Blank", 1, 1, 2]])
        for repeats in (-1, 0, 1, 2):
            with self.subTest(repeats=repeats), self.assertRaises(ValueError):
                read_spectra(self.path, repeats)

    def test_mixed_blank_dilutions_are_rejected_when_normalizing(self):
        self.export(
            [
                ["A1", "sample", 1, 5, 6],
                ["B1", "Blank", 1, 1, 2],
                ["B2", "Blank", 2, 1, 2],
            ]
        )
        with self.assertRaisesRegex(ValueError, "single dilution"):
            read_spectra(self.path, 2, normalize=True)


class CalibrationTests(unittest.TestCase):
    def test_regression_keeps_intercept_and_first_peak_on_ties(self):
        # y = 2x + 10. A fit forced through the origin would give another slope.
        calibration = Spectra((534, 500), {2: (60, 20), 1: (110, 110), 4: (35, 10)})
        slope, wavelength = get_calibration_data(calibration)
        self.assertAlmostEqual(slope, 2)
        self.assertEqual(wavelength, 534)
        # Resolve by wavelength, not by column position. Preserve label selection.
        sample = Spectra((500, 534), {1: (999, 30), 2: (999, 50), 8: (999, 999)})
        self.assertAlmostEqual(get_concentration(calibration, sample, 3), 20)

    def test_degenerate_calibrations(self):
        for samples in ({2: (5,)}, {1: (5,)}, {1: (5,), 2: (5,)}):
            with self.subTest(samples=samples), self.assertRaises(ValueError):
                get_calibration_data(Spectra((534,), samples))

    def test_missing_sample_wavelength_and_empty_selection(self):
        calibration = Spectra((534,), {1: (100,), 2: (50,)})
        with self.assertRaisesRegex(ValueError, "missing calibration wavelength"):
            get_concentration(calibration, Spectra((500,), {1: (20,)}), 3)
        with self.assertRaises(ValueError):
            get_concentration(calibration, Spectra((534,), {4: (20,)}), 3)

    def test_bundled_demo_matches_original_pandas_scipy_result(self):
        calibration = read_spectra(ROOT / "data/calibration.csv", 3, normalize=True)
        sample = read_spectra(ROOT / "data/sample.csv", 3)
        slope, wavelength = get_calibration_data(calibration)
        self.assertEqual(len(calibration.wavelengths), 291)
        self.assertEqual(len(calibration.samples), 8)
        self.assertEqual(wavelength, 534)
        self.assertAlmostEqual(slope, 0.03318958484834676, places=14)
        self.assertAlmostEqual(
            get_concentration(calibration, sample, 3), 45.66693658845705, places=11
        )


class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-S", str(ROOT / "uv_spec.py"), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_help_needs_no_third_party_packages(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--calibration-normalize", result.stdout)

    def test_bad_input_is_an_argparse_error_before_plotting(self):
        result = self.run_cli(
            "-c",
            str(ROOT / "data/calibration.csv"),
            "-s",
            str(ROOT / "data/sample.csv"),
            "-r",
            "0",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Number of replicates must be positive", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
