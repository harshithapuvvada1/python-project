import re
from io import BytesIO

import pandas as pd

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


def read_csv(file):

    return pd.read_csv(file)


def clean_pdf_table(table):

    rows = []

    if not table:
        return rows

    for row in table:

        if not row:
            continue

        cleaned_row = []

        for cell in row:

            if cell is None:
                cleaned_row.append("")
            else:
                cleaned_row.append(
                    str(cell).strip()
                )

        rows.append(cleaned_row)

    return rows


def read_pdf(file):

    if pdfplumber is None:

        raise ImportError(
            "pdfplumber is not installed. "
            "Run: pip install pdfplumber"
        )

    tables = []

    file_bytes = file.getvalue()

    with pdfplumber.open(
        BytesIO(file_bytes)
    ) as pdf:

        for page in pdf.pages:

            page_tables = page.extract_tables()

            for table in page_tables:

                cleaned = clean_pdf_table(table)

                tables.extend(cleaned)

    if tables:

        first_row = tables[0]

        if any(
            "date" in str(cell).lower()
            for cell in first_row
        ):

            header = first_row

            data = tables[1:]

            return pd.DataFrame(
                data,
                columns=header
            )

    # ---------------------------------------------
    # FALLBACK: TEXT EXTRACTION
    # ---------------------------------------------

    text_rows = []

    with pdfplumber.open(
        BytesIO(file_bytes)
    ) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if text:

                text_rows.extend(
                    text.split("\n")
                )

    return parse_pdf_lines(text_rows)


def parse_pdf_lines(lines):

    records = []

    pattern = re.compile(
        r"(\d{1,4}[-/]\d{1,2}[-/]\d{1,4})\s+"
        r"(.+?)\s+"
        r"([\d,]+(?:\.\d+)?)$"
    )

    for line in lines:

        line = line.strip()

        match = pattern.search(line)

        if match:

            records.append({
                "Date": match.group(1),
                "Merchant": match.group(2),
                "Amount": match.group(3)
            })

    if not records:

        raise ValueError(
            "No transactions could be detected "
            "from this PDF format."
        )

    return pd.DataFrame(records)


def read_statement(file):

    filename = file.name.lower()

    if filename.endswith(".csv"):

        return read_csv(file)

    if filename.endswith(".pdf"):

        return read_pdf(file)

    raise ValueError(
        "Only CSV and PDF files are supported."
    )