import streamlit as st
import pandas as pd
import plotly.express as px


def display_dashboard(df):

    data = df.copy()

    # =====================================================
    # CLEAN DATA TYPES
    # =====================================================

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce"
    )

    data["Amount"] = pd.to_numeric(
        data["Amount"],
        errors="coerce"
    ).fillna(0)

    data["Markup"] = pd.to_numeric(
        data["Markup"],
        errors="coerce"
    ).fillna(0)

    data["Total_Cost"] = pd.to_numeric(
        data["Total_Cost"],
        errors="coerce"
    ).fillna(
        data["Amount"] + data["Markup"]
    )

    data["Merchant"] = (
        data["Merchant"]
        .fillna("Unknown Merchant")
        .astype(str)
    )

    data["Category"] = (
        data["Category"]
        .fillna("Other")
        .astype(str)
    )

    data["Currency"] = (
        data["Currency"]
        .fillna("INR")
        .astype(str)
        .str.upper()
    )

    # =====================================================
    # TITLE
    # =====================================================

    st.title("📊 Spending Dashboard")

    # =====================================================
    # BASIC STATISTICS
    # =====================================================

    transaction_count = len(data)

    # INR transactions only for INR spending total
    inr_data = data[
        data["Currency"] == "INR"
    ]

    foreign_data = data[
        data["Currency"] != "INR"
    ]

    total_inr_spending = inr_data[
        "Total_Cost"
    ].sum()

    average_transaction = (
        data["Amount"].abs().mean()
        if transaction_count > 0
        else 0
    )

    unique_merchants = (
        data["Merchant"].nunique()
    )

    total_markup = data[
        "Markup"
    ].sum()

    foreign_count = len(
        foreign_data
    )

    # =====================================================
    # TOP METRICS
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total INR Spending",
            f"₹{total_inr_spending:,.2f}"
        )

    with col2:

        st.metric(
            "Transactions",
            transaction_count
        )

    with col3:

        st.metric(
            "Average Transaction",
            f"₹{average_transaction:,.2f}"
        )

    with col4:

        st.metric(
            "Unique Merchants",
            unique_merchants
        )

    # =====================================================
    # MARKUP + FOREIGN TRANSACTIONS
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Total Markup",
            f"₹{total_markup:,.2f}"
        )

    with col2:

        st.metric(
            "Foreign Currency Transactions",
            foreign_count
        )

    # =====================================================
    # SPENDING BY CATEGORY
    # =====================================================

    st.subheader(
        "🏷️ Spending by Category"
    )

    category_data = (
        inr_data
        .groupby("Category", as_index=False)
        ["Total_Cost"]
        .sum()
        .sort_values(
            "Total_Cost",
            ascending=False
        )
    )

    if not category_data.empty:

        category_chart = px.pie(
            category_data,
            names="Category",
            values="Total_Cost",
            hole=0.35,
            title="Spending Distribution by Category"
        )

        st.plotly_chart(
            category_chart,
            use_container_width=True
        )

    # =====================================================
    # MONTHLY SPENDING
    # =====================================================

    st.subheader(
        "📅 Monthly Spending"
    )

    data["Month"] = (
        data["Date"]
        .dt.strftime("%Y-%m")
    )

    monthly_data = (
        inr_data.copy()
    )

    monthly_data["Month"] = (
        monthly_data["Date"]
        .dt.strftime("%Y-%m")
    )

    monthly_data = (
        monthly_data
        .groupby("Month", as_index=False)
        ["Total_Cost"]
        .sum()
    )

    if not monthly_data.empty:

        monthly_chart = px.bar(
            monthly_data,
            x="Month",
            y="Total_Cost",
            title="Monthly Spending",
            labels={
                "Month": "Month",
                "Total_Cost": "Spending (₹)"
            }
        )

        st.plotly_chart(
            monthly_chart,
            use_container_width=True
        )

    # =====================================================
    # MERCHANT SPENDING
    # =====================================================

    st.subheader(
        "🏪 Merchant Spending"
    )

    merchant_data = (
        data
        .groupby("Merchant")
        .agg(
            Transactions=(
                "Merchant",
                "count"
            ),
            Total_Spending=(
                "Total_Cost",
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            "Total_Spending",
            ascending=False
        )
    )

    st.dataframe(
        merchant_data,
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # RECURRING PAYMENTS
    # =====================================================

    st.subheader(
        "🔄 Possible Recurring Payments"
    )

    recurring_data = (
        data
        .groupby("Merchant")
        .agg(
            Occurrences=(
                "Merchant",
                "count"
            ),
            Average_Amount=(
                "Amount",
                "mean"
            ),
            Total_Amount=(
                "Amount",
                "sum"
            )
        )
        .reset_index()
    )

    recurring_data = (
        recurring_data[
            recurring_data["Occurrences"] >= 2
        ]
        .sort_values(
            "Occurrences",
            ascending=False
        )
    )

    if recurring_data.empty:

        st.info(
            "No recurring payments detected."
        )

    else:

        st.dataframe(
            recurring_data,
            use_container_width=True,
            hide_index=True
        )

    # =====================================================
    # FOREIGN CURRENCY
    # =====================================================

    st.subheader(
        "🌍 Foreign Currency Transactions"
    )

    if foreign_data.empty:

        st.info(
            "No foreign currency transactions found."
        )

    else:

        st.dataframe(
            foreign_data[
                [
                    "Date",
                    "Merchant",
                    "Amount",
                    "Currency",
                    "Markup",
                    "Category"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Foreign transaction amounts are shown "
            "in their original currency. Markup is shown separately in INR."
        )

    # =====================================================
    # ALL CLEANED TRANSACTIONS
    # =====================================================

    st.subheader(
        "📋 Cleaned Transactions"
    )

    st.dataframe(
        data[
            [
                "Date",
                "Merchant",
                "Amount",
                "Currency",
                "Markup",
                "Total_Cost",
                "Category"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    st.subheader(
        "⬇️ Download Report"
    )

    csv_data = (
        data
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        label="📥 Download Cleaned CSV",
        data=csv_data,
        file_name="cleaned_credit_card_transactions.csv",
        mime="text/csv"
    )