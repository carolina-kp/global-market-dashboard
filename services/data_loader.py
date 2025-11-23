import yfinance as yf
import streamlit as st
import feedparser

def load_yahoo_rss(ticker):
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}"
    feed = feedparser.parse(url)
    return feed.entries


def load_data(ticker):
    ticker = ticker.upper().strip()
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5y")
        if hist.empty:
            st.error(f"No data for {ticker}")
            return None, None
        return hist, stock
    except Exception as e:
        st.error(str(e))
        return None, None
