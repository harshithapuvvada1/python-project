import re
import pandas as pd

from config import REQUIRED_COLUMNS


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

def clean_column_names(df):

    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


# ============================================================
# CLEAN AMOUNT
# ============================================================

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


# ============================================================
# NORMALIZE MERCHANT
# ============================================================

def normalize_merchant(merchant):

    if pd.isna(merchant):
        return "Unknown Merchant"

    merchant = str(merchant).strip()

    if merchant == "":
        return "Unknown Merchant"

    upper = merchant.upper()

    # Remove transaction/reference numbers
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

    # ========================================================
    # MERCHANT ALIASES
    # ========================================================

    aliases = {

        # ----------------------------------------------------
        # SHOPPING
        # ----------------------------------------------------

        "AMAZON": "Amazon",
        "AMZN": "Amazon",
        "FLIPKART": "Flipkart",
        "ZARA": "Zara",
        "APPLE": "Apple",

        # ----------------------------------------------------
        # FOOD
        # ----------------------------------------------------

        "SWIGGY": "Swiggy",
        "ZOMATO": "Zomato",
        "BLINKIT": "Blinkit",
        "ZEPTO": "Zepto",
        "DOMINOS": "Dominos",
        "STARBUCKS": "Starbucks",
        "MCDONALD": "McDonald's",

        # ----------------------------------------------------
        # TRANSPORT
        # ----------------------------------------------------

        "UBER": "Uber",
        "OLA": "Ola",
        "SHELL": "Shell",

        # ----------------------------------------------------
        # ENTERTAINMENT
        # ----------------------------------------------------

        "NETFLIX": "Netflix",
        "SPOTIFY": "Spotify",
        "PRIME VIDEO": "Prime Video",
        "BOOKMYSHOW": "BookMyShow",

        # ----------------------------------------------------
        # BILLS
        # ----------------------------------------------------

        "AIRTEL": "Airtel",
        "JIO": "Jio",
        "BESCOM": "BESCOM",

        # ----------------------------------------------------
        # HEALTH
        # ----------------------------------------------------

        "APOLLO PHARMACY": "Apollo Pharmacy",
        "APOLLO HOSPITAL": "Apollo Hospital",
        "PHARMACY": "Pharmacy",

        # ----------------------------------------------------
        # EDUCATION
        # ----------------------------------------------------

        "COURSERA": "Coursera",
        "UDEMY": "Udemy",

        # ----------------------------------------------------
        # TRAVEL
        # ----------------------------------------------------

        "BOOKING.COM": "Booking.com",
        "BOOKING COM": "Booking.com",
        "HOTEL BOOKING": "Hotel Booking",

        # ----------------------------------------------------
        # AI / SOFTWARE
        # ----------------------------------------------------

        "OPENAI": "OpenAI",

        # ----------------------------------------------------
        # FOREIGN MARKUP
        # ----------------------------------------------------

        "FOREIGN TRANSACTION MARKUP":
            "Foreign Transaction Markup",

        "FOREIGN EXCHANGE MARKUP":
            "Foreign Exchange Markup"
    }

    # ========================================================
    # FIND MERCHANT MATCH
    # ========================================================

    for key, value in aliases.items():

        if key in upper:
            return value

    # ========================================================
    # DEFAULT CLEANING
    # ========================================================

    upper = upper.strip()

    if upper == "":
        return "Unknown Merchant"

    return upper.title()


# ============================================================
# CLEAN DATES
# ============================================================

def clean_dates(df):

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
        format="mixed"
    )

    return df


# ============================================================
# CLEAN MERCHANTS
# ============================================================

def clean_merchants(df):

    df["Merchant"] = (
        df["Merchant"]
        .fillna("Unknown Merchant")
        .apply(normalize_merchant)
    )

    return df


# ============================================================
# CLEAN AMOUNTS
# ============================================================

def clean_amounts(df):

    df["Amount"] = (
        df["Amount"]
        .apply(clean_amount)
    )

    return df


# ============================================================
# CLEAN CURRENCY
# ============================================================

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


# ============================================================
# CLEAN MARKUP
# ============================================================

def clean_markup(df):

    if "Markup" not in df.columns:

        df["Markup"] = 0.0

    df["Markup"] = (
        df["Markup"]
        .apply(clean_amount)
    )

    return df


# ============================================================
# CLEAN TRANSACTION TYPE
# ============================================================

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

    for index in df.index:

        if df.at[index, "Type"] == "CR":

            amount = df.at[
                index,
                "Amount"
            ]

            if amount > 0:

                df.at[
                    index,
                    "Amount"
                ] = -amount

    return df


# ============================================================
# MAIN CLEANING FUNCTION
# ============================================================

def clean_data(df):

    df = df.copy()

    # --------------------------------------------------------
    # ORIGINAL ROW COUNT
    # --------------------------------------------------------

    original_rows = len(df)

    # --------------------------------------------------------
    # COLUMN NAMES
    # --------------------------------------------------------

    df = clean_column_names(df)

    # --------------------------------------------------------
    # CHECK REQUIRED COLUMNS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CLEAN DATE
    # --------------------------------------------------------

    df = clean_dates(df)

    # --------------------------------------------------------
    # CLEAN MERCHANT
    # --------------------------------------------------------

    df = clean_merchants(df)

    # --------------------------------------------------------
    # CLEAN AMOUNT
    # --------------------------------------------------------

    df = clean_amounts(df)

    # --------------------------------------------------------
    # CLEAN CURRENCY
    # --------------------------------------------------------

    df = clean_currency(df)

    # --------------------------------------------------------
    # CLEAN MARKUP
    # --------------------------------------------------------

    df = clean_markup(df)

    # --------------------------------------------------------
    # CLEAN TRANSACTION TYPE
    # --------------------------------------------------------

    df = clean_transaction_type(df)

    # --------------------------------------------------------
    # CALCULATE TOTAL COST
    # --------------------------------------------------------

    df["Total_Cost"] = (
        df["Amount"] +
        df["Markup"]
    )

    # --------------------------------------------------------
    # RESET INDEX
    # --------------------------------------------------------

    df = df.reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # STREAMLIT SESSION INFORMATION
    # --------------------------------------------------------

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