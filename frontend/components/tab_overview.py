import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from frontend.styles import PLOTLY_LAYOUT

def render(selected_stock, stock_name, df):
    """Page 1: 個股決策總覽"""


    if df.empty:
        st.markdown("""
        <div class="placeholder-card">
            <div class="placeholder-icon">📡</div>
            <div class="placeholder-title">數據尚未就緒</div>
            <div class="placeholder-desc">請先確保 FastAPI 後端已啟動<br><code>uv run uvicorn api:app --port 8079</code></div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Extract Latest Day Info ──
    latest = df.iloc[-1]
    last_signal = str(latest.get("signal", "—"))
    last_sentiment = round(float(latest.get("avg_sentiment", 0)), 3)  # 強制小數點三位
    last_return_raw = latest.get("return_3d", None)
    last_return = round(float(last_return_raw), 4) if pd.notnull(last_return_raw) else None
    date_str = latest["date"].strftime("%Y-%m-%d")

    # Determine signal type
    ai_comment = "目前市場情緒與股價趨勢正常，無明顯背離跡象。請依個人交易策略操作。"
    sentiment_level = latest.get('sentiment_level', '—')
    return_level = latest.get('return_level', '—')

    if "🔴" in last_signal:
        signal_class = "red"
        signal_icon = "🛑"
        signal_label = "利多出盡"
        signal_subtitle = "紅燈警示"
        comment_border = "red-border"
        hero_desc = f"輿情極度樂觀（{sentiment_level}），股價卻已漲了一段（{return_level}）"
        ai_comment = f"⚠️ 財經新聞出現極度異常之「{sentiment_level}」情緒，但該股過去三日已達「{return_level}」。高度懷疑主力正利用好消息出貨，建議暫緩追高。"
    elif "🟢" in last_signal:
        signal_class = "green"
        signal_icon = "✅"
        signal_label = "超賣反彈"
        signal_subtitle = "綠燈提示"
        comment_border = "green-border"
        hero_desc = f"輿情極度恐慌（{sentiment_level}），股價已超跌（{return_level}）"
        ai_comment = f"💡 新聞呈現「{sentiment_level}」之恐慌情緒，但該股過去三日已達「{return_level}」。市場可能已超賣，短期具備反彈潛力。"
    elif "🟡" in last_signal:
        signal_class = "amber"
        signal_icon = "⏳"
        signal_label = "方向不明"
        signal_subtitle = "黃燈觀望"
        comment_border = "amber-border"
        hero_desc = f"新聞情緒（{sentiment_level}）與股價走勢（{return_level}）方向不一致"
        ai_comment = f"👀 新聞情緒為「{sentiment_level}」，但股價呈現「{return_level}」。市場尚未被資訊撼動，建議等待方向明確。"
    else:
        signal_class = "neutral"
        signal_icon = "⚪"
        signal_label = "正常"
        signal_subtitle = "無背離訊號"
        comment_border = "neutral-border"
        hero_desc = "情緒與股價走勢目前一致，無明顯背離跡象"

    sentiment_color = "positive" if last_sentiment > 0 else ("negative" if last_sentiment < 0 else "neutral")
    sentiment_val = f"{last_sentiment:+.3f}"
    if pd.notnull(last_return):
        return_val = f"{float(last_return):+.2%}"
        return_color = "positive" if float(last_return) > 0 else "negative"
    else:
        return_val = "N/A"
        return_color = "neutral"

    # ── HERO Signal Banner ──
    st.markdown(f"""
    <div class="hero-banner {signal_class}">
        <div class="hero-top-row">
            <div class="hero-stock">
                <span class="hero-stock-name">今日股票資訊 ｜ {stock_name}</span>
                <span class="hero-stock-id">{selected_stock}</span>
            </div>
            <span class="hero-date">{date_str} 收盤結算</span>
        </div>
        <div class="hero-content">
            <div class="hero-main">
                <div class="hero-light-wrap">
                    <div class="hero-light {signal_class}">{signal_icon}</div>
                </div>
                <div class="hero-text">
                    <div class="hero-subtitle">{signal_subtitle}</div>
                    <div class="hero-label">{signal_label}</div>
                    <div class="hero-desc">{hero_desc}</div>
                </div>
            </div>
            <div class="hero-kpi-row">
                <div class="hero-kpi">
                    <span class="hero-kpi-name">📰 新聞量</span>
                    <span class="hero-kpi-val neutral">{int(latest.get('news_count', 0))}</span>
                </div>
                <div class="hero-kpi-divider"></div>
                <div class="hero-kpi">
                    <span class="hero-kpi-name">🧠 情緒分數</span>
                    <span class="hero-kpi-val {sentiment_color}">{sentiment_val}</span>
                </div>
                <div class="hero-kpi-divider"></div>
                <div class="hero-kpi">
                    <span class="hero-kpi-name">📊 近3日漲跌</span>
                    <span class="hero-kpi-val {return_color}">{return_val}</span>
                </div>
                <div class="hero-kpi-divider"></div>
                <div class="hero-kpi">
                    <span class="hero-kpi-name">💰 收盤價</span>
                    <span class="hero-kpi-val neutral">{latest.get('close', 'N/A')}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Compact AI Commentary ──
    st.markdown(f"""
    <div class="ai-compact {comment_border}">
        <span class="ai-compact-tag">🎯 系統短評</span>
        <span class="ai-compact-text">{ai_comment}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Date Range Filter ──
    range_options = {"1個月": 22, "3個月": 65, "6個月": 130, "1年": 252, "全期間": None}
    _, _, _, col_range = st.columns([2, 1, 1, 3])
    with col_range:
        selected_range = st.radio(
            "時間範圍", list(range_options.keys()),
            index=1,  # default = 3個月
            horizontal=True, label_visibility="collapsed",
        )

    # ── Chart Data Prep ──
    n_days = range_options[selected_range]
    df_chart = df.tail(n_days) if n_days else df.copy()

    # ── 3-Row Chart layout ──
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2],
        vertical_spacing=0.03,
        specs=[[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}]],
    )

    # Row 1: Stock price — line with markers
    fig.add_trace(go.Scatter(
        x=df_chart['date'], y=df_chart['close'], name='收盤價',
        mode='lines+markers',
        line=dict(color='#06B6D4', width=2.5),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor='rgba(6, 182, 212, 0.06)',
        hovertemplate='收盤價：%{y}<extra></extra>'
    ), row=1, col=1, secondary_y=False)

    # Row 1: Sentiment — Single line
    fig.add_trace(go.Scatter(
        x=df_chart['date'], y=df_chart['avg_sentiment'], name='情緒分數',
        mode='lines',
        line=dict(color='rgba(139, 92, 246, 0.8)', width=1.5),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.08)',
        hovertemplate='情緒：%{y:.3f}<extra></extra>',
    ), row=1, col=1, secondary_y=True)

    # Row 2: Stock Volume
    if 'volume' in df_chart.columns:
        fig.add_trace(go.Bar(
            x=df_chart['date'], y=df_chart['volume'], name='股票成交量',
            marker_color='rgba(148, 163, 184, 0.35)',
            hovertemplate='成交量：%{y:,.0f} 股<extra></extra>'
        ), row=2, col=1)

    thresholds_data = fetch_thresholds()
    _sp90 = thresholds_data.get('情緒分數_P90', 0.62)
    _sp10 = thresholds_data.get('情緒分數_P10', 0.13)

    # Signal markers on price
    signals_chart = df_chart[df_chart['signal'].astype(str).str.contains("🔴|🟢|🟡", na=False)]
    if not signals_chart.empty:
        marker_colors = []
        marker_labels = []
        for s in signals_chart['signal']:
            s_str = str(s)
            if "🔴" in s_str:
                marker_colors.append('#EF4444')
                marker_labels.append('利多出盡')
            elif "🟢" in s_str:
                marker_colors.append('#10B981')
                marker_labels.append('超賣反彈')
            else:
                marker_colors.append('#F59E0B')
                marker_labels.append('觀望')

        fig.add_trace(go.Scatter(
            x=signals_chart['date'], y=signals_chart['close'],
            mode='markers', name='背離訊號',
            marker=dict(
                size=12, symbol='diamond',
                color=marker_colors,
                line=dict(width=2, color='white'),
            ),
            text=marker_labels,
            hovertemplate='%{text}<br>收盤價：%{y}<br>%{x}<extra></extra>'
        ), row=1, col=1, secondary_y=False)

    # Row 3: News Volume Bar Chart
    if 'news_count' in df_chart.columns:
        bar_colors = [
            'rgba(239, 68, 68, 0.6)' if s > _sp90 else
            'rgba(16, 185, 129, 0.6)' if s < _sp10 else
            'rgba(100, 116, 139, 0.35)'
            for s in df_chart['avg_sentiment']
        ]
        fig.add_trace(go.Bar(
            x=df_chart['date'], y=df_chart['news_count'], name='新聞量',
            marker_color=bar_colors,
            hovertemplate='新聞量：%{y} 篇<extra></extra>',
        ), row=3, col=1)

    fig.update_layout(
        height=600,
        title_text=f"<b>{selected_stock} {stock_name}</b>　情緒分數 × 股價 × 成交量 × 新聞量（{selected_range}）",
        **PLOTLY_LAYOUT,
        barmode='overlay',
    )
    fig.update_yaxes(title_text="收盤價", row=1, col=1, secondary_y=False, gridcolor="rgba(148,163,184,0.06)")
    fig.update_yaxes(title_text="情緒 [-1, 1]", row=1, col=1, secondary_y=True, range=[-1, 1], gridcolor="rgba(148,163,184,0.06)")
    fig.update_yaxes(title_text="成交量", row=2, col=1, gridcolor="rgba(148,163,184,0.06)")
    fig.update_yaxes(title_text="新聞量", row=3, col=1, gridcolor="rgba(148,163,184,0.06)")
    fig.update_xaxes(
        gridcolor="rgba(148,163,184,0.06)",
        rangebreaks=[dict(bounds=["sat", "mon"])]
    )

    st.plotly_chart(fig, use_container_width=True)
