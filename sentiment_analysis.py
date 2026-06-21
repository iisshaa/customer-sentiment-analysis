# ============================================================
# Marketing Analytics Project - Sentiment Analysis
# Tools: Python (VADER + ML), SQL, Power BI
# Author: Isha Roshan | Data Analyst Portfolio Project
# ============================================================

import pandas as pd
import numpy as np
import re
import warnings
warnings.filterwarnings('ignore')

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import sqlite3

# ============================================================
# STEP 1: LOAD & EXPLORE DATA
# ============================================================
print("=" * 55)
print("STEP 1: Loading and Exploring Data")
print("=" * 55)

df = pd.read_csv('data/customer_reviews_raw.csv')
print(f"Shape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nMissing values:\n{df.isnull().sum()}")
print(f"\nRating distribution:\n{df['Rating'].value_counts().sort_index()}")


# ============================================================
# STEP 2: DATA CLEANING
# ============================================================
print("\n" + "=" * 55)
print("STEP 2: Data Cleaning")
print("=" * 55)

def clean_text(text):
    """Clean review text for NLP analysis"""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)   # remove punctuation/numbers
    text = re.sub(r'\s+', ' ', text).strip()    # remove extra whitespace
    return text

df['CleanedReview'] = df['ReviewText'].apply(clean_text)
df['ReviewDate'] = pd.to_datetime(df['ReviewDate'])
df['Month'] = df['ReviewDate'].dt.month
df['MonthName'] = df['ReviewDate'].dt.strftime('%b')
df['Quarter'] = df['ReviewDate'].dt.quarter

# Actual sentiment label from rating (ground truth)
def rating_to_sentiment(rating):
    if rating >= 4:
        return 'Positive'
    elif rating == 3:
        return 'Neutral'
    else:
        return 'Negative'

df['ActualSentiment'] = df['Rating'].apply(rating_to_sentiment)
print("Data cleaned successfully.")
print(f"Actual sentiment distribution:\n{df['ActualSentiment'].value_counts()}")


# ============================================================
# STEP 3: VADER SENTIMENT ANALYSIS
# ============================================================
print("\n" + "=" * 55)
print("STEP 3: VADER Sentiment Analysis")
print("=" * 55)

analyzer = SentimentIntensityAnalyzer()

def get_vader_scores(text):
    scores = analyzer.polarity_scores(text)
    return scores['compound'], scores['pos'], scores['neu'], scores['neg']

def vader_label(compound):
    if compound >= 0.05:
        return 'Positive'
    elif compound <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

scores = df['ReviewText'].apply(lambda x: pd.Series(get_vader_scores(x),
    index=['Compound', 'Positive_Score', 'Neutral_Score', 'Negative_Score']))
df = pd.concat([df, scores], axis=1)
df['VADER_Sentiment'] = df['Compound'].apply(vader_label)

vader_acc = accuracy_score(df['ActualSentiment'], df['VADER_Sentiment'])
print(f"VADER Accuracy: {vader_acc:.2%}")
print(f"\nVADER Sentiment Distribution:\n{df['VADER_Sentiment'].value_counts()}")


# ============================================================
# STEP 4: ML MODEL - LOGISTIC REGRESSION (TFIDF)
# ============================================================
print("\n" + "=" * 55)
print("STEP 4: ML Model - Logistic Regression + TF-IDF")
print("=" * 55)

X = df['CleanedReview']
y = df['ActualSentiment']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words='english')
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

lr_model = LogisticRegression(max_iter=500, random_state=42)
lr_model.fit(X_train_tfidf, y_train)
y_pred = lr_model.predict(X_test_tfidf)

ml_acc = accuracy_score(y_test, y_pred)
print(f"ML Model Accuracy: {ml_acc:.2%}")
print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")

# Predict on full dataset
X_full_tfidf = tfidf.transform(df['CleanedReview'])
df['ML_Sentiment'] = lr_model.predict(X_full_tfidf)
df['ML_Confidence'] = lr_model.predict_proba(X_full_tfidf).max(axis=1).round(3)


