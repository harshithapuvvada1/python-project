APP_TITLE = "Credit Card Statement Analyser"
APP_ICON = "💳"

SUPPORTED_FILE_TYPES = ["csv", "pdf"]

DEFAULT_CURRENCY = "INR"

CATEGORIES = [
    "Food",
    "Shopping",
    "Travel",
    "Entertainment",
    "Bills",
    "Health",
    "Education",
    "Other"
]

REQUIRED_COLUMNS = [
    "Date",
    "Merchant",
    "Amount"
]

CATEGORY_KEYWORDS = {

    "Food": [
        "swiggy",
        "zomato",
        "dominos",
        "pizza",
        "restaurant",
        "food",
        "cafe",
        "kfc",
        "mcdonald"
    ],

    "Shopping": [
        "amazon",
        "amzn",
        "flipkart",
        "myntra",
        "shopping",
        "mall",
        "retail"
    ],

    "Travel": [
        "uber",
        "ola",
        "flight",
        "airlines",
        "irctc",
        "travel",
        "hotel",
        "booking",
        "makemytrip"
    ],

    "Entertainment": [
        "netflix",
        "spotify",
        "movie",
        "cinema",
        "youtube",
        "prime",
        "bookmyshow"
    ],

    "Bills": [
        "airtel",
        "jio",
        "electricity",
        "mobile",
        "internet",
        "water",
        "bill"
    ],

    "Health": [
        "hospital",
        "pharmacy",
        "medical",
        "clinic",
        "apollo"
    ],

    "Education": [
        "college",
        "course",
        "udemy",
        "coursera",
        "books"
    ]
}