import streamlit as st

from config import APP_TITLE, APP_ICON, SUPPORTED_FILE_TYPES
from statement_reader import read_statement
from data_cleaner import clean_data
from categoriser import categorise_transactions
from dashboard import display_dashboard
from database import insert_transactions


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("💳 Credit Card Statement Analyser")

st.subheader("Spend Categoriser")

st.write(
    "Upload your credit card statement to analyse spending, "
    "categorise transactions, detect recurring payments, "
    "analyse foreign currency transactions and generate reports."
)


# ============================================================
# FILE UPLOAD
# ============================================================

st.header("📂 Upload Credit Card Statement")

uploaded_file = st.file_uploader(
    "Choose a CSV or PDF file",
    type=SUPPORTED_FILE_TYPES
)


# ============================================================
# PROCESS FILE
# ============================================================

if uploaded_file is not None:

    file_key = (
        f"{uploaded_file.name}_"
        f"{uploaded_file.size}"
    )

    try:

        # ====================================================
        # PROCESSING STATUS
        # ====================================================

        with st.status(
            "Processing your statement...",
            expanded=True
        ) as status:

            # ------------------------------------------------
            # STEP 1: READ
            # ------------------------------------------------

            st.write(
                "📖 Reading statement..."
            )

            df = read_statement(
                uploaded_file
            )

            if df is None or df.empty:

                st.error(
                    "No transactions were found "
                    "in the uploaded file."
                )

                st.stop()

            original_count = len(df)

            st.write(
                f"✅ {original_count} transaction rows found."
            )


            # ------------------------------------------------
            # STEP 2: CLEAN
            # ------------------------------------------------

            st.write(
                "🧹 Cleaning transaction data..."
            )

            df = clean_data(df)

            cleaned_count = len(df)

            st.write(
                f"✅ {cleaned_count} transactions "
                "ready for analysis."
            )


            # ------------------------------------------------
            # STEP 3: CATEGORISE
            # ------------------------------------------------

            st.write(
                "🏷️ Categorising transactions..."
            )

            df = categorise_transactions(df)

            st.write(
                "✅ Transactions categorised successfully."
            )


            # ------------------------------------------------
            # STEP 4: MYSQL
            # ------------------------------------------------

            st.write(
                "🗄️ Saving transactions to MySQL..."
            )

            if (
                "saved_file" not in st.session_state
                or st.session_state.saved_file != file_key
            ):

                insert_transactions(df)

                st.session_state.saved_file = file_key

                st.write(
                    "✅ Transactions saved to MySQL."
                )

            else:

                st.write(
                    "ℹ️ This file is already saved "
                    "in MySQL."
                )


            # ------------------------------------------------
            # COMPLETE
            # ------------------------------------------------

            status.update(
                label="✅ Statement processed successfully!",
                state="complete",
                expanded=False
            )


        # ====================================================
        # DASHBOARD
        # ====================================================

        st.divider()

        display_dashboard(df)


    except Exception as e:

        st.error(
            "❌ An error occurred while processing "
            "the statement."
        )

        st.exception(e)