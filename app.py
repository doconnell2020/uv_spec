#!/usr/bin/env python3
import os
import io
import pre_proc
import pandas as pd
from scipy.stats import linregress
import base64
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def plot_spec(df: pd.DataFrame) -> str:
    """Generate plot and return as base64 encoded string"""
    import matplotlib

    matplotlib.use("Agg")  # Use non-interactive backend

    ax = df.copy().T.plot(
        xlabel="Wavelength (nm)",
        ylabel="Absorbance (au)",
        title="Calibration Spectra",
        figsize=(15, 9),
    )

    # Save plot to memory
    buf = io.BytesIO()
    ax.figure.savefig(buf, format="png")
    buf.seek(0)

    # Convert to base64 string
    plot_data = base64.b64encode(buf.getvalue()).decode("utf-8")
    return plot_data


def get_calibration_data(df: pd.DataFrame) -> tuple:
    """Extract calibration data from the dataframe"""
    procd_data = df.T
    max_idx = procd_data[[1]].idxmax().values[0]
    max_abs = procd_data.loc[max_idx].values
    conc = [50 / i for i in procd_data.columns]
    slope = linregress(conc, max_abs)[0]
    return slope, max_idx


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Main analysis endpoint"""
    # Check if files were uploaded
    if "calibration" not in request.files or "sample" not in request.files:
        return jsonify({"error": "Both calibration and sample files are required"}), 400

    # Get uploaded files
    calibration_file = request.files["calibration"]
    sample_file = request.files["sample"]

    # Save files temporarily
    calibration_path = os.path.join(UPLOAD_FOLDER, calibration_file.filename)
    sample_path = os.path.join(UPLOAD_FOLDER, sample_file.filename)
    calibration_file.save(calibration_path)
    sample_file.save(sample_path)

    # Read parameters from form data
    cali_norm = request.form.get("calibration_normalize", "false").lower() == "true"
    spl_norm = request.form.get("sample_normalize", "false").lower() == "true"
    num_repeats = int(request.form.get("repeats", "3"))

    # Load data
    calib_df = pd.read_csv(calibration_path)
    spl_df = pd.read_csv(sample_path)

    # Process data
    if cali_norm:
        calib_df = pre_proc.norm_samples(calib_df, num_repeats)
    else:
        calib_df = pre_proc.simple_samples(calib_df, num_repeats)

    if spl_norm:
        spl_df = pre_proc.norm_samples(spl_df, num_repeats)
    else:
        spl_df = pre_proc.simple_samples(spl_df, num_repeats)

    # Generate plot as base64
    plot_data = plot_spec(calib_df)

    # Calculate concentration
    slope, max_idx = get_calibration_data(calib_df)
    spl_abs_max = spl_df[max_idx].loc[:num_repeats].mean()
    concentration = spl_abs_max / slope

    # Clean up temporary files
    os.remove(calibration_path)
    os.remove(sample_path)

    # Return results
    return jsonify(
        {
            "concentration": round(concentration, 1),
            "uncertainty": 0.5,
            "plot": plot_data,
            "max_wavelength": max_idx,
            "calibration_slope": slope,
        }
    )


@app.route("/api/demo", methods=["GET"])
def demo():
    """Demo endpoint using default files"""
    try:
        # Load demo data
        calib_df = pd.read_csv("data/calibration.csv")
        spl_df = pd.read_csv("data/sample.csv")

        # Process data
        calib_df = pre_proc.norm_samples(calib_df, 3)  # normalized calibration
        spl_df = pre_proc.simple_samples(spl_df, 3)  # non-normalized sample

        # Generate plot
        plot_data = plot_spec(calib_df)

        # Calculate concentration
        slope, max_idx = get_calibration_data(calib_df)
        spl_abs_max = spl_df[max_idx].loc[:3].mean()
        concentration = spl_abs_max / slope

        # Return results
        return jsonify(
            {
                "concentration": round(concentration, 1),
                "uncertainty": 0.5,
                "plot": plot_data,
                "max_wavelength": max_idx,
                "calibration_slope": slope,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Demo error: {str(e)}"}), 500


@app.route("/", methods=["GET"])
def home():
    """Home page with basic API info"""
    return jsonify(
        {
            "api": "Spectroscopy Analysis API",
            "version": "1.0",
            "endpoints": {
                "/api/analyze": "POST - Upload calibration and sample files for analysis",
                "/api/demo": "GET - Run demo with default data",
            },
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
