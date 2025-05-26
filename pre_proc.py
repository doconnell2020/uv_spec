import pandas as pd


def restructure_data(df: pd.DataFrame) -> pd.DataFrame:
    """Restructure the incoming data for further processing.

    Args:
        df: The raw dataframe read from the original input files.

    Returns:
        The restructured dataframe, cast as float type for numerical operations.

    """
    df = (
        df.copy()
        .dropna()
        .reset_index()
        .drop(["index", "User: USER", "Unnamed: 1"], axis=1)
    )
    df.columns = df.iloc[0]  # Make row column labels
    df = df.drop(0)  # Drop row of column labels
    return df.astype("float")


def blank_data(df: pd.DataFrame, num_repeats: int) -> pd.DataFrame:
    """Creates a separate DataFrame of the blank (control) samples.

    Samples are returned as a DataFrame, grouped by the Dilution column. Dilution acts as
    an identifier for distinct samples from the spectrophotometer.

    Args:
        df:  The preprocessed data from the raw input data.
        num_repeats: The number of replicate samples.

    Returns:
        The blank data dataframe.
    """
    df = restructure_data(df.copy())
    # Blanks are the final rows
    blanks = df.tail(num_repeats)
    return blanks.groupby(by="Dilution").mean()


def simple_samples(df: pd.DataFrame, num_repeats: int) -> pd.DataFrame:
    """Process the data in a simple case without blank subtraction.

    Samples are returned as a DataFrame, grouped by the Dilution column. Dilution acts as
    an identifier for distinct samples from the spectrophotometer.

    Args:
        df: Raw input dataframe.
        num_repeats: The number of replicate samples.

    Returns:
        The processed data, grouped by "Dilution".
    """
    df = restructure_data(df.copy())
    # The samples are all rows until the num_repeat final rows, which are blanks
    samples = df.iloc[:-num_repeats]
    return samples.groupby(by="Dilution").mean()


def norm_samples(df: pd.DataFrame, num_repeats: int) -> pd.DataFrame:
    """Process the data, normalising with blank subtraction.

    Samples are returned as a DataFrame, grouped by the Dilution column. Dilution acts as
    an identifier for distinct samples from the spectrophotometer.

    Args:
        df: Raw input dataframe.
        num_repeats: The number of replicate samples.

    Returns:
        The processed data, grouped by "Dilution".
    """
    return simple_samples(df.copy(), num_repeats).subtract(
        blank_data(df, num_repeats).values.squeeze()
    )
