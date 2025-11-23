import plotly.graph_objects as go

def price_chart_with_bands(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], name="Upper Band", opacity=0.5))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], name="Lower Band", opacity=0.5))
    fig.update_layout(title=f"{ticker} Price Chart")
    return fig

def rsi_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"))
    fig.add_hline(y=70)
    fig.add_hline(y=30)
    return fig

def macd_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], name="Signal"))
    fig.add_trace(go.Bar(x=df.index, y=df["Histogram"], name="Histogram"))
    return fig

def levels_candlestick(df, levels):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"]
    )])

    for kind, date, level in levels:
        fig.add_hline(y=level, line_dash="dot")
    return fig
