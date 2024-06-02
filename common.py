import pandas as pd


def filter_char(df):
    return (df["p_char"] == "") & (df["char"] != "") & ~pd.isna(df["char"])


def filter_continent(df):
    return (
        (df["p_continent"] == "") & (df["continent"] != "") & ~pd.isna(df["continent"])
    )


def filter_period(df):
    return (df["p_period"] == "") & (df["period"] != "") & ~pd.isna(df["period"])


def filter_country(df):
    return (df["country"] != "") & ~pd.isna(df["country"])
