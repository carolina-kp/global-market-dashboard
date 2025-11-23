import streamlit as st
import yfinance as yf
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Historical Data", layout="wide")

st.title("📊 Historical Stock Data Downloader")

# -----------------------------
# INPUTS
# -----------------------------
ticker = st.text_input("Ticker Symbol", "AAPL")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime(2015, 1, 1))
with col2:
    end_date = st.date_input("End Date", datetime.now())

chart_type = st.radio("Chart Type", ["Line", "Candlestick"], horizontal=True)

# -----------------------------
# LOAD DATA
# -----------------------------
if st.button("Load Data"):
    df = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        st.error("❌ No data found. Check ticker or date range.")
    else:
        # -----------------------------
        # FIX 1 — Flatten MultiIndex
        # -----------------------------
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        # -----------------------------
        # FIX 2 — Clean Datetime Index
        # -----------------------------
        df.index = pd.to_datetime(df.index)
        if getattr(df.index, "tz", None) is not None:
            df.index = df.index.tz_convert(None)

        df = df.sort_index()
        df = df.dropna(subset=["Close"])

        st.success(f"Loaded {len(df)} rows of clean historical data.")

        # -----------------------------
        # PRICE CHART
        # -----------------------------
        st.subheader("Price Chart")

        if chart_type == "Line":
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["Close"],
                    mode="lines",
                    name="Close"
                )
            )
        else:
            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=df.index,
                        open=df["Open"],
                        high=df["High"],
                        low=df["Low"],
                        close=df["Close"],
                        increasing_line_color="green",
                        decreasing_line_color="red",
                        name="Candlestick"
                    )
                ]
            )

        fig.update_layout(
            hovermode="x unified",
            height=500,
            margin=dict(l=10, r=10, t=40, b=10),
        )

        st.plotly_chart(fig, use_container_width=True)

        # -----------------------------
        # VOLUME CHART
        # -----------------------------
        st.subheader("Volume")

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume"))
        fig2.update_layout(height=300)

        st.plotly_chart(fig2, use_container_width=True)

        # -----------------------------
        # DATA TABLE
        # -----------------------------
        st.subheader("Historical Data Table")
        st.dataframe(df, use_container_width=True)

        # -----------------------------
        # DOWNLOAD BUTTONS (Unique keys)
        # -----------------------------
        st.subheader("Download Data")

        # CSV
        csv_data = df.to_csv().encode("utf-8")
        st.download_button(
            "⬇ Download CSV",
            data=csv_data,
            file_name=f"{ticker}_historical.csv",
            mime="text/csv",
            key="csv_download_hist"
        )

        # Excel
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Historical Data")
        excel_buffer.seek(0)

        st.download_button(
            "⬇ Download Excel",
            data=excel_buffer,
            file_name=f"{ticker}_historical.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="excel_download_hist"
        )
