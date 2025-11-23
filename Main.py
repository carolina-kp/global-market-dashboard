import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os

st.set_page_config(page_title="Global Market Dashboard", layout="wide")

st.title("Global Market Dashboard")
st.markdown("Live overview of U.S., global, and crypto markets.")

WATCHLIST_FILE = "watchlist.json"


# ============================
# WATCHLIST PERSISTENCE
# ============================
def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        return []
    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_watchlist(watchlist):
    try:
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(watchlist, f, indent=2)
    except Exception:
        pass


if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

# ============================
# WATCHLIST AT TOP
# ============================
st.subheader("Watchlist")

col_left, col_right = st.columns([2, 3])

with col_left:
    new_ticker = st.text_input("Add ticker to watchlist", "AAPL")
    if st.button("Add to watchlist"):
        sym = new_ticker.strip().upper()
        if sym:
            entry = {"name": sym, "ticker": sym}
            if entry not in st.session_state.watchlist:
                st.session_state.watchlist.append(entry)
                save_watchlist(st.session_state.watchlist)

with col_right:
    if st.session_state.watchlist:
        df_watch = pd.DataFrame(st.session_state.watchlist)
        st.dataframe(df_watch, use_container_width=True)
    else:
        st.info("Watchlist is empty.")

st.write("---")

# ============================
# MARKET OVERVIEW
# ============================

INDEX_TICKERS = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",
    "VIX": "^VIX",
    "FTSE 100": "^FTSE",
    "DAX": "^GDAXI",
    "CAC 40": "^FCHI",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
}

CRYPTO_TICKERS = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
}


def get_ticker_data(ticker: str):
    df = yf.download(
        ticker, period="5d", interval="1d", auto_adjust=True, progress=False
    )
    if df.empty or len(df) < 2:
        return None, None

    close = df["Close"]
    last = float(close.iloc[-1])
    prev = float(close.iloc[-2])
    pct = (last - prev) / prev * 100
    return last, pct


st.subheader("Market Overview")


