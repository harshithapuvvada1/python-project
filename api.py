from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import io

from data_cleaner import clean_data
from categoriser import categorise_transactions
from statement_reader import read_statement

from database import (
    insert_transactions,
    statement_exists,
    delete_statement,
    create_statement,
    get_connection
)


# =========================================================
# CREATE FASTAPI APP
# =========================================================

app = FastAPI(
    title="Credit Card Statement Analyser API",
    description="Backend API for Credit Card Statement Analyser",
    version="1.0.0"
)


# =========================================================
# CORS - ALLOW REACT FRONTEND
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "Credit Card Statement Analyser API is running!"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
def health():

    return {
        "status": "success",
        "message": "Backend is working"
    }


# =========================================================
# UPLOAD STATEMENT
# =========================================================

@app.post("/api/upload")
async def upload_statement(
    file: UploadFile = File(...)
):

    # -----------------------------------------------------
    # CHECK FILE
    # -----------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    original_filename = file.filename
    filename = original_filename.lower()


    # =====================================================
    # CHECK AND REMOVE EXISTING STATEMENT
    # =====================================================

    existing_statement = statement_exists(
        original_filename
    )

    if existing_statement:

        try:

            delete_statement(
                existing_statement
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Could not replace the existing "
                    f"statement: {str(e)}"
                )
            )


    # =====================================================
    # CSV FILE
    # =====================================================

    if filename.endswith(".csv"):

        try:

            # -------------------------------------------------
            # READ FILE
            # -------------------------------------------------

            contents = await file.read()

            if not contents:

                raise HTTPException(
                    status_code=400,
                    detail="CSV file is empty."
                )

            df = pd.read_csv(
                io.BytesIO(contents)
            )

            raw_count = len(df)


            # -------------------------------------------------
            # CLEAN DATA
            # -------------------------------------------------

            cleaned_df = clean_data(df)


            # -------------------------------------------------
            # CATEGORISE DATA
            # -------------------------------------------------

            analysed_df = categorise_transactions(
                cleaned_df
            )


            # -------------------------------------------------
            # CREATE STATEMENT RECORD
            # -------------------------------------------------

            statement_id = create_statement(
                original_filename
            )


            # -------------------------------------------------
            # SAVE TRANSACTIONS TO MYSQL
            # -------------------------------------------------

            insert_transactions(
                analysed_df,
                statement_id
            )


            # -------------------------------------------------
            # CONVERT DATE FOR JSON
            # -------------------------------------------------

            if "Date" in analysed_df.columns:

                analysed_df["Date"] = (
                    analysed_df["Date"]
                    .astype(str)
                )


            # -------------------------------------------------
            # HANDLE EMPTY VALUES
            # -------------------------------------------------

            analysed_df = analysed_df.fillna("")


            # -------------------------------------------------
            # CONVERT DATAFRAME TO JSON
            # -------------------------------------------------

            transactions = analysed_df.to_dict(
                orient="records"
            )


            # -------------------------------------------------
            # RETURN RESPONSE
            # -------------------------------------------------

            return {

                "status": "success",

                "filename": original_filename,

                "file_type": "CSV",

                "statement_id": statement_id,

                "raw_transactions": raw_count,

                "cleaned_transactions": len(
                    analysed_df
                ),

                "columns": list(
                    analysed_df.columns
                ),

                "database": "saved",

                "message": (
                    "CSV statement uploaded, "
                    "cleaned, categorised and "
                    "saved successfully."
                ),

                "transactions": transactions
            }


        except HTTPException:

            raise


        except Exception as e:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"CSV analysis failed: {str(e)}"
                )
            )


    # =====================================================
    # PDF FILE
    # =====================================================

    elif filename.endswith(".pdf"):

        try:

            # -------------------------------------------------
            # READ PDF
            # -------------------------------------------------

            contents = await file.read()

            if not contents:

                raise HTTPException(
                    status_code=400,
                    detail="PDF file is empty."
                )


            # -------------------------------------------------
            # CREATE FILE-LIKE OBJECT
            # -------------------------------------------------

            pdf_file = io.BytesIO(
                contents
            )

            pdf_file.name = original_filename


            # -------------------------------------------------
            # EXTRACT PDF TRANSACTIONS
            # -------------------------------------------------

            df = read_statement(
                pdf_file
            )


            if df is None or df.empty:

                raise ValueError(
                    "No transactions were found in the PDF."
                )


            raw_count = len(df)


            # -------------------------------------------------
            # CLEAN DATA
            # -------------------------------------------------

            cleaned_df = clean_data(df)


            # -------------------------------------------------
            # CATEGORISE DATA
            # -------------------------------------------------

            analysed_df = categorise_transactions(
                cleaned_df
            )


            # -------------------------------------------------
            # CREATE STATEMENT RECORD
            # -------------------------------------------------

            statement_id = create_statement(
                original_filename
            )


            # -------------------------------------------------
            # SAVE TRANSACTIONS TO MYSQL
            # -------------------------------------------------

            insert_transactions(
                analysed_df,
                statement_id
            )


            # -------------------------------------------------
            # CONVERT DATE FOR JSON
            # -------------------------------------------------

            if "Date" in analysed_df.columns:

                analysed_df["Date"] = (
                    analysed_df["Date"]
                    .astype(str)
                )


            # -------------------------------------------------
            # HANDLE EMPTY VALUES
            # -------------------------------------------------

            analysed_df = analysed_df.fillna("")


            # -------------------------------------------------
            # CONVERT DATAFRAME TO JSON
            # -------------------------------------------------

            transactions = analysed_df.to_dict(
                orient="records"
            )


            # -------------------------------------------------
            # RETURN RESPONSE
            # -------------------------------------------------

            return {

                "status": "success",

                "filename": original_filename,

                "file_type": "PDF",

                "statement_id": statement_id,

                "raw_transactions": raw_count,

                "cleaned_transactions": len(
                    analysed_df
                ),

                "columns": list(
                    analysed_df.columns
                ),

                "database": "saved",

                "message": (
                    "PDF statement uploaded, "
                    "transactions extracted, "
                    "cleaned, categorised and "
                    "saved successfully."
                ),

                "transactions": transactions
            }


        except HTTPException:

            raise


        except Exception as e:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"PDF analysis failed: {str(e)}"
                )
            )


    # =====================================================
    # UNSUPPORTED FILE
    # =====================================================

    else:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload a CSV or PDF file."
            )
        )


