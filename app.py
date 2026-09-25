import streamlit as st
import pandas as pd
import io

from config import APP_TITLE, APP_ICON
from statement_reader import read_statement
from data_cleaner import clean_data
from categoriser import categorise_transactions
from dashboard import display_dashboard
from database import insert_transactions


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide"
)


def main():

    st.title("💳 Credit Card Statement Analyser")

    st.write(
        "Upload your credit card statement in CSV or PDF format "
        "to analyse spending, categories, merchants and recurring payments."
    )

    st.divider()

    # =====================================================
    # SAMPLE CSV
    # =====================================================

    st.subheader("📄 Try with a Sample CSV")

    st.write(
        "Download the sample CSV to understand the required "
        "transaction format."
    )

    sample_csv = """Date,Merchant,Amount,Currency,Markup
2026-01-03,Amazon,2499,INR,0
2026-01-05,Swiggy,520,INR,0
2026-01-07,Uber,310,INR,0
2026-01-10,Netflix,649,INR,0
2026-01-12,Flipkart,1899,INR,0
2026-01-15,Airtel Mobile Bill,799,INR,0
2026-01-18,Spotify,119,INR,0
2026-01-20,Amazon,899,INR,0
2026-01-22,Dominos Pizza,780,INR,0
2026-01-25,Uber,280,INR,0
2026-02-02,Amazon,1599,INR,0
2026-02-05,Swiggy,430,INR,0
2026-02-07,Netflix,649,INR,0
2026-02-10,Airtel Mobile Bill,799,INR,0
2026-02-12,Spotify,119,INR,0
2026-02-15,Amazon UK,12000,GBP,360
"""

    col1, col2 = st.columns([1, 2])

    with col1:

        st.download_button(
            label="⬇️ Download Sample CSV",
            data=sample_csv,
            file_name="sample_credit_card_statement.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:

        st.caption(
            "Download the sample, open it in Excel, "
            "edit the transactions if needed, and upload it below."
        )

    with st.expander("👀 View Sample Data"):

        sample_df = pd.read_csv(
            io.StringIO(sample_csv)
        )

        st.dataframe(
            sample_df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # =====================================================
    # FILE UPLOAD
    # =====================================================

    st.subheader("📂 Upload Your Statement")

    uploaded_file = st.file_uploader(
        "Choose a CSV or PDF file",
        type=["csv", "pdf"],
        help="Supported formats: CSV and PDF"
    )

    if uploaded_file is None:

        st.info(
            "👆 Upload a CSV or PDF statement to begin analysis."
        )

        return

    st.success(
        f"📄 File selected: **{uploaded_file.name}**"
    )

    analyse_button = st.button(
        "🚀 Analyse Statement",
        type="primary",
        use_container_width=True
    )

    if not analyse_button:
        return

    try:

        # =================================================
        # READ FILE
        # =================================================

        with st.spinner("📖 Reading statement..."):

            df = read_statement(
                uploaded_file
            )

        if df is None or df.empty:

            st.error(
                "❌ No transactions were found in the uploaded file."
            )

            return

        # TEMPORARY DEBUG INFORMATION
        st.subheader("🔍 Processing Check")

        st.write(
            f"**Rows read from uploaded file: {len(df)}**"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # =================================================
        # CLEAN DATA
        # =================================================

        with st.spinner("🧹 Processing transaction data..."):

            df = clean_data(df)

        if df is None or df.empty:

            st.error(
                "❌ No valid transactions remain after processing."
            )

            return

        # TEMPORARY DEBUG INFORMATION
        st.write(
            f"**Rows after cleaning: {len(df)}**"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # =================================================
        # CATEGORISE
        # =================================================

        with st.spinner("🏷️ Analysing transactions..."):

            df = categorise_transactions(df)

        # =================================================
        # SAVE TO DATABASE
        # =================================================

        with st.spinner("🗄️ Saving data..."):

            try:

                insert_transactions(df)

            except Exception as database_error:

                st.warning(
                    "⚠️ Data could not be saved to MySQL."
                )

                st.caption(
                    f"MySQL message: {database_error}"
                )

        # =================================================
        # DASHBOARD
        # =================================================

        st.divider()

        display_dashboard(df)

    except Exception as e:

        st.error(
            "❌ An error occurred while processing the statement."
        )

        st.exception(e)


if __name__ == "__main__":
    main()