# Customer Sentiment Analysis & Insight Dashboard

NLP pipeline that classifies customer product reviews into Positive / Neutral / Negative sentiment, blending lexicon-based scoring (VADER) with a supervised ML model (TF-IDF + Logistic Regression), then exports results to SQLite for Power BI reporting.

## Overview

This project analyzes 500 customer reviews across 5 products and 4 sales channels to surface sentiment trends, product-level satisfaction, and channel performance — replacing manual review analysis with a scalable, queryable pipeline feeding a Power BI dashboard.

## Tech Stack

- **Python**: Pandas, NumPy, Scikit-learn
- **NLP**: VADER (lexicon-based sentiment scoring)
- **ML**: TF-IDF vectorization + Logistic Regression
- **Database**: SQLite
- **Visualization**: Power BI

## Approach

1. **Data Cleaning** — text normalization (lowercasing, punctuation removal), date parsing, ground-truth sentiment labels derived from star ratings.
2. **VADER Sentiment Scoring** — compound polarity score on raw review text, mapped to Positive/Neutral/Negative.
3. **ML Classification** — TF-IDF (unigrams + bigrams, 500 features) fed into a Logistic Regression classifier trained on rating-derived labels.
4. **Final Sentiment Logic** — ML prediction is used when model confidence ≥ 70%, otherwise falls back to VADER's score — combining the precision of a trained classifier with the coverage of a lexicon-based fallback.
5. **KPI Aggregation** — review volume, average rating, sentiment %, and rolling 3-month sentiment trend, computed both in Python and via SQL (CTEs + window functions).
6. **Export** — final dataset and KPI summary tables written to SQLite (`marketing_analytics.db`) for direct Power BI connection.

## Key Results

- Classified 500 reviews across 5 products and 4 channels into Positive / Neutral / Negative sentiment
- Logistic Regression + TF-IDF model evaluated against rating-derived ground truth on a held-out test split
- Built 9 analytical SQL queries including product sentiment ranking (`RANK()`) and 3-month rolling sentiment average (window functions)
- Identified lowest-performing product/channel combinations to flag for stakeholder review

## Project Structure

```
.
├── data/
│   └── customer_reviews_raw.csv     # Raw review dataset (500 reviews)
├── sentiment_analysis.py            # Main pipeline: clean → VADER → ML → export
├── sql_queries.sql                  # 9 analytical SQL queries (KPIs, trends, rankings)
├── sqlite_runner.py                 # Executes all SQL queries, saves results to /sql_outputs
├── sql_outputs/                     # Query results as CSV (generated)
├── requirements.txt
└── .gitignore
```

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the sentiment pipeline (cleans data, runs VADER + ML, exports to SQLite)
python sentiment_analysis.py

# 3. Run all SQL analysis queries against the generated database
python sqlite_runner.py
```

This produces:
- `marketing_analytics.db` — SQLite database with `customer_reviews` and `kpi_summary` tables
- `sentiment_results.csv` — full dataset with sentiment labels
- `sql_outputs/*.csv` — results of each analytical query

Connect `marketing_analytics.db` directly to Power BI (or Tableau) as a data source to build the dashboard.

## Dashboard

The Power BI dashboard built on top of this data includes:
- Sentiment trend over time (with 3-month rolling average)
- Product-level sentiment and rating breakdown
- Channel performance comparison
- Negative review drill-down table for stakeholder action

## Author

**Isha Roshan**
[GitHub](https://github.com/iisshaa) • [LinkedIn](https://linkedin.com/in/isha-roshan-949b931b1/)
