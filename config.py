APP_TITLE = "Credit Card Statement Analyser"

APP_ICON = "💳"

SUPPORTED_FILE_TYPES = [
    "csv",
    "pdf"
]

DEFAULT_CURRENCY = "INR"

REQUIRED_COLUMNS = [
    "Date",
    "Merchant",
    "Amount"
]

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

CATEGORY_KEYWORDS = {

    "Food": [
        "swiggy",
        "zomato",
        "dominos",
        "pizza",
        "restaurant",
        "food"
    ],

    "Shopping": [
        "amazon",
        "flipkart",
        "myntra",
        "shopping"
    ],

    "Travel": [
        "uber",
        "ola",
        "hotel",
        "booking",
        "flight",
        "travel"
    ],

    "Entertainment": [
        "netflix",
        "spotify",
        "prime video",
        "bookmyshow",
        "movie"
    ],

    "Bills": [
        "airtel",
        "jio",
        "electricity",
        "mobile",
        "internet",
        "bill"
    ],

    "Health": [
        "apollo",
        "pharmacy",
        "hospital",
        "medical"
    ],

    "Education": [
        "udemy",
        "coursera",
        "course",
        "education"
    ]
}