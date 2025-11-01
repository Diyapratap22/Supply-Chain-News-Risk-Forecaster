import streamlit as st
import pandas as pd
import os
import sys
from src.exception import CustomException
from src.logger import logging

# This is the path to your final data
PROCESSED_FILE_PATH = os.path.join('artifacts', 'processed_articles.csv')

# --- Page Setup ---
st.set_page_config(
    page_title="Supply Chain Risk Forecaster",
    page_icon="📈",
    layout="wide"
)

# --- Helper Function for Colors ---
def get_risk_color(score):
    """Returns a CSS color based on the risk score."""
    score = float(score)
    if score >= 5:
        return "#D9534F" # Red (High Risk)
    elif score >= 3:
        return "#F0AD4E" # Orange (Medium Risk)
    else:
        return "#5CB85C" # Green (Low Risk)

# --- Function to load data ---
@st.cache_data
def load_data():
    if not os.path.exists(PROCESSED_FILE_PATH):
        logging.error(f"Processed file not found at: {PROCESSED_FILE_PATH}")
        st.error("Error: Processed data file not found. Please run the data pipeline.")
        return pd.DataFrame()
        
    df = pd.read_csv(PROCESSED_FILE_PATH)
    # Filter for articles that have ANY risk
    df_display = df[df['risk_score'] > 0].copy()
    
    articles_processed = []
    for article in df_display.to_dict('records'):
        entity_str = article['entities']
        entity_str_cleaned = entity_str.replace("'", "").replace("[", "").replace("]", "")
        entity_list = [e.strip() for e in entity_str_cleaned.split(',') if e.strip()]
        article['entities'] = entity_list 
        article['publishedAt'] = article['publishedAt'].split('T')[0]
        articles_processed.append(article)
    
    df_processed = pd.DataFrame(articles_processed)
    
    if not df_processed.empty:
        df_processed['publishedAt'] = pd.to_datetime(df_processed['publishedAt'])
    
    return df_processed

# --- Main App ---
try:
    df_articles = load_data()

    # --- Title ---
    st.title("Supply Chain Risk Forecaster 📈")
    st.markdown("This dashboard pulls live news and uses NLP to score supply chain risk.")

    if not df_articles.empty:
        # --- Metrics (The "Fancy" KPIs) ---
        st.header("Top-Level Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        total_risk_articles = len(df_articles)
        avg_risk_score = round(df_articles['risk_score'].mean(), 2)
        top_source = df_articles['source'].mode()[0]
        
        # --- Custom HTML Metrics for Colors ---
        col1.markdown("### High-Risk Articles")
        col1.markdown(f"<h1 style='color: #D9534F; text-align: left; font-size: 3.5em;'>{total_risk_articles}</h1>", unsafe_allow_html=True)

        avg_score_color = get_risk_color(avg_risk_score)
        col2.markdown("### Average Risk Score")
        col2.markdown(f"<h1 style='color: {avg_score_color}; text-align: left; font-size: 3.5em;'>{avg_risk_score}</h1>", unsafe_allow_html=True)
        
        col3.markdown("### Most Frequent Source")
        col3.markdown(f"<h1 style='color: #333; text-align: left; font-size: 2.5em; padding-top: 15px;'>{top_source}</h1>", unsafe_allow_html=True)


        # --- Charts ---
        st.header("Risk Analysis")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Top 5 Risky Sources")
            # This chart shows which news source reports the most risk
            top_sources = df_articles.groupby('source')['risk_score'].sum().nlargest(5)
            st.bar_chart(top_sources)

        with col_chart2:
            # --- MODIFIED CHART: Risk Score Distribution ---
            st.subheader("Distribution of Risk Scores")
            # This chart shows how many articles we found for each score
            score_counts = df_articles['risk_score'].value_counts().sort_index()
            st.bar_chart(score_counts) 

        # --- Data Table (Your Original List) ---
        st.header("High-Risk Articles Feed")
        
        df_feed = df_articles.sort_values(by='publishedAt', ascending=False)
        
        for index, row in df_feed.iterrows():
            # Get the correct color (red, orange, or green)
            risk_color = get_risk_color(row['risk_score'])
            
            st.markdown(f"### [{row['title']}]({row['url']})")
            
            st.markdown(f"""
                <span style='color: {risk_color} !important; font-size: 1.1em; font-weight: bold;'>Risk: {row['risk_score']}</span> | 
                <strong>Source:</strong> {row['source']} | 
                <strong>Published:</strong> {row['publishedAt'].strftime('%Y-%m-%d')}
            """, unsafe_allow_html=True)
            
            st.write(row['description'])
            
            st.multiselect(
                f"Entities for '{row['title'][:50]}...'", 
                options=row['entities'], 
                default=row['entities'],
                key=f"entities_{index}"
            )
            st.markdown("---")
            
    else:
        # We'll use a green "success" box for no risk
        st.success("No high-risk articles found. The supply chain looks clear! ✅")

except Exception as e:
    st.error("An error occurred while loading the dashboard.")
    st.exception(e)