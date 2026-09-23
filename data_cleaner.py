import re

import pandas as pd

from config import REQUIRED_COLUMNS


# ---------------------------------------------------------
# COLUMN CLEANING
# ---------------------------------------------------------

def clean_column_names(df):

    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


# ---------------------------------------------------------
# AMOUNT CLEANING
# ---------------------------------------------------------

def clean_amount(value):

    if pd.isna(value):

        return None

    value = str(value)

    value = (
        value
        .replace(",", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
        .strip()
    )

    value = re.sub(
        r"[^\d.\-]",
        "",
        value
    )

    try:

        return float(value)

    except ValueError:

        return None


# ---------------------------------------------------------
# MERCHANT NORMALIZATION
# ---------------------------------------------------------

def normalize_merchant(merchant):

    merchant = str(merchant)

    merchant = merchant.upper()

    # Remove common transaction codes
    merchant = re.sub(
        r"[*#@]\w+",
        "",
        merchant
    )

    merchant = re.sub(
        r"\b\d{4,}\b",
        "",
        merchant
    )

    # Known merchant aliases
    aliases = {

        "AMZN": "Amazon",
        "AMZN MKT": "Amazon",
        "AMZN MKTP": "Amazon",
        "AMAZON INDIA": "Amazon",
        "AMAZON IN": "Amazon",

        "SWIGGY INSTAMART": "Swiggy",
        "SWIGGY ORDER": "Swiggy",

        "ZOMATO ORDER": "Zomato",

        "UBER INDIA": "Uber",

        "OLA CABS": "Ola",

        "NETFLIX.COM": "Netflix",

        "SPOTIFY P": "Spotify",

        "AIRTEL MOBILE": "Airtel",

        "JIO MOBILE": "Jio"
    }

    for key, value in aliases.items():

        if key in merchant:

            return value

    merchant = merchant.strip()

    if merchant == "":

        return "Unknown Merchant"

    return merchant.title()


# ---------------------------------------------------------
# DATE CLEANING
# ---------------------------------------------------------

def clean_dates(df):

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    return df


# ---------------------------------------------------------
# MERCHANT CLEANING
# ---------------------------------------------------------

def clean_merchants(df):

    df["Merchant"] = (
        df["Merchant"]
        .fillna("Unknown Merchant")
        .apply(normalize_merchant)
    )

    return df


# ---------------------------------------------------------
# AMOUNT CLEANING
# ---------------------------------------------------------

def clean_amounts(df):

    df["Amount"] = (
        df["Amount"]
        .apply(clean_amount)
    )

    return df


# ---------------------------------------------------------
# CURRENCY
# ---------------------------------------------------------

def clean_currency(df):

    if "Currency" not in df.columns:

        df["Currency"] = "INR"

    df["Currency"] = (
        df["Currency"]
        .fillna("INR")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    return df


# ---------------------------------------------------------
# MARKUP
# ---------------------------------------------------------

def clean_markup(df):

    if "Markup" not in df.columns:

        df["Markup"] = 0.0

    df["Markup"] = (
        df["Markup"]
        .apply(clean_amount)
        .fillna(0.0)
    )

    return df


# ---------------------------------------------------------
# SEPARATE MARKUP ROW DETECTION
# ---------------------------------------------------------

def combine_markup_rows(df):

    df = df.copy()

    if "Markup" not in df.columns:

        df["Markup"] = 0.0

    rows_to_remove = []

    for index in range(len(df)):

        merchant = str(
            df.iloc[index]["Merchant"]
        ).lower()

        is_markup = any(
            word in merchant
            for word in [
                "markup",
                "mark up",
                "forex fee",
                "foreign exchange fee",
                "currency conversion fee"
            ]
        )

        if not is_markup:
            continue

        amount = df.iloc[index]["Amount"]

        # Attach markup to previous transaction
        if index > 0:

            previous_index = df.index[index - 1]

            df.at[
                previous_index,
                "Markup"
            ] += amount

            rows_to_remove.append(
                df.index[index]
            )

    df = df.drop(
        rows_to_remove
    )

    return df.reset_index(
        drop=True
    )


# ---------------------------------------------------------
# MAIN CLEANING FUNCTION
# ---------------------------------------------------------

def clean_data(df):

    df = clean_column_names(df)

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )

    df = clean_dates(df)

    df = clean_merchants(df)

    df = clean_amounts(df)

    df = clean_currency(df)

    df = clean_markup(df)

    df = combine_markup_rows(df)

    df = df.dropna(
        subset=[
            "Date",
            "Amount"
        ]
    )

    df = df[
        df["Amount"] >= 0
    ]

    df["Total_Cost"] = (
        df["Amount"]
        + df["Markup"]
    )

    return df.reset_index(
        drop=True
    )