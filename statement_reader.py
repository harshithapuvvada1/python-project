import re
import io
import pandas as pd
import pdfplumber


# =========================================================
# CSV READER
# =========================================================

def read_csv(file):
    return pd.read_csv(file)


# =========================================================
# FIND HEADER ROW
# =========================================================

def find_header_row(rows):
    for index, row in enumerate(rows):

        text = " ".join(
            str(value).lower()
            for value in row
            if value is not None
        )

        if (
            "date" in text
            and (
                "amount" in text
                or "transaction" in text
                or "description" in text
                or "merchant" in text
            )
        ):
            return index

    return None


# =========================================================
# TABLE ROWS TO DATAFRAME
# =========================================================

def table_rows_to_dataframe(table):

    if not table:
        return pd.DataFrame()

    header_index = find_header_row(table)

    if header_index is None:
        return pd.DataFrame()

    header = table[header_index]
    data = table[header_index + 1:]

    cleaned_header = []

    for column in header:

        if column is None:
            cleaned_header.append("")
        else:
            cleaned_header.append(
                str(column).strip()
            )

    # Remove completely empty column names
    for i, column in enumerate(cleaned_header):

        if column == "":
            cleaned_header[i] = f"Column_{i}"

    try:
        df = pd.DataFrame(
            data,
            columns=cleaned_header
        )
    except Exception:
        return pd.DataFrame()

    return df


# =========================================================
# STANDARDIZE PDF COLUMNS
# =========================================================

def standardize_pdf_columns(df):

    if df.empty:
        return df

    new_columns = {}

    for column in df.columns:

        name = str(column).strip().lower()

        if name in [
            "date",
            "transaction date",
            "txn date"
        ]:
            new_columns[column] = "Date"

        elif name in [
            "transaction details",
            "transaction detail",
            "description",
            "merchant",
            "details"
        ]:
            new_columns[column] = "Merchant"

        elif name in [
            "amount",
            "amount (inr)",
            "amount(inr)",
            "transaction amount",
            "debit",
            "credit"
        ]:
            new_columns[column] = "Amount"

        elif name in [
            "currency",
            "curr"
        ]:
            new_columns[column] = "Currency"

        elif name in [
            "markup",
            "foreign markup"
        ]:
            new_columns[column] = "Markup"

        elif name in [
            "type",
            "transaction type",
            "dr/cr"
        ]:
            new_columns[column] = "Type"

    df = df.rename(
        columns=new_columns
    )

    return df


# =========================================================
# DETECT CURRENCY
# =========================================================

def detect_currency(merchant):

    text = str(merchant).upper()

    # USD
    if re.search(r"\bUSD\b", text):
        return "USD"

    # EUR
    if re.search(r"\bEUR\b", text):
        return "EUR"

    # GBP
    if re.search(r"\bGBP\b", text):
        return "GBP"

    # AED
    if re.search(r"\bAED\b", text):
        return "AED"

    # SGD
    if re.search(r"\bSGD\b", text):
        return "SGD"

    # AUD
    if re.search(r"\bAUD\b", text):
        return "AUD"

    # CAD
    if re.search(r"\bCAD\b", text):
        return "CAD"

    # JPY
    if re.search(r"\bJPY\b", text):
        return "JPY"

    # Default
    return "INR"


# =========================================================
# DETECT TRANSACTION TYPE
# =========================================================

def detect_type(merchant):

    text = str(merchant).upper()

    if re.search(r"\bCR\b", text):
        return "CR"

    return "DR"


# =========================================================
# CLEAN PDF DATAFRAME
# =========================================================

