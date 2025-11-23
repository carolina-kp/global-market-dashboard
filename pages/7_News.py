import streamlit as st
from services.news import get_yahoo_news

st.title("Stock News")

ticker = st.text_input("Ticker", "NVDA")

if st.button("Load News"):
    news = get_yahoo_news(ticker)

    if not news:
        st.info("No news available.")
    else:
        for item in news:
            st.subheader(item["title"])
            st.write(item["published"])
            st.write(item["link"])
            st.write("---")
