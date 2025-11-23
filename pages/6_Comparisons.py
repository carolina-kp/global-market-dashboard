import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.title("Multi-Ticker Comparison")

symbols = st.text_input("Tickers (comma separated)", "NVDA, AAPL, MSFT")

# Time range selector
time_options = {
    "1 Month": 30,
    "3 Months": 90,
    "6 Months": 180,
    "1 Year": 365,
    "2 Years": 365 * 2,
    "5 Years": 365 * 5,
    "MAX": None
}

selected_range = st.selectbox("Select Time Range", list(time_options.keys()))

if st.button("Compare"):
    tickers = [s.strip().upper() for s in symbols.split(",")]

    # Determine start date
    end_date = datetime.now()
    days = time_options[selected_range]

    if days is None:  # MAX
        start_date = "1900-01-01"
    else:
        start_date = end_date - timedelta(days=days)

    # Download data
    df = yf.download(tickers, start=start_date, end=end_date)["Close"]

    if isinstance(df, pd.Series):
        df = df.to_frame()

    st.write(f"Comparing from **{start_date}** to **{end_date.date()}**")

    fig = px.line(
        df,
        x=df.index,
        y=df.columns,
        title=f"{', '.join(tickers)} Price Comparison"
    )
    fig.update_layout(hovermode="x unified")

    st.plotly_chart(fig, use_container_width=True)
