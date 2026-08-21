import streamlit as st
from frontend.app import main

st.set_page_config(page_title="FinMood 股市情緒決策", page_icon="🧠", layout="wide")

if __name__ == "__main__":
    main()
