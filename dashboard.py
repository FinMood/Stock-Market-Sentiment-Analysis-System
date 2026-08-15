import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ================= Configuration =================
st.set_page_config(page_title="Stock Sentiment Dashboard", layout="wide", initial_sidebar_state="expanded")
API_BASE = "http://localhost:8080/api"

st.markdown("""
    <style>
    .big-signal { font-size: 64px !important; text-align: center; border-radius: 10px; padding: 20px; font-weight: bold;}
    .normal-light { background-color: #374151; color: white; }
    .green-light { background-color: #10B981; color: white; }
    .red-light { background-color: #EF4444; color: white; }
    .yellow-light { background-color: #F59E0B; color: white; }
    </style>
""", unsafe_allow_html=True)

# ================= Data Fetching =================
@st.cache_data(ttl=10)
def fetch_stock_data(stock_id):
    try:
        res = requests.get(f"{API_BASE}/signals/{stock_id}")
        if res.status_code == 200:
            df = pd.DataFrame(res.json()["data"])
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            return df
    except Exception as e:
        st.error(f"Cannot connect to API: {e}")
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

# ================= Pages =================

def page_overview():
    st.title("📈 個股決策總覽 (Overview)")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        selected_stock = st.selectbox("選擇股票", ["2330", "2308", "2454"])
        
    df = fetch_stock_data(selected_stock)
    
    if df.empty:
        st.warning("查無資料，請先確保 FastAPI 後端已啟動 (`uv run uvicorn api:app --port 8000`)")
        return

    # Extract Latest Day Info
    latest = df.iloc[-1]
    last_signal = latest.get("signal", "—")
    last_sentiment = latest.get("avg_sentiment", 0)
    last_return = latest.get("return_3d", 0)
    
    # AI 一句話短評邏輯
    ai_comment = "正常波動，無明顯背離跡象，請依個人交易策略進行。"
    if "🔴" in str(last_signal): 
        css_class = "red-light"
        ai_comment = f"⚠️ 注意：該股過去三日已達『{latest.get('return_level', '')}』，但今日財經新聞出現極度異常之『{latest.get('sentiment_level', '')}』情緒，高度懷疑主力正利用好消息出貨，建議今日暫緩追高。"
    elif "🟢" in str(last_signal): 
        css_class = "green-light"
        ai_comment = f"💡 提示：該股過去三日已達『{latest.get('return_level', '')}』，但今日財經新聞卻呈現『{latest.get('sentiment_level', '')}』之恐慌情緒。市場可能已經超賣，短期具備反彈潛力，可列入觀察名單。"
    elif "🟡" in str(last_signal): 
        css_class = "yellow-light"
        ai_comment = f"👀 觀望：新聞情緒為『{latest.get('sentiment_level', '')}』，但股價呈現『{latest.get('return_level', '')}』，市場未被資訊撼動，需等待方向明確。"
    else: 
        css_class = "normal-light"
    
    st.markdown("### 🚦 當前決策燈號")
    st.markdown(f'<div class="big-signal {css_class}">{last_signal} <br><span style="font-size:24px;">(更新日期: {latest["date"].strftime("%Y-%m-%d")})</span></div>', unsafe_allow_html=True)
    
    st.info(f"**🎯 系統決策短評**：{ai_comment}")
    
    st.divider()
    
    st.markdown("### 📊 情緒與股價疊加時間序列圖")
    
    # Dual Axis Chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # K-line/price
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['close'], name='收盤價', mode='lines', 
        line=dict(color='white', width=2)
    ), secondary_y=False)
    
    # Sentiment bar (Taiwanese market: Red is up/optimistic, Green is down/pessimistic)
    colors = ['#EF4444' if s > 0 else '#10B981' for s in df['avg_sentiment']]
    fig.add_trace(go.Bar(x=df['date'], y=df['avg_sentiment'], name='平均情緒分數', marker_color=colors, opacity=0.8), secondary_y=True)
    
    # Signal Markers
    signals = df[df['signal'].astype(str).str.contains("🔴|🟢|🟡", na=False)]
    if not signals.empty:
        fig.add_trace(go.Scatter(
            x=signals['date'], y=signals['close'],
            mode='markers', name='防呆訊號',
            marker=dict(size=12, symbol='star', color='cyan', line=dict(width=2, color='white')),
            text=signals['signal'], hoverinfo='text+x+y'
        ), secondary_y=False)
        
    fig.update_layout(height=500, title_text=f"{selected_stock} 近期走勢與社會情緒對比", template="plotly_dark")
    fig.update_yaxes(title_text="股價 (TWD)", secondary_y=False)
    fig.update_yaxes(title_text="平均情緒分數 ([-1, 1])", secondary_y=True, range=[-1, 1])
    st.plotly_chart(fig, use_container_width=True)

    
    # 確保不會為空，加上容錯
    st.markdown("### 🎛️ 雷達儀表板：分數數據區")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("當日綜合情緒分數", f"{float(last_sentiment):+.2f} (滿分 1.0/-1.0)")
    with c2:
        return_txt = f"{float(last_return):+.2%}" if pd.notnull(last_return) else "無資料"
        st.metric("短期位階判定", f"{latest.get('return_level', '無資料')}", f"(T-3累積漲跌 {return_txt})")


def page_signals():
    st.title("🚦 歷史背離訊號分析 (Divergence Analysis)")
    
    st.markdown("透過歷史數據說服散戶「為何紅燈不能追、綠燈不要怕」。")
    df_all = fetch_all_signals()
    
    if df_all.empty:
        st.warning("請啟動 API。")
        return
        
    signals_only = df_all[df_all['signal'].astype(str).str.contains("🔴|🟢|🟡", na=False)].copy()
    
    st.markdown(f"**共找到 {len(signals_only)} 次背離事件**")
    
    # Backtest dummy stats (For demo logic)
    col1, col2 = st.columns(2)
    col1.info("🔻 **紅燈後跌幅機率**: (需計算 t+3 實際機率, 已預留欄位)")
    col2.success("🔺 **綠燈後反彈機率**: (需計算 t+3 實際機率, 已預留欄位)")
    
    # Show dataframe
    st.dataframe(signals_only[['date', 'stock_id', 'close', 'avg_sentiment', 'return_3d', 'signal', 'sentiment_level', 'return_level']].sort_values(by="date", ascending=False), use_container_width=True)


def page_engines():
    st.title("🧠 演算法引擎觀測站 (Engine Comparison)")
    st.info("此頁面未來將展示 4 大核心引擎 (FinBERT, CKIP-BERT, RoBERTa, Jieba) 的個別預測對比矩陣與一致率 (Consensus)。")
    

# ================= App Routing =================
st.sidebar.title("導覽選項 (Navigation)")
page = st.sidebar.radio("選擇頁面", ["總覽與決策儀表板", "歷史背離訊號分析", "演算法引擎觀測站"])

if page == "總覽與決策儀表板":
    page_overview()
elif page == "歷史背離訊號分析":
    page_signals()
elif page == "演算法引擎觀測站":
    page_engines()
