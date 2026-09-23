def total_spending(df):

    return df["Total_Cost"].sum()


def average_transaction(df):

    return df["Total_Cost"].mean()


def transaction_count(df):

    return len(df)


def unique_merchants(df):

    return df["Merchant"].nunique()


def total_markup(df):

    return df["Markup"].sum()


def category_summary(df):

    return (
        df.groupby("Category")[
            "Total_Cost"
        ]
        .sum()
        .reset_index()
        .sort_values(
            "Total_Cost",
            ascending=False
        )
    )


def monthly_summary(df):

    data = df.copy()

    data["Month"] = (
        data["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    return (
        data.groupby("Month")[
            "Total_Cost"
        ]
        .sum()
        .reset_index()
    )


def merchant_summary(df):

    return (
        df.groupby("Merchant")
        .agg(
            Total_Spending=(
                "Total_Cost",
                "sum"
            ),
            Transactions=(
                "Merchant",
                "count"
            )
        )
        .reset_index()
        .sort_values(
            "Total_Spending",
            ascending=False
        )
    )


def foreign_currency_summary(df):

    foreign = df[
        df["Currency"].str.upper()
        != "INR"
    ]

    return foreign[
        [
            "Date",
            "Merchant",
            "Amount",
            "Currency",
            "Markup",
            "Total_Cost"
        ]
    ]