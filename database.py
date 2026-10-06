import mysql.connector


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Harshi@1#",
        database="credit_card_analyser"
    )


# =========================================================
# CHECK STATEMENT
# =========================================================

def statement_exists(filename):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        query = """
            SELECT statement_id
            FROM statements
            WHERE filename = %s
            LIMIT 1
        """

        cursor.execute(
            query,
            (filename,)
        )

        result = cursor.fetchone()

        return result[0] if result else None

    finally:

        cursor.close()
        connection.close()


# =========================================================
# DELETE EXISTING STATEMENT
# =========================================================

def delete_statement(statement_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # -------------------------------------------------
        # DELETE TRANSACTIONS FIRST
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM transactions
            WHERE statement_id = %s
            """,
            (statement_id,)
        )

        # -------------------------------------------------
        # DELETE STATEMENT
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM statements
            WHERE statement_id = %s
            """,
            (statement_id,)
        )

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CREATE STATEMENT
# =========================================================

def create_statement(filename):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        query = """
            INSERT INTO statements (filename)
            VALUES (%s)
        """

        cursor.execute(
            query,
            (filename,)
        )

        statement_id = cursor.lastrowid

        connection.commit()

        return statement_id

    except Exception:

        connection.rollback()
        raise

    finally:

        cursor.close()
        connection.close()


# =========================================================
# INSERT TRANSACTIONS
# =========================================================

def insert_transactions(df, statement_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        query = """
            INSERT INTO transactions
            (
                date,
                merchant,
                amount,
                currency,
                markup,
                total_cost,
                category,
                statement_id
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
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
                str(row["Category"]),
                statement_id
            )

            cursor.execute(
                query,
                values
            )

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        cursor.close()
        connection.close()