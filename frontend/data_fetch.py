import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8079/api"

def fetch_stock_data(stock_id):
    try:
        res = requests.get(f"{API_BASE}/signals/{stock_id}")
        if res.status_code == 200:
            df = pd.DataFrame(res.json()["data"])
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            return df
    except Exception as e:
        st.error(f"❌ 無法連線至 API：{e}")
    return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_all_signals():
    try:
        res = requests.get(f"{API_BASE}/signals/all")
        if res.status_code == 200:
            df = pd.DataFrame(res.json()["data"])
            return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_thresholds():
    """取得分位數門檻 (P10/P25/P75/P90)"""
    try:
        res = requests.get(f"{API_BASE}/thresholds")
        if res.status_code == 200:
            data = res.json()["data"]
            thresholds = {}
            for item in data:
                key = f"{item['指標']}_{item['分位']}"
                thresholds[key] = item['門檻值']
            return thresholds
    except:
        pass
    return {}

# ================= Plotly Theme =================
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(11, 17, 32, 0)",
    plot_bgcolor="rgba(11, 17, 32, 0.4)",
    font=dict(family="Inter, Noto Sans TC, sans-serif", color="#94A3B8", size=12),
    title_font=dict(size=16, color="#F1F5F9", family="Inter, Noto Sans TC, sans-serif"),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(148, 163, 184, 0.1)",
        borderwidth=1,
        font=dict(size=11, color="#94A3B8"),
    ),
    xaxis=dict(
        gridcolor="rgba(148, 163, 184, 0.06)",
        zerolinecolor="rgba(148, 163, 184, 0.1)",
    ),
    yaxis=dict(
        gridcolor="rgba(148, 163, 184, 0.06)",
        zerolinecolor="rgba(148, 163, 184, 0.1)",
    ),
    margin=dict(l=16, r=16, t=48, b=16),
    hoverlabel=dict(bgcolor="#1E293B", bordercolor="#334155", font=dict(color="#F1F5F9")),
)


# ================= Pages =================
