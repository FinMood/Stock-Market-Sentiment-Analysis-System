import streamlit as st
import pandas as pd

from frontend.styles import apply_custom_css, STOCK_NAMES
from frontend.data_fetch import fetch_stock_data
from frontend.components import tab_overview, tab_position, tab_history

def main():
    apply_custom_css()
    
    # ================= Global Layout (Tabs & Filters) =================
    stock_options = [f"{sid} {STOCK_NAMES.get(sid, '')}" for sid in STOCK_NAMES]
    
    col_stock, col_date, _empty, col_brand = st.columns([2, 2, 3, 3])
    
    with col_stock:
        selected_label = st.selectbox("🎯 選擇觀測標的", stock_options)
        selected_stock = selected_label.split(" ")[0]
        stock_name = STOCK_NAMES.get(selected_stock, "")
    
    with col_brand:
        st.markdown('''
        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 12px; margin-top: 10px;">
            <div style="text-align: right;">
                <div style="font-size: 24px; font-weight: 800; background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: -4px;">FinMood</div>
                <div style="font-size: 11px; color: var(--text-muted); font-weight: 500;">股市情緒防呆決策系統</div>
            </div>
            <span style="font-size: 36px; line-height: 1;">🧠</span>
        </div>
        ''', unsafe_allow_html=True)
    
    df_global = fetch_stock_data(selected_stock)
    
    with col_date:
        if not df_global.empty:
            date_options = df_global["date"].dt.strftime("%Y-%m-%d").tolist()[::-1]
            selected_date_str = st.selectbox("📅 結算回測日期", date_options)
            df_up_to_date = df_global[df_global["date"] <= pd.to_datetime(selected_date_str)].copy()
        else:
            selected_date_str = None
            df_up_to_date = df_global.copy()
            st.selectbox("📅 結算回測日期", ["無資料"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Top-level Tabs
    tab1, tab2, tab3 = st.tabs(["📈  即時情緒決策板", "📊  歷史位階與組合研判", "🚦  歷史背離訊號紀錄"])
    
    with tab1:
        tab_overview.render(selected_stock, stock_name, df_up_to_date)
    
    with tab2:
        tab_position.render(selected_stock, stock_name, df_up_to_date)
    
    with tab3:
        tab_history.render(selected_stock, stock_name, df_up_to_date)