# =========================================================
# GET ALL TRANSACTIONS FROM MYSQL
# =========================================================

@app.get("/api/transactions")
def get_transactions():

    connection = None
    cursor = None

    try:

        # -------------------------------------------------
        # CONNECT TO DATABASE
        # -------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # GET TRANSACTIONS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                transaction_id,
                date,
                merchant,
                amount,
                currency,
                markup,
                total_cost,
                category,
                statement_id
            FROM transactions
            ORDER BY date DESC, transaction_id DESC
            """
        )


        transactions = cursor.fetchall()


        # -------------------------------------------------
        # CONVERT DATE TO STRING
        # -------------------------------------------------

        for transaction in transactions:

            if transaction["date"]:

                transaction["date"] = str(
                    transaction["date"]
                )


        # -------------------------------------------------
        # RETURN DATA
        # -------------------------------------------------

        return {

            "status": "success",

            "count": len(
                transactions
            ),

            "transactions": transactions
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not fetch transactions: "
                f"{str(e)}"
            )
        )


    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()


# =========================================================
# GET ALL STATEMENTS
# =========================================================

@app.get("/api/statements")
def get_statements():

    connection = None
    cursor = None

    try:

        # -------------------------------------------------
        # CONNECT TO DATABASE
        # -------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # GET STATEMENTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                statement_id,
                filename,
                upload_date
            FROM statements
            ORDER BY upload_date DESC
            """
        )


        statements = cursor.fetchall()


        # -------------------------------------------------
        # CONVERT DATETIME TO STRING
        # -------------------------------------------------

        for statement in statements:

            if statement["upload_date"]:

                statement["upload_date"] = str(
                    statement["upload_date"]
                )


        # -------------------------------------------------
        # RETURN DATA
        # -------------------------------------------------

        return {

            "status": "success",

            "count": len(
                statements
            ),

            "statements": statements
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not fetch statements: "
                f"{str(e)}"
            )
        )


    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()