def plot(df):
    return df.copy().T.plot(xlabel="Wavelength (nm)", ylabel="Absorbance (au)", title="Calibration Spectra", figsize=(15,9))