# ============================================================
# STEP 5: FINAL SENTIMENT (ML overrides VADER where confident)
# ============================================================
def final_sentiment(row):
    if row['ML_Confidence'] >= 0.70:
        return row['ML_Sentiment']
    return row['VADER_Sentiment']

df['FinalSentiment'] = df.apply(final_sentiment, axis=1)
print(f"\nFinal Sentiment Distribution:\n{df['FinalSentiment'].value_counts()}")


# ============================================================
# STEP 6: KPI CALCULATIONS
# ============================================================
print("\n" + "=" * 55)
print("STEP 5: Key KPIs")
print("=" * 55)

total_reviews = len(df)
avg_rating = df['Rating'].mean()
positive_pct = (df['FinalSentiment'] == 'Positive').mean() * 100
negative_pct = (df['FinalSentiment'] == 'Negative').mean() * 100
sentiment_score = df['Compound'].mean()

print(f"Total Reviews     : {total_reviews}")
print(f"Average Rating    : {avg_rating:.2f} / 5.0")
print(f"Positive Reviews  : {positive_pct:.1f}%")
print(f"Negative Reviews  : {negative_pct:.1f}%")
print(f"Avg Sentiment Score: {sentiment_score:.3f}")

print("\n--- By Product ---")
prod_summary = df.groupby('ProductName').agg(
    Avg_Rating=('Rating', 'mean'),
    Total_Reviews=('ReviewID', 'count'),
    Positive_Count=('FinalSentiment', lambda x: (x == 'Positive').sum()),
    Avg_Compound=('Compound', 'mean')
).round(2)
prod_summary['Positive_Pct'] = (prod_summary['Positive_Count'] / prod_summary['Total_Reviews'] * 100).round(1)
print(prod_summary)

print("\n--- By Channel ---")
channel_summary = df.groupby('Channel').agg(
    Total_Reviews=('ReviewID', 'count'),
    Avg_Rating=('Rating', 'mean'),
    Avg_Compound=('Compound', 'mean')
).round(2)
print(channel_summary)


# ============================================================
# STEP 7: EXPORT TO CSV + SQLITE (for Power BI connection)
# ============================================================
print("\n" + "=" * 55)
print("STEP 6: Exporting Data")
print("=" * 55)

output_cols = [
    'ReviewID', 'CustomerID', 'ProductName', 'Category', 'Rating',
    'ReviewText', 'CleanedReview', 'ReviewDate', 'Month', 'MonthName',
    'Quarter', 'Channel', 'Country', 'Compound', 'Positive_Score',
    'Negative_Score', 'VADER_Sentiment', 'ML_Sentiment', 'ML_Confidence',
    'FinalSentiment', 'ActualSentiment'
]

df_out = df[output_cols].copy()

# CSV export
df_out.to_csv('sentiment_results.csv', index=False)
print("Exported: sentiment_results.csv")

# SQLite export (connect Power BI directly to this)
conn = sqlite3.connect('marketing_analytics.db')
df_out.to_sql('customer_reviews', conn, if_exists='replace', index=False)

# Also store KPI summary table
kpi_df = df.groupby(['ProductName', 'Category', 'Channel']).agg(
    Total_Reviews=('ReviewID', 'count'),
    Avg_Rating=('Rating', 'mean'),
    Positive_Reviews=('FinalSentiment', lambda x: (x == 'Positive').sum()),
    Negative_Reviews=('FinalSentiment', lambda x: (x == 'Negative').sum()),
    Neutral_Reviews=('FinalSentiment', lambda x: (x == 'Neutral').sum()),
    Avg_Sentiment_Score=('Compound', 'mean')
).round(3).reset_index()
kpi_df['Positive_Pct'] = (kpi_df['Positive_Reviews'] / kpi_df['Total_Reviews'] * 100).round(1)
kpi_df.to_sql('kpi_summary', conn, if_exists='replace', index=False)
conn.close()
print("Exported: marketing_analytics.db (SQLite)")
print("\nDone! All outputs ready for Power BI.")