def render_boxes(ticker_dict, title: str):
    st.markdown(f"## {title}")
    cols = st.columns(3)

    for idx, (name, ticker) in enumerate(ticker_dict.items()):
        last, pct = get_ticker_data(ticker)
        col = cols[idx % 3]

        if last is None:
            col.markdown(f"**{name}**  \nData unavailable")
            continue

        color = "#00cc66" if pct >= 0 else "#ff4444"

        col.markdown(
            f"""
            <div style="
                padding:15px;
                border-radius:14px;
                background:linear-gradient(135deg,#141414,#101820);
                border:1px solid #333333;
                box-shadow:0 4px 16px rgba(0,0,0,0.4);
            ">
                <h4 style="margin:0; color:white; font-weight:600;">{name}</h4>
                <p style="margin:4px 0 0 0; color:{color}; font-size:22px; font-weight:600;">
                    {pct:.2f}% today
                </p>
                <p style="margin:2px 0 0 0; color:#aaaaaa; font-size:13px;">
                    Last close: {last:.2f}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


render_boxes(INDEX_TICKERS, "Global Stock Indices")
render_boxes(CRYPTO_TICKERS, "Major Cryptocurrencies")

st.write("---")

# ============================
# MARKET PERFORMANCE CHARTS
# ============================
st.subheader("Market Performance Charts")

# Company override
manual_ticker = st.text_input("Search any stock (AAPL, TSLA, NVDA...)", "")

if manual_ticker.strip() != "":
    selected_ticker = manual_ticker.strip().upper()
    selected_market = selected_ticker
else:
    selected_market = st.selectbox(
        "Choose a market to visualize:",
        list(INDEX_TICKERS.keys()) + list(CRYPTO_TICKERS.keys()),
    )
    selected_ticker = (
        INDEX_TICKERS.get(selected_market)
        or CRYPTO_TICKERS.get(selected_market)
    )

# Time ranges
period_option = st.selectbox(
    "Time Range",
    ["1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "5 Years", "MAX"],
)

period_mapping = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
    "MAX": "max",
}

# Fetch clean data
df = yf.download(
    selected_ticker,
    period=period_mapping[period_option],
    interval="1d",
    auto_adjust=False,
    progress=False,
)

if df.empty:
    st.warning("No market data available.")
    st.stop()

# Clean index and remove timezone noise
df.index = pd.to_datetime(df.index, errors="coerce")
# pandas tz_localize compatibility
try:
    df.index = df.index.tz_localize(None, errors="ignore")
except TypeError:
    if getattr(df.index, "tz", None) is not None:
        df.index = df.index.tz_localize(None)

df = df.sort_index()

# Normalize columns in case yf.download returned a MultiIndex or different casing
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [col[0] for col in df.columns]

if "Close" not in df.columns:
    # try case-insensitive match or substring
    cols_lower = {c.lower(): c for c in df.columns}
    if "close" in cols_lower:
        df.rename(columns={cols_lower["close"]: "Close"}, inplace=True)
    else:
        found = None
        for c in df.columns:
            if "close" in str(c).lower():
                found = c
                break
        if found:
            df.rename(columns={found: "Close"}, inplace=True)

if "Close" not in df.columns:
    st.warning("Downloaded data does not contain a Close column. Cannot render chart.")
    st.stop()

df = df.dropna(subset=["Close"])

# Chart choice
chart_type = st.radio("Chart type", ["Line", "Candlestick"], horizontal=True)

# Draw chart
fig = go.Figure()

if chart_type == "Line":
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        name=selected_market
    ))
else:
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        increasing_line_color="green",
        decreasing_line_color="red",
    ))

fig.update_layout(
    title=f"{selected_market} - {period_option} Performance",
    height=500,
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)

# ============================
# FUNDAMENTALS (Companies only)
# ============================
if selected_ticker.startswith("^") or selected_ticker.endswith("USD"):
    st.info("Fundamental data is available only for individual stocks.")
else:
    st.subheader("Fundamentals and Events")
    tkr = yf.Ticker(selected_ticker)

    tab1, tab2, tab3 = st.tabs(
        ["Dividends & Splits", "Earnings", "Analyst Targets"]
    )

    # Dividends/Splits
    with tab1:
        st.write("**Dividends**")
        dividends = tkr.dividends
        def _has_data(obj):
            if obj is None:
                return False
            if hasattr(obj, "empty"):
                try:
                    return not obj.empty
                except Exception:
                    return False
            if isinstance(obj, (dict, list, tuple, set)):
                return bool(obj)
            try:
                return bool(obj)
            except Exception:
                return False

        if _has_data(dividends):
            try:
                st.line_chart(dividends)
                st.dataframe(dividends)
            except Exception:
                # fallback to showing raw object
                st.write(dividends)
        else:
            st.info("No dividend data.")

        st.write("**Splits**")
        splits = tkr.splits
        if _has_data(splits):
            try:
                st.dataframe(splits)
            except Exception:
                st.write(splits)
        else:
            st.info("No split data.")

    # Earnings
    with tab2:
        cal = None
        try:
            cal = tkr.calendar
        except Exception:
            cal = None

        if _has_data(cal):
            # calendar may be a DataFrame or a dict depending on yfinance version
            if isinstance(cal, (pd.DataFrame, pd.Series)):
                st.dataframe(cal, use_container_width=True)
            elif isinstance(cal, dict):
                try:
                    df_cal = pd.DataFrame.from_dict(cal)
                    if df_cal.empty:
                        st.json(cal)
                    else:
                        st.dataframe(df_cal, use_container_width=True)
                except Exception:
                    st.write(cal)
            else:
                st.write(cal)
        else:
            st.info("No earnings calendar data.")

    # Analyst targets
    with tab3:
        info = tkr.info
        fields = [
            ("Target High", "targetHighPrice"),
            ("Target Mean", "targetMeanPrice"),
            ("Target Low", "targetLowPrice"),
            ("Analyst Count", "numberOfAnalystOpinions"),
            ("Recommendation", "recommendationKey"),
        ]

        available = False
        for title, key in fields:
            if key in info and info[key] is not None:
                st.write(f"**{title}:** {info[key]}")
                available = True

        if not available:
            st.info("No analyst data available.")


# ============================
# CORRELATION MATRIX
# ============================
st.subheader("Correlation Matrix Between Tickers")

corr_symbols = st.text_input(
    "Tickers for correlation (comma separated)",
    value="AAPL, MSFT, NVDA, TSLA",
)

corr_period = st.selectbox(
    "Correlation period",
    ["3 Months", "6 Months", "1 Year"],
    index=1,
)

corr_mapping = {
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
}

if st.button("Compute Correlation"):
    tickers = [s.strip().upper() for s in corr_symbols.split(",") if s.strip()]

    if len(tickers) < 2:
        st.warning("Enter at least two tickers.")
    else:
        prices = yf.download(
            tickers,
            period=corr_mapping[corr_period],
            interval="1d",
            auto_adjust=True,
            progress=False,
        )["Close"]

        if isinstance(prices, pd.Series):
            prices = prices.to_frame()

        prices = prices.dropna()
        if prices.empty:
            st.info("No price data for the selected tickers.")
        else:
            returns = prices.pct_change().dropna()
            corr = returns.corr()

            st.markdown("Correlation table")
            st.dataframe(corr, use_container_width=True)

            fig_corr = px.imshow(
                corr,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu",
                zmin=-1,
                zmax=1,
            )
            st.plotly_chart(fig_corr, use_container_width=True)