def clean_pdf_dataframe(df):

    if df.empty:
        return df

    # Standardize columns
    df = standardize_pdf_columns(df)

    # Required columns
    if "Date" not in df.columns:
        return pd.DataFrame()

    if "Merchant" not in df.columns:
        return pd.DataFrame()

    if "Amount" not in df.columns:
        return pd.DataFrame()

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
        dayfirst=True
    )

    # -----------------------------------------------------
    # MERCHANT
    # -----------------------------------------------------

    df["Merchant"] = (
        df["Merchant"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # -----------------------------------------------------
    # AMOUNT
    # -----------------------------------------------------

    df["Amount"] = (
        df["Amount"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.strip()
    )

    df["Amount"] = pd.to_numeric(
        df["Amount"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # CURRENCY
    # -----------------------------------------------------

    if "Currency" not in df.columns:

        df["Currency"] = df["Merchant"].apply(
            detect_currency
        )

    else:

        df["Currency"] = df.apply(
            lambda row: (
                detect_currency(
                    row["Merchant"]
                )
                if str(
                    row["Currency"]
                ).strip() == ""
                else str(
                    row["Currency"]
                ).upper().strip()
            ),
            axis=1
        )

    # -----------------------------------------------------
    # TRANSACTION TYPE
    # -----------------------------------------------------

    if "Type" not in df.columns:

        df["Type"] = df["Merchant"].apply(
            detect_type
        )

    else:

        df["Type"] = (
            df["Type"]
            .fillna("DR")
            .astype(str)
            .str.upper()
            .str.strip()
        )

    # -----------------------------------------------------
    # MARKUP
    # -----------------------------------------------------

    if "Markup" not in df.columns:

        df["Markup"] = 0.0

    else:

        df["Markup"] = (
            df["Markup"]
            .astype(str)
            .str.replace(
                ",",
                "",
                regex=False
            )
            .str.replace(
                "₹",
                "",
                regex=False
            )
        )

        df["Markup"] = pd.to_numeric(
            df["Markup"],
            errors="coerce"
        ).fillna(0.0)

    # -----------------------------------------------------
    # REFUNDS
    # -----------------------------------------------------

    for index in df.index:

        merchant = str(
            df.at[index, "Merchant"]
        ).upper()

        transaction_type = str(
            df.at[index, "Type"]
        ).upper()

        # Credit transaction
        if transaction_type == "CR":

            amount = df.at[
                index,
                "Amount"
            ]

            if (
                pd.notna(amount)
                and amount > 0
            ):
                df.at[
                    index,
                    "Amount"
                ] = -amount

        # Refund mentioned in description
        elif "REFUND" in merchant:

            amount = df.at[
                index,
                "Amount"
            ]

            if (
                pd.notna(amount)
                and amount > 0
            ):
                df.at[
                    index,
                    "Amount"
                ] = -amount

            df.at[
                index,
                "Type"
            ] = "CR"

    # -----------------------------------------------------
    # MARKUP / FOREX / IGST ARE INR
    # -----------------------------------------------------

    for index in df.index:

        merchant = str(
            df.at[index, "Merchant"]
        ).upper()

        if (
            "MARKUP" in merchant
            or "FCY" in merchant
            or "FOREX" in merchant
            or "IGST" in merchant
        ):

            df.at[
                index,
                "Currency"
            ] = "INR"

    # -----------------------------------------------------
    # REMOVE INVALID ROWS
    # -----------------------------------------------------

    df = df.dropna(
        subset=[
            "Date",
            "Amount"
        ]
    )

    df = df.reset_index(
        drop=True
    )

    return df


# =========================================================
# EXTRACT PDF TABLES
# =========================================================

def extract_pdf_tables(file):

    try:

        file_bytes = file.getvalue()

        tables = []

        with pdfplumber.open(
            io.BytesIO(file_bytes)
        ) as pdf:

            for page in pdf.pages:

                page_tables = (
                    page.extract_tables()
                )

                for table in page_tables:

                    df = (
                        table_rows_to_dataframe(
                            table
                        )
                    )

                    if not df.empty:
                        tables.append(df)

        if not tables:
            return pd.DataFrame()

        combined = pd.concat(
            tables,
            ignore_index=True
        )

        combined = clean_pdf_dataframe(
            combined
        )

        return combined

    except Exception:

        return pd.DataFrame()


# =========================================================
# EXTRACT PDF TEXT
# =========================================================

def extract_pdf_text(file):

    file_bytes = file.getvalue()

    text_parts = []

    with pdfplumber.open(
        io.BytesIO(file_bytes)
    ) as pdf:

        for page in pdf.pages:

            page_text = (
                page.extract_text()
            )

            if page_text:
                text_parts.append(
                    page_text
                )

    return "\n".join(
        text_parts
    )


# =========================================================
# PARSE PDF TEXT
# =========================================================

def parse_pdf_text(text):

    rows = []

    if not text:
        return pd.DataFrame()

    lines = text.splitlines()

    # Example:
    #
    # 15/02/2026 APPLE.COM/BILL USD 19.99 @ 84.50 1,689.15 DR
    #
    # 20/02/2026 OPENAI *CHATGPT SUBSCRIPTION USD 20.00 1,690.00 DR

    date_pattern = re.compile(
        r"^(\d{2}[/-]\d{2}[/-]\d{4})\s+(.*)$"
    )

    for line in lines:

        line = line.strip()

        match = date_pattern.match(
            line
        )

        if not match:
            continue

        date_text = match.group(1)

        transaction_text = (
            match.group(2).strip()
        )

        # -------------------------------------------------
        # TRANSACTION TYPE
        # -------------------------------------------------

        transaction_type = "DR"

        if re.search(
            r"\sCR$",
            transaction_text,
            re.IGNORECASE
        ):

            transaction_type = "CR"

            transaction_text = re.sub(
                r"\sCR$",
                "",
                transaction_text,
                flags=re.IGNORECASE
            ).strip()

        elif re.search(
            r"\sDR$",
            transaction_text,
            re.IGNORECASE
        ):

            transaction_text = re.sub(
                r"\sDR$",
                "",
                transaction_text,
                flags=re.IGNORECASE
            ).strip()

        # -------------------------------------------------
        # DETECT CURRENCY
        # -------------------------------------------------

        currency = detect_currency(
            transaction_text
        )

        # -------------------------------------------------
        # FIND MONEY VALUES
        # -------------------------------------------------

        money_values = re.findall(
            r"(?<!\d)\d[\d,]*\.\d{2}(?!\d)",
            transaction_text
        )

        if not money_values:
            continue

        # Last amount is the INR transaction value
        amount_text = money_values[-1]

        amount = float(
            amount_text.replace(
                ",",
                ""
            )
        )

        # -------------------------------------------------
        # REFUND
        # -------------------------------------------------

        if transaction_type == "CR":

            amount = -abs(
                amount
            )

        if (
            "REFUND"
            in transaction_text.upper()
            and amount > 0
        ):

            amount = -amount

            transaction_type = "CR"

        # -------------------------------------------------
        # MARKUP / FOREX / IGST
        # -------------------------------------------------

        upper_text = (
            transaction_text.upper()
        )

        if (
            "MARKUP" in upper_text
            or "FCY" in upper_text
            or "FOREX" in upper_text
            or "IGST" in upper_text
        ):

            currency = "INR"

        # -------------------------------------------------
        # ADD ROW
        # -------------------------------------------------

        rows.append(
            {
                "Date": date_text,
                "Merchant": transaction_text,
                "Amount": amount,
                "Currency": currency,
                "Markup": 0.0,
                "Type": transaction_type
            }
        )

    df = pd.DataFrame(
        rows
    )

    if df.empty:
        return df

    return clean_pdf_dataframe(
        df
    )


# =========================================================
# READ PDF
# =========================================================

def read_pdf(file):

    # -----------------------------------------------------
    # FIRST TRY TABLE EXTRACTION
    # -----------------------------------------------------

    df = extract_pdf_tables(
        file
    )

    if not df.empty:

        # Make sure currency is detected
        if "Currency" not in df.columns:

            df["Currency"] = (
                df["Merchant"]
                .apply(
                    detect_currency
                )
            )

        else:

            df["Currency"] = df.apply(
                lambda row: (
                    detect_currency(
                        row["Merchant"]
                    )
                    if str(
                        row["Currency"]
                    ).strip() == ""
                    else str(
                        row["Currency"]
                    ).upper().strip()
                ),
                axis=1
            )

        # Force forex/markup/IGST rows to INR
        for index in df.index:

            merchant = str(
                df.at[
                    index,
                    "Merchant"
                ]
            ).upper()

            if (
                "MARKUP" in merchant
                or "FCY" in merchant
                or "FOREX" in merchant
                or "IGST" in merchant
            ):

                df.at[
                    index,
                    "Currency"
                ] = "INR"

        return clean_pdf_dataframe(
            df
        )

    # -----------------------------------------------------
    # TABLE EXTRACTION FAILED
    # USE TEXT EXTRACTION
    # -----------------------------------------------------

    text = extract_pdf_text(
        file
    )

    df = parse_pdf_text(
        text
    )

    if df.empty:

        raise ValueError(
            "No transactions were found in the PDF."
        )

    return df


# =========================================================
# READ STATEMENT
# =========================================================

def read_statement(file):

    filename = getattr(
        file,
        "name",
        ""
    ).lower()

    if filename.endswith(
        ".csv"
    ):

        return read_csv(
            file
        )

    elif filename.endswith(
        ".pdf"
    ):

        return read_pdf(
            file
        )

    else:

        raise ValueError(
            "Unsupported file type. "
            "Please upload a CSV or PDF."
        )