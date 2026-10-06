import React, { useMemo, useState } from "react";
import "./App.css";

const sampleTransactions = [
  {
    Date: "2026-02-01",
    Merchant: "Amazon",
    Amount: 2499,
    Currency: "INR",
    Markup: 0,
    Category: "Shopping",
  },
  {
    Date: "2026-02-03",
    Merchant: "Netflix",
    Amount: 649,
    Currency: "INR",
    Markup: 0,
    Category: "Entertainment",
  },
  {
    Date: "2026-02-05",
    Merchant: "Spotify",
    Amount: 119,
    Currency: "INR",
    Markup: 0,
    Category: "Entertainment",
  },
  {
    Date: "2026-02-07",
    Merchant: "Swiggy",
    Amount: 450,
    Currency: "INR",
    Markup: 0,
    Category: "Food",
  },
  {
    Date: "2026-02-09",
    Merchant: "Zomato",
    Amount: 620,
    Currency: "INR",
    Markup: 0,
    Category: "Food",
  },
  {
    Date: "2026-02-12",
    Merchant: "Uber",
    Amount: 280,
    Currency: "INR",
    Markup: 0,
    Category: "Travel",
  },
  {
    Date: "2026-02-15",
    Merchant: "Apple",
    Amount: 1689.15,
    Currency: "USD",
    Markup: 0,
    Category: "Other",
  },
  {
    Date: "2026-02-15",
    Merchant: "Apple FCY Markup",
    Amount: 59.12,
    Currency: "INR",
    Markup: 0,
    Category: "Other",
  },
  {
    Date: "2026-02-20",
    Merchant: "OpenAI",
    Amount: 1690,
    Currency: "USD",
    Markup: 0,
    Category: "Other",
  },
  {
    Date: "2026-02-20",
    Merchant: "OpenAI FCY Markup",
    Amount: 59.15,
    Currency: "INR",
    Markup: 0,
    Category: "Other",
  },
  {
    Date: "2026-02-25",
    Merchant: "Amazon Refund",
    Amount: -799,
    Currency: "INR",
    Markup: 0,
    Category: "Shopping",
  },
];

const categoryKeywords = {
  Food: [
    "swiggy",
    "zomato",
    "dominos",
    "mcdonald",
    "starbucks",
    "blinkit",
    "zepto",
  ],
  Shopping: [
    "amazon",
    "flipkart",
    "zara",
    "blinkit",
    "zepto",
    "bookmyshow",
  ],
  Entertainment: [
    "netflix",
    "spotify",
    "prime video",
    "bookmyshow",
  ],
  Travel: [
    "uber",
    "ola",
    "shell",
    "booking.com",
    "hotel booking",
  ],
  Bills: [
    "airtel",
    "jio",
    "bescom",
  ],
  Health: [
    "apollo pharmacy",
    "apollo hospital",
    "pharmacy",
  ],
  Education: [
    "coursera",
    "udemy",
  ],
};

