import pandas as pd


def process_microbatch(df: pd.DataFrame):

    df["accelerometer-total"] = df["accelerometer-x"].abs() + df["accelerometer-y"].abs() + df["accelerometer-z"].abs()

    return df