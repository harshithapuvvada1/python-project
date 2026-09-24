import re

import pandas as pd

from config import REQUIRED_COLUMNS


# =========================================================
# COLUMN CLEANING
# =========================================================

def clean_column_names(df):

    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


# =========================================================
# AMOUNT CLEANING
# =========================================================

def clean_amount(value):

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    # Remove currency symbols and commas
    value = (
        value
        .replace(",", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
    )

    # Keep numbers, decimal point and minus
    value = re.sub(
        r"[^\d.\-]",
        "",
        value
    )

    try:
        return float(value)

    except ValueError:
        return None


# =========================================================
# MERCHANT NORMALIZATION
# =========================================================

def normalize_merchant(merchant):

    merchant = str(
        merchant
    ).strip()

    if merchant == "":
        return "Unknown Merchant"

    upper = merchant.upper()

    # Remove transaction/reference codes
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

    # -----------------------------------------------------
    # Known merchant aliases
    # -----------------------------------------------------

    aliases = {

        # Food
        "SWG": "Swiggy",
        "SWIGGY": "Swiggy",

        "ZMT": "Zomato",
        "ZOMATO": "Zomato",

        "STRBKS": "Starbucks",
        "STARBUCKS": "Starbucks",

        "MCDONALD": "McDonald's",

        "DOMINOS": "Dominos",

        # Transport
        "UBER": "Uber",
        "OLA CABS": "Ola",
        "OLA": "Ola",

        "SHELL PETROL": "Shell",

        # Shopping
        "AMZN": "Amazon",
        "AMAZON": "Amazon",

        "FLIPKART": "Flipkart",

        "ZARA": "Zara",

        # Subscriptions
        "NFLX": "Netflix",
        "NETFLIX": "Netflix",

        "SPOTIFY": "Spotify",

        "APPLE.COM": "Apple",

        "OPENAI": "OpenAI",

        # Bills
        "AIRTEL": "Airtel",

        "BESCOM": "BESCOM",

        # Grocery
        "BLINKIT": "Blinkit",

        "ZEPTO": "Zepto",

        # Health
        "APOLLO PHARMACY": "Apollo Pharmacy"
    }

    for key, value in aliases.items():

        if key in upper:

            return value

    upper = upper.strip()

    if upper == "":
        return "Unknown Merchant"

    return upper.title()


# =========================================================
# DATE CLEANING
# =========================================================

def clean_dates(df):

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
        dayfirst=True
    )

    return df


# =========================================================
# MERCHANT CLEANING
# =========================================================

def clean_merchants(df):

    df["Merchant"] = (
        df["Merchant"]
        .fillna("Unknown Merchant")
        .apply(normalize_merchant)
    )

    return df


# =========================================================
# AMOUNT CLEANING
# =========================================================

def clean_amounts(df):

    df["Amount"] = (
        df["Amount"]
        .apply(clean_amount)
    )

    return df


# =========================================================
# CURRENCY
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

    # Detect USD transactions from merchant description
    if "Merchant" in df.columns:

        for index in df.index:

            merchant = str(
                df.at[index, "Merchant"]
            ).upper()

            if (
                "USD" in merchant
                or "APPLE.COM/BILL" in merchant
                or "OPENAI" in merchant
            ):

                # Only infer foreign currency where
                # currency wasn't explicitly supplied
                if df.at[index, "Currency"] == "INR":

                    if (
                        "APPLE" in merchant
                        or "OPENAI" in merchant
                    ):

                        df.at[
                            index,
                            "Currency"
                        ] = "USD"

    return df


# =========================================================
# MARKUP CLEANING
# =========================================================

def clean_markup(df):

    if "Markup" not in df.columns:

        df["Markup"] = 0.0

    df["Markup"] = (
        df["Markup"]
        .apply(clean_amount)
        .fillna(0.0)
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

    # Credit/refund transactions become negative
    for index in df.index:

        if df.at[index, "Type"] == "CR":

            amount = df.at[
                index,
                "Amount"
            ]

            if (
                amount is not None
                and amount > 0
            ):

                df.at[
                    index,
                    "Amount"
                ] = -amount

    return df


# =========================================================
# MARKUP / IGST ROW DETECTION
# =========================================================

def is_markup_row(merchant):

    merchant = str(
        merchant
    ).lower()

    keywords = [

        "markup",
        "mark up",
        "forex fee",
        "foreign exchange fee",
        "foreign exchange markup",
        "fcy markup",
        "currency conversion fee",
        "igst on forex",
        "igst on fcy",
        "igst @"
    ]

    return any(
        keyword in merchant
        for keyword in keywords
    )


# =========================================================
# COMBINE MARKUP AND IGST ROWS
# =========================================================

def combine_markup_rows(df):

    df = df.copy()

    if "Markup" not in df.columns:

        df["Markup"] = 0.0

    rows_to_remove = []

    last_transaction_index = None

    for index in df.index:

        merchant = str(
            df.at[index, "Merchant"]
        )

        amount = df.at[
            index,
            "Amount"
        ]

        if pd.isna(amount):

            continue

        # ---------------------------------------------
        # Markup / IGST row
        # ---------------------------------------------

        if is_markup_row(merchant):

            if last_transaction_index is not None:

                df.at[
                    last_transaction_index,
                    "Markup"
                ] += abs(float(amount))

                rows_to_remove.append(index)

            continue

        # ---------------------------------------------
        # Normal transaction
        # ---------------------------------------------

        last_transaction_index = index

    df = df.drop(
        rows_to_remove
    )

    return df.reset_index(
        drop=True
    )


# =========================================================
# MAIN CLEANING FUNCTION
# =========================================================

def clean_data(df):

    # -----------------------------------------------------
    # 1. Column names
    # -----------------------------------------------------

    df = clean_column_names(df)

    # -----------------------------------------------------
    # 2. Check required columns
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
    # 3. Date
    # -----------------------------------------------------

    df = clean_dates(df)

    # -----------------------------------------------------
    # 4. Merchant
    # -----------------------------------------------------

    df = clean_merchants(df)

    # -----------------------------------------------------
    # 5. Amount
    # -----------------------------------------------------

    df = clean_amounts(df)

    # -----------------------------------------------------
    # 6. Currency
    # -----------------------------------------------------

    df = clean_currency(df)

    # -----------------------------------------------------
    # 7. Markup
    # -----------------------------------------------------

    df = clean_markup(df)

    # -----------------------------------------------------
    # 8. Transaction type
    # -----------------------------------------------------

    df = clean_transaction_type(df)

    # -----------------------------------------------------
    # 9. Combine markup / IGST rows
    # -----------------------------------------------------

    df = combine_markup_rows(df)

    # -----------------------------------------------------
    # 10. Remove invalid dates/amounts
    # -----------------------------------------------------

    df = df.dropna(
        subset=[
            "Date",
            "Amount"
        ]
    )

    # -----------------------------------------------------
    # 11. Calculate total cost
    # -----------------------------------------------------

    df["Total_Cost"] = (
        df["Amount"]
        + df["Markup"]
    )

    return df.reset_index(
        drop=True
    )