function cleanMerchant(merchant) {
  if (!merchant) return "Unknown Merchant";

  let name = String(merchant).trim();

  name = name
    .replace(/[*#@]\w+/g, "")
    .replace(/\b\d{4,}\b/g, "")
    .replace(/\s+/g, " ")
    .trim();

  const upper = name.toUpperCase();

  const aliases = {
    AMAZON: "Amazon",
    "AMAZON UK": "Amazon",
    "AMAZON UK LTD": "Amazon",
    FLIPKART: "Flipkart",
    ZARA: "Zara",
    APPLE: "Apple",
    SWIGGY: "Swiggy",
    ZOMATO: "Zomato",
    BLINKIT: "Blinkit",
    ZEPTO: "Zepto",
    DOMINOS: "Dominos",
    STARBUCKS: "Starbucks",
    MCDONALD: "McDonald's",
    UBER: "Uber",
    OLA: "Ola",
    SHELL: "Shell",
    NETFLIX: "Netflix",
    SPOTIFY: "Spotify",
    "PRIME VIDEO": "Prime Video",
    BOOKMYSHOW: "BookMyShow",
    AIRTEL: "Airtel",
    JIO: "Jio",
    BESCOM: "BESCOM",
    "APOLLO PHARMACY": "Apollo Pharmacy",
    "APOLLO HOSPITAL": "Apollo Hospital",
    PHARMACY: "Pharmacy",
    COURSERA: "Coursera",
    UDEMY: "Udemy",
    "BOOKING.COM": "Booking.com",
    "BOOKING COM": "Booking.com",
    "HOTEL BOOKING": "Hotel Booking",
    OPENAI: "OpenAI",
  };

  for (const key of Object.keys(aliases)) {
    if (upper.includes(key)) {
      return aliases[key];
    }
  }

  return name
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getCategory(merchant, existingCategory = "") {
  if (existingCategory && existingCategory !== "Other") {
    return existingCategory;
  }

  const name = String(merchant || "").toLowerCase();

  for (const [category, keywords] of Object.entries(categoryKeywords)) {
    if (keywords.some((keyword) => name.includes(keyword))) {
      return category;
    }
  }

  return "Other";
}

function isCreditOrRefund(transaction) {
  const type = String(
    transaction.Type ?? transaction.type ?? ""
  ).toUpperCase();

  const merchant = String(
    transaction.Merchant ?? transaction.merchant ?? ""
  ).toLowerCase();

  const amount = Number(
    transaction.Amount ?? transaction.amount ?? 0
  );

  return (
    type === "CR" ||
    merchant.includes("refund") ||
    amount < 0
  );
}

function isMarkupTransaction(transaction) {
  const merchant = String(
    transaction.Merchant ?? transaction.merchant ?? ""
  ).toLowerCase();

  return (
    merchant.includes("markup") ||
    merchant.includes("forex") ||
    merchant.includes("fcy") ||
    merchant.includes("foreign transaction")
  );
}

function formatCurrency(value) {
  return `₹${Math.abs(Number(value || 0)).toLocaleString(
    "en-IN",
    {
      maximumFractionDigits: 2,
    }
  )}`;
}

function formatForeignAmount(value, currency) {
  return `${Math.abs(Number(value || 0)).toLocaleString(
    "en-IN",
    {
      maximumFractionDigits: 2,
    }
  )} ${currency || ""}`;
}

function getSubscriptionList(transactions) {
  const grouped = {};

  transactions.forEach((transaction) => {
    if (
      isCreditOrRefund(transaction) ||
      isMarkupTransaction(transaction)
    ) {
      return;
    }

    const merchant = cleanMerchant(
      transaction.Merchant ?? transaction.merchant
    );

    const amount = Number(
      transaction.Amount ?? transaction.amount ?? 0
    );

    if (!grouped[merchant]) {
      grouped[merchant] = {
        merchant,
        occurrences: 0,
        total: 0,
        amounts: [],
      };
    }

    grouped[merchant].occurrences += 1;
    grouped[merchant].total += Math.abs(amount);
    grouped[merchant].amounts.push(Math.abs(amount));
  });

  return Object.values(grouped)
    .filter((item) => {
      if (item.occurrences < 2) return false;

      const min = Math.min(...item.amounts);
      const max = Math.max(...item.amounts);

      return max === 0 || max / min <= 1.15;
    })
    .sort((a, b) => b.occurrences - a.occurrences);
}

export default function App() {
  const [activePage, setActivePage] = useState("home");

  const [transactions, setTransactions] =
      useState(sampleTransactions);

  const [selectedFile, setSelectedFile] =
      useState(null);

  const [uploadMessage, setUploadMessage] =
      useState("");

  const [uploading, setUploading] =
      useState(false);

  const [search, setSearch] = useState("");

  const [categoryFilter, setCategoryFilter] =
      useState("All");

  const [currencyFilter, setCurrencyFilter] =
      useState("All");

  const [monthFilter, setMonthFilter] =
      useState("All");

  const navigate = (page) => {
    setActivePage(page);
  };

  const analysedTransactions = useMemo(() => {
    return transactions.map((transaction) => ({
      ...transaction,
      Merchant: cleanMerchant(
          transaction.Merchant ??
          transaction.merchant
      ),
      Category: getCategory(
          transaction.Merchant ??
          transaction.merchant,
          transaction.Category ??
          transaction.category
      ),
    }));
  }, [transactions]);

  const inrTransactions = useMemo(() => {
    return analysedTransactions.filter(
        (transaction) =>
            String(
                transaction.Currency ??
                transaction.currency ??
                "INR"
            ).toUpperCase() === "INR"
    );
  }, [analysedTransactions]);

  const foreignTransactions = useMemo(() => {
    return analysedTransactions.filter(
        (transaction) => {
          const currency = String(
              transaction.Currency ??
              transaction.currency ??
              "INR"
          ).toUpperCase();

          return (
              currency !== "INR" &&
              !isMarkupTransaction(transaction) &&
              !isCreditOrRefund(transaction)
          );
        }
    );
  }, [analysedTransactions]);

  const totalSpending = useMemo(() => {
    return inrTransactions
        .filter(
            (transaction) =>
                !isMarkupTransaction(transaction)
        )
        .reduce((sum, transaction) => {
          const amount = Number(
              transaction.Amount ??
              transaction.amount ??
              0
          );

          return (
              sum +
              (isCreditOrRefund(transaction)
                  ? -Math.abs(amount)
                  : Math.abs(amount))
          );
        }, 0);
  }, [inrTransactions]);

  const totalMarkup = useMemo(() => {
    return analysedTransactions
        .filter(isMarkupTransaction)
        .reduce((sum, transaction) => {
          return (
              sum +
              Math.abs(
                  Number(
                      transaction.Amount ??
                      transaction.amount ??
                      0
                  )
              )
          );
        }, 0);
  }, [analysedTransactions]);

  const averageTransaction =
      inrTransactions.length > 0
          ? totalSpending /
          inrTransactions.filter(
              (transaction) =>
                  !isCreditOrRefund(transaction) &&
                  !isMarkupTransaction(transaction)
          ).length
          : 0;

  // =====================================================
  // FOREIGN MARKUP MATCHING
  // =====================================================

  const getForeignMarkup = (transaction) => {
    const merchant = cleanMerchant(
        transaction.Merchant ??
        transaction.merchant ??
        ""
    ).toLowerCase();

    const firstWord = merchant
        .split(/\s+/)[0]
        .toLowerCase();

    return analysedTransactions
        .filter((item) => {
          if (!isMarkupTransaction(item)) {
            return false;
          }

          const markupMerchant =
              cleanMerchant(
                  item.Merchant ??
                  item.merchant ??
                  ""
              ).toLowerCase();

          return (
              markupMerchant.includes(firstWord) ||
              firstWord.includes(
                  markupMerchant.split(/\s+/)[0]
              )
          );
        })
        .reduce((sum, item) => {
          return (
              sum +
              Math.abs(
                  Number(
                      item.Amount ??
                      item.amount ??
                      0
                  )
              )
          );
        }, 0);
  };

  const totalForeignMarkup = useMemo(() => {
    return analysedTransactions
        .filter(isMarkupTransaction)
        .reduce((sum, transaction) => {
          return (
              sum +
              Math.abs(
                  Number(
                      transaction.Amount ??
                      transaction.amount ??
                      0
                  )
              )
          );
        }, 0);
  }, [analysedTransactions]);

  const subscriptions = useMemo(
      () => getSubscriptionList(analysedTransactions),
      [analysedTransactions]
  );

  // =====================================================
  // CATEGORY DATA
  // =====================================================

  const categoryData = useMemo(() => {
    const grouped = {};

    inrTransactions.forEach((transaction) => {
      if (
          isMarkupTransaction(transaction) ||
          isCreditOrRefund(transaction)
      ) {
        return;
      }

      const category =
          transaction.Category ||
          transaction.category ||
          "Other";

      const amount = Math.abs(
          Number(
              transaction.Amount ??
              transaction.amount ??
              0
          )
      );

      grouped[category] =
          (grouped[category] || 0) + amount;
    });

    return Object.entries(grouped)
        .map(([category, amount]) => ({
          category,
          amount,
        }))
        .sort((a, b) => b.amount - a.amount);
  }, [inrTransactions]);

  // =====================================================
  // MONTHLY DATA
  // =====================================================

  const monthlyData = useMemo(() => {
    const grouped = {};

    inrTransactions.forEach((transaction) => {
      if (
          isMarkupTransaction(transaction) ||
          isCreditOrRefund(transaction)
      ) {
        return;
      }

      const date = new Date(
          transaction.Date ??
          transaction.date
      );

      if (Number.isNaN(date.getTime())) {
        return;
      }

      const month = date.toLocaleString(
          "en-US",
          {
            month: "short",
          }
      );

      grouped[month] =
          (grouped[month] || 0) +
          Math.abs(
              Number(
                  transaction.Amount ??
                  transaction.amount ??
                  0
              )
          );
    });

    return Object.entries(grouped).map(
        ([month, amount]) => ({
          month,
          amount,
        })
    );
  }, [inrTransactions]);

  // =====================================================
  // MERCHANT DATA
  // =====================================================

  const merchantData = useMemo(() => {
    const grouped = {};

    inrTransactions.forEach((transaction) => {
      if (
          isMarkupTransaction(transaction) ||
          isCreditOrRefund(transaction)
      ) {
        return;
      }

      const merchant = cleanMerchant(
          transaction.Merchant ??
          transaction.merchant
      );

      grouped[merchant] =
          (grouped[merchant] || 0) +
          Math.abs(
              Number(
                  transaction.Amount ??
                  transaction.amount ??
                  0
              )
          );
    });

    return Object.entries(grouped)
        .map(([merchant, amount]) => ({
          merchant,
          amount,
        }))
        .sort((a, b) => b.amount - a.amount)
        .slice(0, 8);
  }, [inrTransactions]);

  const filteredTransactions =
      analysedTransactions.filter(
          (transaction) => {
            const merchant = cleanMerchant(
                transaction.Merchant ??
                transaction.merchant
            );

            const category =
                transaction.Category ??
                transaction.category ??
                "Other";

            const currency = String(
                transaction.Currency ??
                transaction.currency ??
                "INR"
            ).toUpperCase();

            const date = new Date(
                transaction.Date ??
                transaction.date
            );

            const month = Number.isNaN(
                date.getTime()
            )
                ? ""
                : date.toLocaleString(
                    "en-US",
                    {
                      month: "short",
                    }
                );

            const matchesSearch =
                merchant
                    .toLowerCase()
                    .includes(
                        search.toLowerCase()
                    );

            const matchesCategory =
                categoryFilter === "All" ||
                category === categoryFilter;

            const matchesCurrency =
                currencyFilter === "All" ||
                currency === currencyFilter;

            const matchesMonth =
                monthFilter === "All" ||
                month === monthFilter;

            return (
                matchesSearch &&
                matchesCategory &&
                matchesCurrency &&
                matchesMonth
            );
          }
      );

  // =====================================================
  // FILE UPLOAD
  // =====================================================

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    setSelectedFile(file || null);
    setUploadMessage("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage(
          "Please select a CSV or PDF file."
      );
      return;
    }

    const formData = new FormData();

    formData.append(
        "file",
        selectedFile
    );

    try {
      setUploading(true);
      setUploadMessage(
          "Uploading and analysing statement..."
      );

      const response = await fetch(
          "http://127.0.0.1:8000/api/upload",
          {
            method: "POST",
            body: formData,
          }
      );

      const data =
          await response.json();

      if (!response.ok) {
        throw new Error(
            data.detail ||
            "Upload failed."
        );
      }

      if (
          Array.isArray(
              data.transactions
          )
      ) {
        setTransactions(
            data.transactions
        );
      }

      setUploadMessage(
          `✓ ${data.message}`
      );

      setActivePage("dashboard");
    } catch (error) {
      setUploadMessage(
          `Error: ${error.message}`
      );
    } finally {
      setUploading(false);
    }
  };

  // =====================================================
  // CSV DOWNLOAD
  // =====================================================

  const downloadCSV = () => {
    if (
        filteredTransactions.length ===
        0
    ) {
      return;
    }

    const headers = [
      "Date",
      "Merchant",
      "Amount",
      "Currency",
      "Markup",
      "Category",
    ];

    const rows =
        filteredTransactions.map(
            (transaction) => [
              transaction.Date ??
              transaction.date ??
              "",
              cleanMerchant(
                  transaction.Merchant ??
                  transaction.merchant
              ),
              transaction.Amount ??
              transaction.amount ??
              0,
              transaction.Currency ??
              transaction.currency ??
              "INR",
              transaction.Markup ??
              transaction.markup ??
              0,
              transaction.Category ??
              transaction.category ??
              "Other",
            ]
        );

    const csv = [
      headers,
      ...rows,
    ]
        .map((row) =>
            row
                .map((value) =>
                    `"${String(value).replace(
                        /"/g,
                        '""'
                    )}"`
                )
                .join(",")
        )
        .join("\n");

    const blob = new Blob(
        [csv],
        {
          type: "text/csv;charset=utf-8;",
        }
    );

    const url =
        URL.createObjectURL(blob);

    const link =
        document.createElement("a");

    link.href = url;
    link.download =
        "credit_card_transactions.csv";

    link.click();

    URL.revokeObjectURL(url);
  };

  // =====================================================
  // HOME PAGE
  // =====================================================

  function HomePage() {
    return (
        <main className="home-page">

          <section className="hero">

            <div className="hero-content">

            <span className="hero-badge">
              Smart Finance Analysis
            </span>

              <h1>
                Credit Card Statement
                <span> Analyser</span>
              </h1>

              <p>
                Upload your credit card
                statement and transform
                complex transactions into
                clear, meaningful spending
                insights.
              </p>

              <div className="hero-buttons">

                <button
                    className="primary-btn"
                    onClick={() =>
                        navigate("upload")
                    }
                >
                  Upload Statement
                </button>

                <button
                    className="secondary-btn"
                    onClick={() =>
                        navigate("dashboard")
                    }
                >
                  View Dashboard
                </button>

              </div>

            </div>

          </section>

          <section className="features">

            <div className="section-heading">
            <span>
              Powerful Features
            </span>

              <h2>
                Everything you need to
                understand your spending
              </h2>
            </div>

            <div className="feature-grid">

              <div className="feature-card">
                <div className="feature-icon">
                  📄
                </div>

                <h3>
                  Statement Analysis
                </h3>

                <p>
                  Extract transactions from
                  CSV and PDF statements
                  automatically.
                </p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">
                  🏷️
                </div>

                <h3>
                  Smart Categorisation
                </h3>

                <p>
                  Organise merchants into
                  useful spending categories.
                </p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">
                  📊
                </div>

                <h3>
                  Spending Insights
                </h3>

                <p>
                  Understand your monthly,
                  category and merchant
                  spending.
                </p>
              </div>

              <div className="feature-card">
                <div className="feature-icon">
                  🔁
                </div>

                <h3>
                  Subscription Detection
                </h3>

                <p>
                  Identify repeated payments
                  and possible subscriptions.
                </p>
              </div>

            </div>

          </section>

        </main>
    );
  }

  // =====================================================
  // UPLOAD PAGE
  // =====================================================

  function UploadPage() {
    return (
        <main className="page-container">

          <div className="page-heading">
          <span>
            Upload Statement
          </span>

            <h1>
              Analyse your statement
            </h1>

            <p>
              Upload a CSV or PDF credit
              card statement to begin.
            </p>
          </div>

          <div className="upload-card">

            <div className="upload-icon">
              📤
            </div>

            <h2>
              Select Statement
            </h2>

            <p>
              Supported formats:
              CSV and PDF
            </p>

            <input
                type="file"
                accept=".csv,.pdf"
                onChange={
                  handleFileChange
                }
            />

            {selectedFile && (
                <div className="selected-file">
                  Selected:
                  <strong>
                    {selectedFile.name}
                  </strong>
                </div>
            )}

            <button
                className="primary-btn"
                onClick={handleUpload}
                disabled={uploading}
            >
              {uploading
                  ? "Analysing..."
                  : "Upload & Analyse"}
            </button>

            {uploadMessage && (
                <p className="upload-message">
                  {uploadMessage}
                </p>
            )}

          </div>

        </main>
    );
  }

  // =====================================================
  // DASHBOARD PAGE
  // =====================================================

  function DashboardPage() {
    const maxCategory =
        Math.max(
            ...categoryData.map(
                (item) => item.amount
            ),
            1
        );

    const maxMonthly =
        Math.max(
            ...monthlyData.map(
                (item) => item.amount
            ),
            1
        );

    const maxMerchant =
        Math.max(
            ...merchantData.map(
                (item) => item.amount
            ),
            1
        );

    return (
        <main className="page-container">

          <div className="page-heading">
          <span>
            Financial Overview
          </span>

            <h1>
              Spending Dashboard
            </h1>

            <p>
              Get a clear view of your
              credit card spending.
            </p>
          </div>

          <section className="summary-grid">

            <div className="summary-card">
            <span>
              Total Spending
            </span>

              <h2>
                {formatCurrency(
                    totalSpending
                )}
              </h2>

              <small>
                INR transactions
              </small>
            </div>

            <div className="summary-card">
            <span>
              Transactions
            </span>

              <h2>
                {
                  analysedTransactions.filter(
                      (transaction) =>
                          !isMarkupTransaction(
                              transaction
                          )
                  ).length
                }
              </h2>

              <small>
                Analysed records
              </small>
            </div>

            <div className="summary-card">
            <span>
              Average Transaction
            </span>

              <h2>
                {formatCurrency(
                    averageTransaction
                )}
              </h2>

              <small>
                Per INR transaction
              </small>
            </div>

            <div className="summary-card">
            <span>
              Subscriptions
            </span>

              <h2>
                {subscriptions.length}
              </h2>

              <small>
                Possible recurring payments
              </small>
            </div>

          </section>

          {/* CATEGORY CHART */}

          <section className="chart-card">

            <div className="section-heading">
            <span>
              Spending Analysis
            </span>

              <h2>
                Spending by Category
              </h2>
            </div>

            <div className="bar-chart">

              {categoryData.length === 0 ? (
                  <p>
                    No category data available.
                  </p>
              ) : (
                  categoryData.map(
                      (item) => (
                          <div
                              className="bar-item"
                              key={item.category}
                          >

                            <div className="bar-label">

                      <span>
                        {item.category}
                      </span>

                              <span>
                        {formatCurrency(
                            item.amount
                        )}
                      </span>

                            </div>

                            <div className="bar-track">

                              <div
                                  className="bar-fill"
                                  style={{
                                    width: `${
                                        (item.amount /
                                            maxCategory) *
                                        100
                                    }%`,
                                  }}
                              />

                            </div>

                          </div>
                      )
                  )
              )}

            </div>

          </section>

          {/* MONTHLY CHART */}

          <section className="chart-card">

            <div className="section-heading">
            <span>
              Monthly Overview
            </span>

              <h2>
                Monthly Spending
              </h2>
            </div>

            <div className="monthly-chart">

              {monthlyData.map(
                  (item) => (
                      <div
                          className="month-bar"
                          key={item.month}
                      >

                        <div
                            className="month-bar-fill"
                            style={{
                              height: `${
                                  Math.max(
                                      8,
                                      (item.amount /
                                          maxMonthly) *
                                      100
                                  )
                              }%`,
                            }}
                        >
                    <span>
                      {formatCurrency(
                          item.amount
                      )}
                    </span>
                        </div>

                        <small>
                          {item.month}
                        </small>

                      </div>
                  )
              )}

            </div>

          </section>

          {/* MERCHANT CHART */}

          <section className="chart-card">

            <div className="section-heading">
            <span>
              Merchant Analysis
            </span>

              <h2>
                Top Merchants
              </h2>
            </div>

            <div className="bar-chart">

              {merchantData.map(
                  (item) => (
                      <div
                          className="bar-item"
                          key={item.merchant}
                      >

                        <div className="bar-label">

                    <span>
                      {item.merchant}
                    </span>

                          <span>
                      {formatCurrency(
                          item.amount
                      )}
                    </span>

                        </div>

                        <div className="bar-track">

                          <div
                              className="bar-fill merchant-bar-fill"
                              style={{
                                width: `${
                                    (item.amount /
                                        maxMerchant) *
                                    100
                                }%`,
                              }}
                          />

                        </div>

                      </div>
                  )
              )}

            </div>

          </section>

          {/* FOREIGN TRANSACTIONS */}

          <section className="chart-card">

            <div className="section-heading">
            <span>
              International Spending
            </span>

              <h2>
                Foreign Transactions
              </h2>
            </div>

            {foreignTransactions.length ===
            0 ? (
                <p>
                  No foreign transactions
                  found.
                </p>
            ) : (
                <div className="foreign-grid">

                  {foreignTransactions.map(
                      (transaction, index) => {

                        const currency =
                            transaction.Currency ??
                            transaction.currency ??
                            "";

                        const amount =
                            transaction.Amount ??
                            transaction.amount ??
                            0;

                        const markup =
                            getForeignMarkup(
                                transaction
                            );

                        return (
                            <div
                                className="foreign-card"
                                key={`${transaction.Merchant}-${index}`}
                            >

                              <div>
                        <span>
                          Merchant
                        </span>

                                <h3>
                                  {cleanMerchant(
                                      transaction.Merchant ??
                                      transaction.merchant
                                  )}
                                </h3>
                              </div>

                              <div>
                        <span>
                          Foreign Amount
                        </span>

                                <strong>
                                  {formatForeignAmount(
                                      amount,
                                      currency
                                  )}
                                </strong>
                              </div>

                              <div>
                        <span>
                          Markup
                        </span>

                                <strong>
                                  {formatCurrency(
                                      markup
                                  )}
                                </strong>
                              </div>

                            </div>
                        );
                      }
                  )}

                </div>
            )}

          </section>

          {/* TOTAL MARKUP */}

          <section className="summary-grid">

            <div className="summary-card">

            <span>
              Total Foreign Markup
            </span>

              <h2>
                {formatCurrency(
                    totalForeignMarkup
                )}
              </h2>

              <small>
                Separate markup transactions
              </small>

            </div>

          </section>

          <div className="dashboard-actions">

            <button
                className="primary-btn"
                onClick={downloadCSV}
            >
              Download CSV
            </button>

            <button
                className="secondary-btn"
                onClick={() =>
                    navigate("transactions")
                }
            >
              View Transactions
            </button>

          </div>

        </main>
    );
  }

  // =====================================================
  // TRANSACTIONS PAGE
  // =====================================================

  function TransactionsPage() {
    const categories = [
      "All",
      ...new Set(
          analysedTransactions.map(
              (transaction) =>
                  transaction.Category ||
                  transaction.category ||
                  "Other"
          )
      ),
    ];

    const currencies = [
      "All",
      ...new Set(
          analysedTransactions.map(
              (transaction) =>
                  String(
                      transaction.Currency ??
                      transaction.currency ??
                      "INR"
                  ).toUpperCase()
          )
      ),
    ];

    const months = [
      "All",
      ...new Set(
          analysedTransactions
              .map((transaction) => {
                const date = new Date(
                    transaction.Date ??
                    transaction.date
                );

                return Number.isNaN(
                    date.getTime()
                )
                    ? ""
                    : date.toLocaleString(
                        "en-US",
                        {
                          month: "short",
                        }
                    );
              })
              .filter(Boolean)
      ),
    ];

    return (
        <main className="page-container">

          <div className="page-heading">

          <span>
            Transaction Records
          </span>

            <h1>
              All Transactions
            </h1>

            <p>
              Search, filter and inspect
              your statement transactions.
            </p>

          </div>

          <section className="filters-card">

            <input
                type="text"
                placeholder="Search merchant..."
                value={search}
                onChange={(event) =>
                    setSearch(
                        event.target.value
                    )
                }
            />

            <select
                value={categoryFilter}
                onChange={(event) =>
                    setCategoryFilter(
                        event.target.value
                    )
                }
            >
              {categories.map(
                  (category) => (
                      <option
                          key={category}
                          value={category}
                      >
                        {category}
                      </option>
                  )
              )}
            </select>

            <select
                value={currencyFilter}
                onChange={(event) =>
                    setCurrencyFilter(
                        event.target.value
                    )
                }
            >
              {currencies.map(
                  (currency) => (
                      <option
                          key={currency}
                          value={currency}
                      >
                        {currency}
                      </option>
                  )
              )}
            </select>

            <select
                value={monthFilter}
                onChange={(event) =>
                    setMonthFilter(
                        event.target.value
                    )
                }
            >
              {months.map((month) => (
                  <option
                      key={month}
                      value={month}
                  >
                    {month}
                  </option>
              ))}
            </select>

          </section>

          <section className="table-card">

            <div className="table-header">

              <h2>
                Transactions
              </h2>

              <span>
              {filteredTransactions.length}{" "}
                records
            </span>

            </div>

            <div className="table-wrapper">

              <table>

                <thead>

                <tr>
                  <th>Date</th>
                  <th>Merchant</th>
                  <th>Amount</th>
                  <th>Currency</th>
                  <th>Markup</th>
                  <th>Category</th>
                </tr>

                </thead>

                <tbody>

                {filteredTransactions.map(
                    (transaction, index) => (
                        <tr
                            key={
                                transaction.transaction_id ??
                                index
                            }
                        >

                          <td>
                            {String(
                                transaction.Date ??
                                transaction.date ??
                                ""
                            ).slice(0, 10)}
                          </td>

                          <td>
                            {cleanMerchant(
                                transaction.Merchant ??
                                transaction.merchant
                            )}
                          </td>

                          <td>
                            {Number(
                                transaction.Amount ??
                                transaction.amount ??
                                0
                            ).toLocaleString(
                                "en-IN",
                                {
                                  maximumFractionDigits: 2,
                                }
                            )}
                          </td>

                          <td>
                            {String(
                                transaction.Currency ??
                                transaction.currency ??
                                "INR"
                            ).toUpperCase()}
                          </td>

                          <td>
                            ₹
                            {Number(
                                transaction.Markup ??
                                transaction.markup ??
                                0
                            ).toLocaleString(
                                "en-IN",
                                {
                                  maximumFractionDigits: 2,
                                }
                            )}
                          </td>

                          <td>
                        <span className="category-badge">
                          {transaction.Category ??
                              transaction.category ??
                              "Other"}
                        </span>
                          </td>

                        </tr>
                    )
                )}

                </tbody>

              </table>

            </div>

          </section>

        </main>
    );
  }

  // =====================================================
  // SUBSCRIPTIONS PAGE
  // =====================================================

  function SubscriptionsPage() {
    return (
        <main className="page-container">

          <div className="page-heading">

          <span>
            Recurring Payments
          </span>

            <h1>
              Subscriptions
            </h1>

            <p>
              Repeated transactions that
              may represent subscriptions.
            </p>

          </div>

          {subscriptions.length === 0 ? (
              <section className="empty-card">

                <div className="feature-icon">
                  🔍
                </div>

                <h2>
                  No recurring subscriptions
                  detected
                </h2>

                <p>
                  Upload a statement with
                  repeated payments to detect
                  subscriptions.
                </p>

              </section>
          ) : (
              <div className="subscription-grid">

                {subscriptions.map(
                    (subscription) => (
                        <div
                            className="subscription-card"
                            key={
                              subscription.merchant
                            }
                        >

                          <div className="subscription-icon">
                            🔁
                          </div>

                          <h3>
                            {subscription.merchant}
                          </h3>

                          <p>
                            {subscription.occurrences}{" "}
                            repeated payments
                          </p>

                          <strong>
                            {formatCurrency(
                                subscription.total
                            )}
                          </strong>

                        </div>
                    )
                )}

              </div>
          )}

        </main>
    );
  }

  // =====================================================
  // PAGE SWITCH
  // =====================================================

  function renderPage() {
    if (activePage === "upload") {
      return <UploadPage/>;
    }

    if (activePage === "dashboard") {
      return <DashboardPage/>;
    }

    if (activePage === "transactions") {
      return <TransactionsPage/>;
    }

    if (activePage === "subscriptions") {
      return <SubscriptionsPage/>;
    }

    return <HomePage/>;
  }

  // =====================================================
  // MAIN RETURN
  // =====================================================

  return (
      <div className="app">

        <header className="navbar">

          <div
              className="logo"
              onClick={() =>
                  navigate("home")
              }
          >

          <span className="logo-icon">
            💳
          </span>

            <div>

              <strong>
                Credit Card
              </strong>

              <small>
                Statement Analyser
              </small>

            </div>

          </div>

          <nav>

            <button
                className={
                  activePage === "home"
                      ? "active"
                      : ""
                }
                onClick={() =>
                    navigate("home")
                }
            >
              Home
            </button>

            <button
                className={
                  activePage === "upload"
                      ? "active"
                      : ""
                }
                onClick={() =>
                    navigate("upload")
                }
            >
              Upload
            </button>

            <button
                className={
                  activePage === "dashboard"
                      ? "active"
                      : ""
                }
                onClick={() =>
                    navigate("dashboard")
                }
            >
              Dashboard
            </button>

            <button
                className={
                  activePage === "transactions"
                      ? "active"
                      : ""
                }
                onClick={() =>
                    navigate("transactions")
                }
            >
              Transactions
            </button>

            <button
                className={
                  activePage === "subscriptions"
                      ? "active"
                      : ""
                }
                onClick={() =>
                    navigate("subscriptions")
                }
            >
              Subscriptions
            </button>

          </nav>

        </header>

        {renderPage()}

        <footer className="footer">

          <div>

            <strong>
              💳 Credit Card Statement
              Analyser
            </strong>

            <p>
              Smart financial analysis
              made simple.
            </p>

          </div>

          <p>
            © 2026 Credit Card
            Statement Analyser
          </p>

        </footer>

      </div>
  );
}

