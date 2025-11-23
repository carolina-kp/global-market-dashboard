import streamlit as st
import pandas as pd
from io import BytesIO

from services.data_loader import load_data
from services.indicator import compute_rsi, compute_macd, compute_bollinger
from services.support_resistance import detect_levels

from components.charts import (
    price_chart_with_bands,
    rsi_chart,
    macd_chart,
    levels_candlestick
)

st.title("Technical Analysis and AI Explanation")

ticker = st.text_input("Ticker", "NVDA")

if st.button("Analyze"):
    data, stock = load_data(ticker)
    if data is not None:
        # Compute indicators
        data = compute_bollinger(data)
        data["RSI"] = compute_rsi(data["Close"])
        data = compute_macd(data)
        levels = detect_levels(data["Close"])

        # Coerce indicator values to Python scalars for safe comparisons
        last_close = float(data["Close"].iloc[-1])
        rsi_value = float(data["RSI"].iloc[-1])
        macd = float(data["MACD"].iloc[-1])
        signal = float(data["Signal"].iloc[-1])
        hist = float(data["Histogram"].iloc[-1])
        sma = float(data["SMA20"].iloc[-1])
        upper = float(data["BB_upper"].iloc[-1])
        lower = float(data["BB_lower"].iloc[-1])

        st.subheader("Price with Bollinger Bands")
        st.plotly_chart(price_chart_with_bands(data, ticker), use_container_width=True)

        st.markdown("### AI Interpretation of Price Action")

        st.markdown("""
        **What Bollinger Bands Mean:**  
        Bollinger Bands measure volatility.  
        - When price pushes above the upper band → the asset is extended or overbought.  
        - When price falls under the lower band → it may be oversold or due for a bounce.  
        - Staying inside the bands indicates normal volatility.
        """)

        if last_close > upper:
            st.write("The price is above the upper Bollinger Band. This often suggests strong bullish momentum but can also signal an overextended move that may pull back.")
        elif last_close < lower:
            st.write("The price is below the lower Bollinger Band. This indicates oversold market conditions, sometimes associated with a rebound.")
        else:
            st.write("The price is inside the Bollinger Bands. Volatility is normal, and price is not stretched in either direction.")

        if last_close > sma:
            st.write("The price is above the 20-day moving average, indicating short-term bullish trend.")
        else:
            st.write("The price is below the 20-day moving average, indicating short-term bearish pressure.")

        st.write("---")

        # RSI
        st.subheader("RSI (Relative Strength Index)")
        st.plotly_chart(rsi_chart(data), use_container_width=True)

        st.markdown("### AI Interpretation of RSI")
        st.markdown("""
        **What RSI Means:**  
        RSI measures momentum on a scale from 0 to 100.  
        - Above 70 → Overbought, trend may slow or reverse  
        - Below 30 → Oversold, price may rebound  
        - Between 30–70 → Neutral strength  
        """)

        if rsi_value > 70:
            st.write(f"RSI is {rsi_value:.2f}. This indicates an overbought condition, meaning price moved up too quickly and may cool down.")
        elif rsi_value < 30:
            st.write(f"RSI is {rsi_value:.2f}. This indicates oversold conditions, meaning price may bounce or reverse upward.")
        else:
            st.write(f"RSI is {rsi_value:.2f}, which is neutral. Market momentum is balanced.")

        st.write("---")

        # MACD
        st.subheader("MACD")
        st.plotly_chart(macd_chart(data), use_container_width=True)

        st.markdown("### AI Interpretation of MACD")
        st.markdown("""
        **What MACD Means:**  
        MACD measures trend strength:  
        - MACD crossing above Signal → bullish acceleration  
        - MACD crossing below Signal → bearish slowdown  
        - Histogram shows momentum strength  
        """)

        if macd > signal:
            st.write("MACD is above the signal line. This suggests bullish momentum strengthening.")
        else:
            st.write("MACD is below the signal line. This suggests bearish or weakening momentum.")

        if hist > 0:
            st.write("MACD histogram is positive: upward momentum is building.")
        else:
            st.write("MACD histogram is negative: trend may be weakening.")

        st.write("---")

        # Support/Resistance
        st.subheader("Support and Resistance Levels")
        st.plotly_chart(levels_candlestick(data, levels), use_container_width=True)

        st.markdown("### AI Interpretation of Support & Resistance")
        st.markdown("""
        **What Support Means:**  
        Support levels are floors where price historically reversed upward.  
        
        **What Resistance Means:**  
        Resistance levels are ceilings where price historically rejected downward.
        """)

        if not levels:
            st.write("No strong support or resistance levels detected.")
        else:
            for kind, date, level in levels[-5:]:
                st.write(f"{kind.capitalize()} at ${level:.2f}")

        st.write("---")

        # Summary
        st.subheader("Overall AI Summary")

        summary = []

        # RSI summary (priority)
        if not pd.isna(rsi_value):
            if rsi_value > 70:
                summary.append("RSI indicates overbought market conditions.")
            elif rsi_value < 30:
                summary.append("RSI indicates oversold momentum.")
            else:
                summary.append("RSI is neutral.")

        # MACD summary
        if not (pd.isna(macd) or pd.isna(signal)):
            if macd > signal:
                summary.append("MACD suggests bullish acceleration.")
            else:
                summary.append("MACD suggests bearish momentum.")

        # Bollinger Bands summary
        if not (pd.isna(last_close) or pd.isna(upper) or pd.isna(lower)):
            if last_close > upper:
                summary.append("Price is stretched above Bollinger Bands (overbought zone).")
            elif last_close < lower:
                summary.append("Price is below the lower Bollinger Band (possible oversold).")
            else:
                summary.append("Price is inside the Bollinger Bands.")

        # Short-term trend via SMA
        if not pd.isna(last_close) and not pd.isna(sma):
            if last_close > sma:
                summary.append("Short-term trend is bullish.")
            else:
                summary.append("Short-term trend is bearish.")

        for s in summary:
            st.write("-", s)

        # DOWNLOAD SECTION
        st.subheader("Download Data")

        df_csv = data.to_csv().encode("utf-8")
        st.download_button("Download CSV", df_csv, f"{ticker}_technical.csv", "text/csv")

        excel_buffer = BytesIO()
        data = data.copy()
        data.index = pd.to_datetime(data.index)
        if getattr(data.index, "tz", None) is not None:
            data.index = data.index.tz_convert(None)

        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            data.to_excel(writer, sheet_name="Technical Analysis")
        excel_buffer.seek(0)

        st.download_button(
            "Download Excel",
            data=excel_buffer,
            file_name=f"{ticker}_technical.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
