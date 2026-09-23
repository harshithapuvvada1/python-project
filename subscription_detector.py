def detect_recurring_payments(df):

    recurring = (
        df.groupby("Merchant")
        .agg(
            Occurrences=(
                "Merchant",
                "count"
            ),
            Average_Amount=(
                "Total_Cost",
                "mean"
            ),
            Total_Amount=(
                "Total_Cost",
                "sum"
            )
        )
        .reset_index()
    )

    recurring = recurring[
        recurring["Occurrences"] >= 2
    ]

    recurring[
        "Average_Amount"
    ] = recurring[
        "Average_Amount"
    ].round(2)

    recurring[
        "Total_Amount"
    ] = recurring[
        "Total_Amount"
    ].round(2)

    return recurring.sort_values(
        "Occurrences",
        ascending=False
    )