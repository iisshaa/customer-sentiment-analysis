# ============================================================
# Marketing Analytics - SQLite Full Workflow
# Run all SQL queries and export results to CSV
# Author: Isha Roshan | Data Analyst Portfolio Project
# ============================================================

import sqlite3
import pandas as pd
import os

DB_PATH = 'marketing_analytics.db'
OUTPUT_DIR = 'sql_outputs'
os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# ---- Helper: run query, print result, save CSV ----
def run_query(name, sql, save=True):
    print(f"\n{'='*55}")
    print(f"  {name}")
    print('='*55)
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    if save:
        fname = f"{OUTPUT_DIR}/{name.replace(' ','_').replace(':','').lower()}.csv"
        df.to_csv(fname, index=False)
        print(f"  → Saved: {fname}")
    return df


# ============================================================
# Q1: Overall KPIs
# ============================================================
run_query("Q1: Overall KPIs", """
SELECT
    COUNT(*)                                                     AS Total_Reviews,
    ROUND(AVG(Rating), 2)                                        AS Avg_Rating,
    ROUND(AVG(Compound), 3)                                      AS Avg_Sentiment_Score,
    SUM(CASE WHEN FinalSentiment='Positive' THEN 1 ELSE 0 END)  AS Positive_Count,
    SUM(CASE WHEN FinalSentiment='Neutral'  THEN 1 ELSE 0 END)  AS Neutral_Count,
    SUM(CASE WHEN FinalSentiment='Negative' THEN 1 ELSE 0 END)  AS Negative_Count,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment='Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Positive_Pct,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment='Negative' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Negative_Pct
FROM customer_reviews
""")


# ============================================================
# Q2: Sentiment by Product
# ============================================================
run_query("Q2: Sentiment by Product", """
SELECT
    ProductName,
    Category,
    COUNT(*)                                                        AS Total_Reviews,
    ROUND(AVG(Rating), 2)                                           AS Avg_Rating,
    ROUND(AVG(Compound), 3)                                         AS Avg_Sentiment_Score,
    SUM(CASE WHEN FinalSentiment='Positive' THEN 1 ELSE 0 END)     AS Positive,
    SUM(CASE WHEN FinalSentiment='Neutral'  THEN 1 ELSE 0 END)     AS Neutral,
    SUM(CASE WHEN FinalSentiment='Negative' THEN 1 ELSE 0 END)     AS Negative,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment='Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Positive_Pct
FROM customer_reviews
GROUP BY ProductName, Category
ORDER BY Avg_Sentiment_Score DESC
""")


# ============================================================
# Q3: Monthly Trend
# ============================================================
run_query("Q3: Monthly Sentiment Trend", """
SELECT
    Month,
    MonthName,
    COUNT(*)                                                      AS Total_Reviews,
    ROUND(AVG(Rating), 2)                                         AS Avg_Rating,
    ROUND(AVG(Compound), 3)                                       AS Avg_Sentiment_Score,
    SUM(CASE WHEN FinalSentiment='Positive' THEN 1 ELSE 0 END)   AS Positive,
    SUM(CASE WHEN FinalSentiment='Negative' THEN 1 ELSE 0 END)   AS Negative
FROM customer_reviews
GROUP BY Month, MonthName
ORDER BY Month
""")


# ============================================================
# Q4: Channel Performance
# ============================================================
run_query("Q4: Channel Performance", """
SELECT
    Channel,
    COUNT(*)                                                      AS Total_Reviews,
    ROUND(AVG(Rating), 2)                                         AS Avg_Rating,
    ROUND(AVG(Compound), 3)                                       AS Avg_Sentiment_Score,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment='Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Positive_Pct,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment='Negative' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Negative_Pct
FROM customer_reviews
GROUP BY Channel
ORDER BY Avg_Sentiment_Score DESC
""")


# ============================================================
# Q5: Country Breakdown
# ============================================================
run_query("Q5: Country Breakdown", """
SELECT
    Country,
    COUNT(*)                                                      AS Total_Reviews,
    ROUND(AVG(Rating), 2)                                         AS Avg_Rating,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment='Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Positive_Pct
FROM customer_reviews
GROUP BY Country
ORDER BY Total_Reviews DESC
""")


# ============================================================
# Q6: CTE — Product Sentiment Ranking
# ============================================================
run_query("Q6: CTE Product Sentiment Ranking", """
WITH ProductSentiment AS (
    SELECT
        ProductName,
        COUNT(*)                AS Total_Reviews,
        ROUND(AVG(Compound),3)  AS Avg_Sentiment_Score,
        ROUND(AVG(Rating),2)    AS Avg_Rating
    FROM customer_reviews
    GROUP BY ProductName
)
SELECT
    ProductName,
    Total_Reviews,
    Avg_Sentiment_Score,
    Avg_Rating,
    RANK() OVER (ORDER BY Avg_Sentiment_Score DESC) AS Sentiment_Rank
FROM ProductSentiment
ORDER BY Sentiment_Rank
""")


# ============================================================
# Q7: Window Function — 3-Month Rolling Avg Sentiment
# ============================================================
run_query("Q7: 3-Month Rolling Avg Sentiment", """
WITH MonthlyAvg AS (
    SELECT
        Month,
        MonthName,
        ROUND(AVG(Compound), 3) AS Monthly_Avg_Sentiment
    FROM customer_reviews
    GROUP BY Month, MonthName
)
SELECT
    Month,
    MonthName,
    Monthly_Avg_Sentiment,
    ROUND(AVG(Monthly_Avg_Sentiment) OVER (
        ORDER BY Month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 3) AS Rolling_3Month_Avg
FROM MonthlyAvg
ORDER BY Month
""")


# ============================================================
# Q8: Negative Reviews Drill-Down (Stakeholder table)
# ============================================================
run_query("Q8: Negative Reviews Drill Down", """
SELECT
    ReviewID,
    ProductName,
    Channel,
    Country,
    Rating,
    ReviewText,
    ROUND(Compound,3) AS Sentiment_Score,
    ReviewDate
FROM customer_reviews
WHERE FinalSentiment = 'Negative'
ORDER BY Compound ASC
LIMIT 15
""")


# ============================================================
# Q9: Quarterly Summary (for Power BI slicer)
# ============================================================
run_query("Q9: Quarterly Summary", """
SELECT
    'Q' || Quarter                                                AS Quarter,
    COUNT(*)                                                      AS Total_Reviews,
    ROUND(AVG(Rating), 2)                                         AS Avg_Rating,
    ROUND(AVG(Compound), 3)                                       AS Avg_Sentiment,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment='Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Positive_Pct,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment='Negative' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Negative_Pct
FROM customer_reviews
GROUP BY Quarter
ORDER BY Quarter
""")

conn.close()
print(f"\n{'='*55}")
print("  All queries done! CSVs saved to: sql_outputs/")
print("  Connect marketing_analytics.db to Power BI next.")
print('='*55)
