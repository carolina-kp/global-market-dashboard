import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta

st.set_page_config(page_title="Forecasting", layout="wide")

st.title("Simple Price Forecasting")

ticker = st.text_input("Ticker", "AAPL")

period = st.selectbox(
    "Training Period",
    ["6 Months", "1 Year", "2 Years"],
    index=1
)

period_map = {
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
}

horizon = st.slider("Forecast Horizon (days)", 10, 60, 30)

if st.button("Run Forecast"):
    df = yf.download(
        ticker,
        period=period_map[period],
        interval="1d",
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        st.error("No data available.")
    else:
        # Clean index + flatten
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        df.index = pd.to_datetime(df.index)
        if getattr(df.index, "tz", None) is not None:
            df.index = df.index.tz_convert(None)

        df = df.sort_index()
        df = df.dropna(subset=["Close"])

        closes = df["Close"]
        x = np.arange(len(closes))

        # Linear trend line
        coeffs = np.polyfit(x, closes.values, 1)
        trend = np.polyval(coeffs, x)

        # Forecast future values
        last_day = df.index[-1]
        future_x = np.arange(len(closes), len(closes) + horizon)
        future_dates = [last_day + timedelta(days=i + 1) for i in range(horizon)]
        future_values = np.polyval(coeffs, future_x)

        # PLOTTING
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df.index,
            y=closes,
            mode="lines",
            name="Historical"
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=trend,
            mode="lines",
            name="Trend",
            line=dict(dash="dash")
        ))

        fig.add_trace(go.Scatter(
            x=future_dates,
            y=future_values,
            mode="lines",
            name="Forecast",
            line=dict(dash="dot")
        ))

        fig.update_layout(
            title=f"{ticker} — {horizon}-Day Linear Forecast",
            hovermode="x unified",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Forecast Table")
        forecast_df = pd.DataFrame({
            "Date": future_dates,
            "Forecasted Close": future_values
        })

        st.dataframe(forecast_df, use_container_width=True)
# ============================
# FOOTER
# ============================

st.write("---")

footer_html = """
<div style='text-align: center; padding: 20px; color: #888888; font-size: 14px;'>
    <p>Made by <strong>Carolina Kogan Plachkinova</strong></p>
    <p>23/11/2025</p>
    <p>© 2025 All rights reserved. Unauthorized use, reproduction, or distribution is prohibited.</p>
</div>
"""

st.markdown(footer_html, unsafe_allow_html=True)
