import re
import pandas as pd

from config import REQUIRED_COLUMNS


# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

def clean_column_names(df):

    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


# =========================================================
# CLEAN AMOUNT
# =========================================================

def clean_amount(value):

    if pd.isna(value):
        return 0.0

    value = str(value).strip()

    if value == "":
        return 0.0

    value = (
        value
        .replace(",", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
    )

    value = re.sub(
        r"[^\d.\-]",
        "",
        value
    )

    try:
        return float(value)
    except ValueError:
        return 0.0


# =========================================================
# NORMALIZE MERCHANT
# =========================================================

def normalize_merchant(merchant):

    if pd.isna(merchant):
        return "Unknown Merchant"

    merchant = str(merchant).strip()

    if merchant == "":
        return "Unknown Merchant"

    upper = merchant.upper()

    # Remove reference numbers
    upper = re.sub(
        r"[*#@]\w+",
        "",
        upper
    )

    upper = re.sub(
        r"\b\d{4,}\b",
        "",
        upper
    )

    aliases = {

        "SWIGGY": "Swiggy",
        "SWG": "Swiggy",

        "ZOMATO": "Zomato",
        "ZMT": "Zomato",

        "UBER": "Uber",

        "OLA": "Ola",

        "AMZN": "Amazon",
        "AMAZON": "Amazon",

        "FLIPKART": "Flipkart",

        "NETFLIX": "Netflix",
        "NFLX": "Netflix",

        "SPOTIFY": "Spotify",

        "AIRTEL": "Airtel",

        "JIO": "Jio",

        "APOLLO PHARMACY": "Apollo Pharmacy",

        "BOOKMYSHOW": "BookMyShow",

        "PRIME VIDEO": "Prime Video",

        "COURSERA": "Coursera",

        "UDemy": "Udemy",

        "OPENAI": "OpenAI",

        "APPLE": "Apple"
    }

    for key, value in aliases.items():

        if key in upper:
            return value

    upper = upper.strip()

    if upper == "":
        return "Unknown Merchant"

    return upper.title()


# =========================================================
# CLEAN DATES
# =========================================================

def clean_dates(df):

    # IMPORTANT:
    # Do NOT use dayfirst=True here.
    # Your sample uses YYYY-MM-DD.

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
        format="mixed"
    )

    return df


# =========================================================
# CLEAN MERCHANTS
# =========================================================

def clean_merchants(df):

    df["Merchant"] = (
        df["Merchant"]
        .fillna("Unknown Merchant")
        .apply(normalize_merchant)
    )

    return df


# =========================================================
# CLEAN AMOUNTS
# =========================================================

def clean_amounts(df):

    df["Amount"] = (
        df["Amount"]
        .apply(clean_amount)
    )

    return df


# =========================================================
# CLEAN CURRENCY
# =========================================================

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


# =========================================================
# CLEAN MARKUP
# =========================================================

def clean_markup(df):

    if "Markup" not in df.columns:

        df["Markup"] = 0.0

    df["Markup"] = (
        df["Markup"]
        .apply(clean_amount)
    )

    return df


# =========================================================
# TRANSACTION TYPE
# =========================================================

def clean_transaction_type(df):

    if "Type" not in df.columns:

        df["Type"] = "DR"

    df["Type"] = (
        df["Type"]
        .fillna("DR")
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # Refund / credit transactions
    # are represented as negative amounts.

    for index in df.index:

        if df.at[index, "Type"] == "CR":

            amount = df.at[index, "Amount"]

            if amount > 0:

                df.at[index, "Amount"] = -amount

    return df


# =========================================================
# MAIN CLEAN FUNCTION
# =========================================================

def clean_data(df):

    # Make a copy
    df = df.copy()

    # -----------------------------------------------------
    # Count original rows
    # -----------------------------------------------------

    original_rows = len(df)

    # -----------------------------------------------------
    # Clean column names
    # -----------------------------------------------------

    df = clean_column_names(df)

    # -----------------------------------------------------
    # Check required columns
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Clean each column
    # -----------------------------------------------------

    df = clean_dates(df)

    df = clean_merchants(df)

    df = clean_amounts(df)

    df = clean_currency(df)

    df = clean_markup(df)

    df = clean_transaction_type(df)

    # -----------------------------------------------------
    # DO NOT DELETE TRANSACTIONS
    # -----------------------------------------------------

    # Keep every row from the uploaded statement.
    #
    # If a date is invalid, keep the row.
    # If an amount is invalid, it becomes 0.
    #
    # This prevents the cleaner from silently
    # removing valid transactions.

    # -----------------------------------------------------
    # Calculate total cost
    # -----------------------------------------------------

    df["Total_Cost"] = (
        df["Amount"]
        + df["Markup"]
    )

    # -----------------------------------------------------
    # Reset index
    # -----------------------------------------------------

    df = df.reset_index(
        drop=True
    )

    # -----------------------------------------------------
    # Store processing information
    # -----------------------------------------------------

    try:

        import streamlit as st

        st.session_state[
            "original_count"
        ] = original_rows

        st.session_state[
            "cleaned_count"
        ] = len(df)

    except Exception:
        pass

    return df