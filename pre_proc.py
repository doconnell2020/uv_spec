import pandas as pd


def restructure_data(df: pd.DataFrame) -> pd.DataFrame:
    # Remove unnecessary lines
    df = (
        df.copy()
        .dropna()
        .reset_index()
        .drop(["index", "User: USER", "Unnamed: 1"], axis=1)
    )
    df.columns = df.iloc[0]
    df = df.drop(0)
    # Cast all data to be float type for numerical operations
    return df.astype("float")


def blank_data(df: pd.DataFrame, num_repeats: int) -> pd.DataFrame:
    df = restructure_data(df)
    # Blanks are teh final three rows
    blanks = df.tail(num_repeats)
    return blanks.groupby(by="Dilution").mean()


def simple_samples(df: pd.DataFrame, num_repeats: int) -> pd.DataFrame:
    df = restructure_data(df)
    # The samples are all rows until the num_repeat final rows, which are blanks
    samples = df.iloc[:-num_repeats]
    return samples.groupby(by="Dilution").mean()


def norm_samples(df: pd.DataFrame, num_repeats: int) -> pd.DataFrame:
    return simple_samples(df, num_repeats).subtract(
        blank_data(df, num_repeats).values.squeeze()
    )
