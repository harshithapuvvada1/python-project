import re
import io
import pandas as pd
import pdfplumber


# =========================================================
# CSV READER
# =========================================================

def read_csv(file):

    try:
        df = pd.read_csv(file)

        if df.empty:
            raise ValueError("The CSV file is empty.")

        return df

    except Exception as e:
        raise ValueError(f"Unable to read CSV file: {e}")


# =========================================================
# PDF TABLE READER
# =========================================================

def extract_pdf_tables(file):

    tables_data = []

    file_bytes = file.getvalue()

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                if not table:
                    continue

                for row in table:

                    if row:
                        cleaned_row = [
                            str(cell).strip() if cell is not None else ""
                            for cell in row
                        ]

                        tables_data.append(cleaned_row)

    return tables_data


# =========================================================
# FIND HEADER ROW
# =========================================================

def find_header_row(rows):

    for index, row in enumerate(rows):

        text = " ".join(
            str(cell).lower()
            for cell in row
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
# CONVERT TABLE TO DATAFRAME
# =========================================================

def table_rows_to_dataframe(rows):

    if not rows:
        return None

    header_index = find_header_row(rows)

    if header_index is None:
        return None

    headers = rows[header_index]

    data_rows = rows[header_index + 1:]

    if not data_rows:
        return None

    max_columns = len(headers)

    cleaned_rows = []

    for row in data_rows:

        if len(row) < max_columns:
            row = row + [""] * (max_columns - len(row))

        elif len(row) > max_columns:
            row = row[:max_columns]

        cleaned_rows.append(row)

    df = pd.DataFrame(
        cleaned_rows,
        columns=headers
    )

    return df


# =========================================================
# STANDARDIZE PDF COLUMNS
# =========================================================

def standardize_pdf_columns(df):

    if df is None or df.empty:
        return None

    # Clean column names
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    column_mapping = {}

    for column in df.columns:

        lower = column.lower().strip()

        # Date
        if lower in [
            "date",
            "transaction date",
            "txn date",
            "trans date",
            "posting date"
        ]:
            column_mapping[column] = "Date"

        # Merchant / description
        elif lower in [
            "merchant",
            "description",
            "transaction",
            "transaction description",
            "merchant description",
            "details",
            "particulars"
        ]:
            column_mapping[column] = "Merchant"

        # Amount
        elif lower in [
            "amount",
            "transaction amount",
            "txn amount",
            "debit",
            "purchase amount",
            "transaction value"
        ]:
            column_mapping[column] = "Amount"

        # Currency
        elif lower in [
            "currency",
            "curr",
            "currency code"
        ]:
            column_mapping[column] = "Currency"

        # Markup
        elif lower in [
            "markup",
            "mark up",
            "forex markup",
            "foreign exchange markup"
        ]:
            column_mapping[column] = "Markup"

    df = df.rename(
        columns=column_mapping
    )

    return df


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_text(file):

    text = ""

    file_bytes = file.getvalue()

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += "\n" + page_text

    return text


# =========================================================
# TEXT TRANSACTION EXTRACTION
# =========================================================

def parse_pdf_text(text):

    rows = []

    if not text:
        return pd.DataFrame()

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # -------------------------------------------------
        # DATE PATTERNS
        # -------------------------------------------------

        date_match = re.match(
            r"^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.*)",
            line
        )

        if not date_match:

            date_match = re.match(
                r"^(\d{4}[/-]\d{1,2}[/-]\d{1,2})\s+(.*)",
                line
            )

        if not date_match:
            continue

        date_value = date_match.group(1)
        remaining = date_match.group(2).strip()

        # -------------------------------------------------
        # FIND MONEY VALUE AT END OF LINE
        # -------------------------------------------------

        amount_matches = re.findall(
            r"(?:₹|\$|€|£)?\s*-?\d[\d,]*(?:\.\d{1,2})?",
            remaining
        )

        if not amount_matches:
            continue

        amount_text = amount_matches[-1]

        amount_clean = (
            amount_text
            .replace("₹", "")
            .replace("$", "")
            .replace("€", "")
            .replace("£", "")
            .replace(",", "")
            .strip()
        )

        try:
            amount = float(amount_clean)
        except ValueError:
            continue

        # -------------------------------------------------
        # MERCHANT
        # -------------------------------------------------

        merchant = remaining

        # Remove final amount
        merchant = merchant.rsplit(
            amount_text,
            1
        )[0].strip()

        # Remove common trailing balance
        merchant = re.sub(
            r"\s+\d[\d,]*\.\d{2}$",
            "",
            merchant
        ).strip()

        if merchant == "":
            merchant = "Unknown Merchant"

        rows.append(
            {
                "Date": date_value,
                "Merchant": merchant,
                "Amount": amount,
                "Currency": "INR",
                "Markup": 0
            }
        )

    return pd.DataFrame(rows)


# =========================================================
# PDF READER
# =========================================================

def read_pdf(file):

    # -----------------------------------------------------
    # STEP 1: TRY TABLE EXTRACTION
    # -----------------------------------------------------

    try:

        table_rows = extract_pdf_tables(file)

        if table_rows:

            df = table_rows_to_dataframe(
                table_rows
            )

            if df is not None and not df.empty:

                df = standardize_pdf_columns(df)

                # If required transaction columns exist
                if (
                    "Date" in df.columns
                    and "Merchant" in df.columns
                    and "Amount" in df.columns
                ):

                    if "Currency" not in df.columns:
                        df["Currency"] = "INR"

                    if "Markup" not in df.columns:
                        df["Markup"] = 0

                    return df

    except Exception:
        pass

    # -----------------------------------------------------
    # STEP 2: FALL BACK TO TEXT EXTRACTION
    # -----------------------------------------------------

    text = extract_pdf_text(file)

    df = parse_pdf_text(text)

    if df.empty:

        raise ValueError(
            "No transactions could be extracted from this PDF. "
            "The PDF may be scanned/image-based or use an unsupported layout."
        )

    return df


# =========================================================
# MAIN FILE READER
# =========================================================

def read_statement(file):

    if file is None:
        raise ValueError("No file was uploaded.")

    filename = file.name.lower()

    # CSV
    if filename.endswith(".csv"):

        return read_csv(file)

    # PDF
    elif filename.endswith(".pdf"):

        return read_pdf(file)

    else:

        raise ValueError(
            "Unsupported file type. Please upload a CSV or PDF file."
        )