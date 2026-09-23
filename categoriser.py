from config import CATEGORY_KEYWORDS


def categorise_merchant(merchant):

    merchant = str(
        merchant
    ).lower()

    for category, keywords in (
        CATEGORY_KEYWORDS.items()
    ):

        for keyword in keywords:

            if keyword in merchant:

                return category

    return "Other"


def categorise_transactions(df):

    df = df.copy()

    df["Category"] = (
        df["Merchant"]
        .apply(
            categorise_merchant
        )
    )

    return df