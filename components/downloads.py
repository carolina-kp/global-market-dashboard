import streamlit as st
from io import BytesIO
import pandas as pd

def download_section(df, ticker):
    csv = df.to_csv()
    st.download_button(
        "Download CSV",
        data=csv,
        file_name=f"{ticker}.csv",
        mime="text/csv"
    )

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer)
    buffer.seek(0)

    st.download_button(
        "Download Excel",
        data=buffer,
        file_name=f"{ticker}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
