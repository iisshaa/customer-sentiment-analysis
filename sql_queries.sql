-- ============================================================
-- Marketing Analytics Project - SQL Queries
-- Database: marketing_analytics.db (SQLite)
-- Author: Isha Roshan | Data Analyst Portfolio Project
-- ============================================================


-- ============================================================
-- QUERY 1: Data Cleaning Check - Null values & Duplicates
-- ============================================================
-- Check for nulls
SELECT
    COUNT(*) AS Total_Records,
    COUNT(ReviewID) AS Non_Null_ReviewID,
    COUNT(ReviewText) AS Non_Null_ReviewText,
    COUNT(Rating) AS Non_Null_Rating
FROM customer_reviews;

-- Check for duplicate ReviewIDs
SELECT ReviewID, COUNT(*) AS cnt
FROM customer_reviews
GROUP BY ReviewID
HAVING cnt > 1;


-- ============================================================
-- QUERY 2: Overall KPIs
-- ============================================================
SELECT
    COUNT(*)                                        AS Total_Reviews,
    ROUND(AVG(Rating), 2)                           AS Avg_Rating,
    ROUND(AVG(Compound), 3)                         AS Avg_Sentiment_Score,
    SUM(CASE WHEN FinalSentiment = 'Positive' THEN 1 ELSE 0 END)  AS Positive_Count,
    SUM(CASE WHEN FinalSentiment = 'Neutral'  THEN 1 ELSE 0 END)  AS Neutral_Count,
    SUM(CASE WHEN FinalSentiment = 'Negative' THEN 1 ELSE 0 END)  AS Negative_Count,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment = 'Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Positive_Pct,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment = 'Negative' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Negative_Pct
FROM customer_reviews;


-- ============================================================
-- QUERY 3: Sentiment by Product (for Power BI bar chart)
-- ============================================================
SELECT
    ProductName,
    Category,
    COUNT(*)                                        AS Total_Reviews,
    ROUND(AVG(Rating), 2)                           AS Avg_Rating,
    ROUND(AVG(Compound), 3)                         AS Avg_Sentiment_Score,
    SUM(CASE WHEN FinalSentiment = 'Positive' THEN 1 ELSE 0 END) AS Positive,
    SUM(CASE WHEN FinalSentiment = 'Neutral'  THEN 1 ELSE 0 END) AS Neutral,
    SUM(CASE WHEN FinalSentiment = 'Negative' THEN 1 ELSE 0 END) AS Negative,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment = 'Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Positive_Pct
FROM customer_reviews
GROUP BY ProductName, Category
ORDER BY Avg_Sentiment_Score DESC;


-- ============================================================
-- QUERY 4: Monthly Sentiment Trend (for time series visual)
-- ============================================================
SELECT
    Month,
    MonthName,
    COUNT(*)                                        AS Total_Reviews,
    ROUND(AVG(Rating), 2)                           AS Avg_Rating,
    ROUND(AVG(Compound), 3)                         AS Avg_Sentiment_Score,
    SUM(CASE WHEN FinalSentiment = 'Positive' THEN 1 ELSE 0 END) AS Positive,
    SUM(CASE WHEN FinalSentiment = 'Negative' THEN 1 ELSE 0 END) AS Negative
FROM customer_reviews
GROUP BY Month, MonthName
ORDER BY Month;


-- ============================================================
-- QUERY 5: Channel Performance Analysis
-- ============================================================
SELECT
    Channel,
    COUNT(*)                                        AS Total_Reviews,
    ROUND(AVG(Rating), 2)                           AS Avg_Rating,
    ROUND(AVG(Compound), 3)                         AS Avg_Sentiment_Score,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment = 'Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Positive_Pct,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment = 'Negative' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Negative_Pct
FROM customer_reviews
GROUP BY Channel
ORDER BY Avg_Sentiment_Score DESC;


-- ============================================================
-- QUERY 6: Country-wise Review Volume (for map visual)
-- ============================================================
SELECT
    Country,
    COUNT(*)                                        AS Total_Reviews,
    ROUND(AVG(Rating), 2)                           AS Avg_Rating,
    ROUND(AVG(Compound), 3)                         AS Avg_Sentiment_Score,
    ROUND(100.0 * SUM(CASE WHEN FinalSentiment = 'Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS Positive_Pct
FROM customer_reviews
GROUP BY Country
ORDER BY Total_Reviews DESC;


-- ============================================================
-- QUERY 7: Negative Reviews Drill-Down (for stakeholders)
-- ============================================================
SELECT
    ReviewID,
    ProductName,
    Channel,
    Country,
    Rating,
    ReviewText,
    Compound AS Sentiment_Score,
    ReviewDate
FROM customer_reviews
WHERE FinalSentiment = 'Negative'
ORDER BY Compound ASC
LIMIT 20;


-- ============================================================
-- QUERY 8: CTE - Ranking products by sentiment score
-- ============================================================
WITH ProductSentiment AS (
    SELECT
        ProductName,
        COUNT(*)             AS Total_Reviews,
        ROUND(AVG(Compound), 3) AS Avg_Sentiment_Score,
        ROUND(AVG(Rating), 2)   AS Avg_Rating
    FROM customer_reviews
    GROUP BY ProductName
)
SELECT
    ProductName,
    Total_Reviews,
    Avg_Sentiment_Score,
    Avg_Rating,
    RANK() OVER (ORDER BY Avg_Sentiment_Score DESC) AS Sentiment_Rank
FROM ProductSentiment;


-- ============================================================
-- QUERY 9: Window Function - Running average sentiment by month
-- ============================================================
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
ORDER BY Month;
