import streamlit as st
import pandas as pd
from frontend.data_fetch import fetch_all_signals

def render(selected_stock, stock_name, df):
    """Page 3: 歷史背離訊號紀錄"""

    st.markdown('<div class="section-title"><span class="icon">🚦</span>歷史背離訊號分析 Divergence Analysis<span class="line"></span></div>', unsafe_allow_html=True)

    col_view, _ = st.columns([2, 3])
    with col_view:
        view_mode = st.radio(
            "🔎 歷史統計範圍", 
            [f"單一個股 ({selected_stock} {stock_name})", "全部個股 (大盤加總)"], 
            horizontal=True,
            label_visibility="collapsed"
        )
        
    df_all = fetch_all_signals()
    if 'date' in df_all.columns:
        df_all['date'] = pd.to_datetime(df_all['date'])
        
        # In Tab 3, we don't apply the single-page Date selector, we show all history.
        # But we do filter by stock if "單一個股" is chosen.
        if "單一個股" in view_mode:
            df_all = df_all[df_all["stock_id"].astype(str) == str(selected_stock)]

    if df_all.empty:
        st.markdown('''
        <div class="placeholder-card">
            <div class="placeholder-icon">📡</div>
            <div class="placeholder-title">此範圍內目前無歷史背離紀錄</div>
            <div class="placeholder-desc">請調整選股範圍或確認資料庫是否已同步。</div>
        </div>
        ''', unsafe_allow_html=True)
        return

    signals_only = df_all[df_all['signal'].astype(str).str.contains("🔴|🟢|🟡", na=False)].copy()

    red_count = len(signals_only[signals_only['signal'].astype(str).str.contains("🔴", na=False)])
    green_count = len(signals_only[signals_only['signal'].astype(str).str.contains("🟢", na=False)])
    amber_count = len(signals_only[signals_only['signal'].astype(str).str.contains("🟡", na=False)])
    total_count = len(signals_only)

    # ── Stats Cards ──
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-number neutral">{total_count}</div>
            <div class="stat-desc">📋 歷史背離事件總數</div>
        </div>
        <div class="stat-card red-glow">
            <div class="stat-number red">{red_count}</div>
            <div class="stat-desc">🛑 紅燈（利多出盡）</div>
        </div>
        <div class="stat-card green-glow">
            <div class="stat-number green">{green_count}</div>
            <div class="stat-desc">✅ 綠燈（超賣反彈）</div>
        </div>
        <div class="stat-card">
            <div class="stat-number amber">{amber_count}</div>
            <div class="stat-desc">⏳ 黃燈（觀望）</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Backtest Placeholder ──
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="ai-comment-card red-border">
            <div class="ai-comment-title">🔻 紅燈後跌幅機率</div>
            <div class="ai-comment-text">需計算未來3日實際跌幅機率，此區域為回測統計預留欄位。連接歷史數據後將自動更新。</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="ai-comment-card green-border">
            <div class="ai-comment-title">🔺 綠燈後反彈機率</div>
            <div class="ai-comment-text">需計算未來3日實際反彈機率，此區域為回測統計預留欄位。連接歷史數據後將自動更新。</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Signal History Table ──
    st.markdown('<div class="section-title"><span class="icon">📋</span>訊號歷史明細<span class="line"></span></div>', unsafe_allow_html=True)

    display_cols = ['date', 'stock_id', 'close', 'avg_sentiment', 'return_3d', 'signal', 'sentiment_level', 'return_level']
    available_cols = [c for c in display_cols if c in signals_only.columns]
    
    st.dataframe(
        signals_only[available_cols].sort_values(by="date", ascending=False),
        use_container_width=True,
        height=500,
        column_config={
            "date": "結算日期",
            "stock_id": "代碼",
            "close": "當日收盤價",
            "avg_sentiment": "平均情緒",
            "return_3d": "近3日漲跌",
            "signal": "背離判斷訊號",
            "sentiment_level": "情緒等級",
            "return_level": "股價等級"
        }
    )
