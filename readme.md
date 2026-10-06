# 💳 Credit Card Statement Analyser & Spend Categoriser

A full-stack web application that analyses credit card statements, cleans transaction data, categorises spending, detects foreign transactions and recurring payments, and stores transaction records in a MySQL database.

---

## 📌 Project Overview

The Credit Card Statement Analyser helps users understand their credit card spending by processing statement files in CSV and PDF formats.

The system extracts transaction information, cleans and standardises the data, categorises merchants, stores the processed transactions in MySQL, and displays the results through an interactive React dashboard.

---

## 🎯 Objectives

- Analyse credit card transactions automatically.
- Support CSV and PDF statements.
- Clean and standardise transaction data.
- Categorise transactions based on merchants.
- Identify foreign transactions.
- Identify recurring payments and possible subscriptions.
- Store transaction data in MySQL.
- Provide an easy-to-understand dashboard for spending analysis.

---

## ✨ Features

### 📄 Statement Upload

- Upload CSV credit card statements.
- Upload PDF credit card statements.
- Extract transaction information automatically.

### 🧹 Data Cleaning

- Clean transaction amounts.
- Standardise merchant names.
- Process transaction dates.
- Handle currencies and markups.
- Handle credit and refund transactions.

### 🏷️ Spending Categorisation

Transactions can be organised into categories such as:

- Food
- Shopping
- Travel
- Entertainment
- Bills
- Health
- Education
- Other

### 📊 Spending Dashboard

The dashboard provides:

- Total spending
- Average transaction
- Transaction count
- Category-wise spending
- Monthly spending
- Merchant analysis
- Foreign transaction information
- Recurring payment information

### 🌍 Foreign Transaction Detection

The application identifies transactions made in foreign currencies and separates them from regular INR transactions.

### 🔁 Recurring Payment Detection

The application identifies merchants appearing multiple times and displays them as possible recurring payments or subscriptions.

Refunds and foreign transaction markup/tax entries are excluded from subscription detection.

### 🗄️ MySQL Database

Processed transactions and uploaded statement information are stored in MySQL.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Data processing and backend logic |
| Pandas | Data cleaning and analysis |
| FastAPI | Backend REST API |
| React.js | Frontend application |
| CSS | Frontend styling |
| MySQL | Database |
| pdfplumber | PDF statement extraction |
| Vite | React development server |
| Git | Version control |
| GitHub | Source code management |



