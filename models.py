from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:

    date: datetime
    merchant: str
    amount: float
    currency: str = "INR"
    category: str = "Other"
    markup: float = 0.0

    def is_foreign_currency(self):

        return self.currency.upper() != "INR"

    def total_cost(self):

        return self.amount + self.markup


@dataclass
class Statement:

    filename: str
    transactions: list

    def transaction_count(self):

        return len(self.transactions)

    def total_amount(self):

        return sum(
            transaction.amount
            for transaction in self.transactions
        )

    def total_markup(self):

        return sum(
            transaction.markup
            for transaction in self.transactions
        )