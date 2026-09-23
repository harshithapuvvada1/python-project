import mysql.connector


# ============================================================
# MYSQL CONNECTION
# ============================================================

def get_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Harshi@1#",
        database="credit_card_analyser"
    )

    return connection


# ============================================================
# INSERT TRANSACTIONS
# ============================================================

def insert_transactions(df):

    connection = get_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO transactions
        (
            date,
            merchant,
            amount,
            currency,
            markup,
            total_cost,
            category
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    for _, row in df.iterrows():

        date_value = row["Date"]

        if hasattr(date_value, "date"):
            date_value = date_value.date()

        values = (
            date_value,
            str(row["Merchant"]),
            float(row["Amount"]),
            str(row["Currency"]),
            float(row["Markup"]),
            float(row["Total_Cost"]),
            str(row["Category"])
        )

        cursor.execute(
            query,
            values
        )

    connection.commit()

    cursor.close()

    connection.close()