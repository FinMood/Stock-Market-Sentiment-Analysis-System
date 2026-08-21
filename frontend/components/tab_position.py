import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from frontend.data_fetch import fetch_thresholds

def render(selected_stock, stock_name, df):
    """Page 2: 歷史背離訊號分析"""


    latest = df.iloc[-1]
    last_signal = str(latest.get("signal", "—"))
    last_sentiment = round(float(latest.get("avg_sentiment", 0)), 3)
    last_return_raw = latest.get("return_3d", None)
    last_return = round(float(last_return_raw), 4) if pd.notnull(last_return_raw) else None
    sentiment_level = latest.get('sentiment_level', '—')
    return_level = latest.get('return_level', '—')

    if "🔴" in last_signal: signal_class = "red"
    elif "🟢" in last_signal: signal_class = "green"
    elif "🟡" in last_signal: signal_class = "amber"
    else: signal_class = "neutral"


    # ── Percentile Position Bars ──
    st.markdown('<div class="section-title compact"><span class="icon">📊</span>歷史位階分析 Percentile Position<span class="line"></span></div>', unsafe_allow_html=True)

    thresholds = fetch_thresholds()
    sent_p10 = thresholds.get('情緒分數_P10', 0.13)
    sent_p25 = thresholds.get('情緒分數_P25', 0.28)
    sent_p75 = thresholds.get('情緒分數_P75', 0.55)
    sent_p90 = thresholds.get('情緒分數_P90', 0.62)
    ret_p10 = thresholds.get('漲跌幅_P10', -0.051)
    ret_p25 = thresholds.get('漲跌幅_P25', -0.028)
    ret_p75 = thresholds.get('漲跌幅_P75', 0.058)
    ret_p90 = thresholds.get('漲跌幅_P90', 0.109)

    return_val_num = float(last_return) if pd.notnull(last_return) else 0

    def _build_percentile_bar(label, value, value_fmt, p10, p25, p75, p90, range_min, range_max, zones):
        """Build a horizontal percentile bar chart using Plotly shapes."""
        fig = go.Figure()
        total = range_max - range_min

        # Zone colors and labels
        boundaries = [range_min, p10, p25, p75, p90, range_max]
        for i in range(5):
            fig.add_shape(
                type="rect",
                x0=boundaries[i], x1=boundaries[i+1], y0=0, y1=1,
                fillcolor=zones[i]["color"],
                line=dict(width=0),
                layer="below",
            )
            # Zone label in center
            cx = (boundaries[i] + boundaries[i+1]) / 2
            fig.add_annotation(
                x=cx, y=0.5,
                text=zones[i]["label"],
                showarrow=False,
                font=dict(size=13, color="rgba(241,245,249,0.85)", family="Noto Sans TC, sans-serif"),
            )

        # Percentile boundary lines & labels
        for pval, plabel in [(p10, "P10"), (p25, "P25"), (p75, "P75"), (p90, "P90")]:
            fig.add_shape(
                type="line",
                x0=pval, x1=pval, y0=-0.05, y1=1.05,
                line=dict(color="rgba(241,245,249,0.4)", width=1, dash="dot"),
            )
            fig.add_annotation(
                x=pval, y=-0.22,
                text=f"<b>{plabel}</b><br>{pval:.3f}" if abs(pval) < 1 else f"<b>{plabel}</b><br>{pval:.1%}",
                showarrow=False,
                font=dict(size=11, color="#94A3B8"),
            )

        # Current value marker (triangle)
        clamped_val = max(range_min, min(range_max, value))
        fig.add_trace(go.Scatter(
            x=[clamped_val], y=[1.18],
            mode="markers+text",
            marker=dict(symbol="triangle-down", size=16, color="#F1F5F9"),
            text=[f"<b>{value_fmt}</b>"],
            textposition="top center",
            textfont=dict(size=17, color="#F1F5F9", family="Inter"),
            hoverinfo="skip",
            showlegend=False,
        ))

        fig.update_layout(
            height=130,
            template="plotly_dark",
            paper_bgcolor="rgba(11, 17, 32, 0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, Noto Sans TC, sans-serif", color="#94A3B8"),
            margin=dict(l=10, r=10, t=40, b=35),
            xaxis=dict(
                range=[range_min, range_max],
                showgrid=False, zeroline=False, showticklabels=False,
                fixedrange=True,
            ),
            yaxis=dict(
                range=[-0.4, 1.5],
                showgrid=False, zeroline=False, showticklabels=False,
                fixedrange=True,
            ),
            title=dict(
                text=f"<b>{label}</b>",
                font=dict(size=13, color="#CBD5E1"),
                x=0, xanchor="left",
            ),
            hovermode=False,
        )
        return fig

    # ── Sentiment Percentile Bar ──
    sent_zones = [
        {"color": "rgba(30, 58, 138, 0.7)",  "label": "🔴 極度悲觀"},
        {"color": "rgba(59, 130, 246, 0.4)",  "label": "🟠 偏空"},
        {"color": "rgba(100, 116, 139, 0.25)", "label": "⚪ 中性"},
        {"color": "rgba(245, 158, 11, 0.35)",  "label": "🟢 偏多"},
        {"color": "rgba(239, 68, 68, 0.55)",   "label": "🟢🟢 極度樂觀"},
    ]
    fig_sent_bar = _build_percentile_bar(
        label="🧠 情緒位階 — 目前新聞輿情落在歷史的哪個區間？",
        value=last_sentiment,
        value_fmt=f"{last_sentiment:+.3f}",
        p10=sent_p10, p25=sent_p25, p75=sent_p75, p90=sent_p90,
        range_min=-1, range_max=1,
        zones=sent_zones,
    )
    st.plotly_chart(fig_sent_bar, use_container_width=True, config={'staticPlot': True})

    # ── Return Percentile Bar ──
    ret_range_max = max(0.15, abs(ret_p90) * 1.5, abs(ret_p10) * 1.5, abs(return_val_num) * 1.3)
    ret_range_min = -ret_range_max
    ret_zones = [
        {"color": "rgba(16, 185, 129, 0.5)",   "label": "📉 大跌"},
        {"color": "rgba(16, 185, 129, 0.2)",   "label": "小跌"},
        {"color": "rgba(100, 116, 139, 0.25)",  "label": "平盤震盪"},
        {"color": "rgba(239, 68, 68, 0.2)",     "label": "小漲"},
        {"color": "rgba(239, 68, 68, 0.5)",     "label": "📈 大漲"},
    ]
    fig_ret_bar = _build_percentile_bar(
        label="📊 漲跌位階 — 近 3 日股價累積漲跌在歷史的哪個區間？",
        value=return_val_num,
        value_fmt=f"{return_val_num:+.2%}",
        p10=ret_p10, p25=ret_p25, p75=ret_p75, p90=ret_p90,
        range_min=ret_range_min, range_max=ret_range_max,
        zones=ret_zones,
    )
    st.plotly_chart(fig_ret_bar, use_container_width=True, config={'staticPlot': True})

    # ── Combination Analysis ──
    combo_text = f"情緒：<b>{sentiment_level}</b> ＋ 漲跌：<b>{return_level}</b>"
    if signal_class == "red":
        combo_icon = "🔴"
        combo_result = "紅燈警示 — 利多出盡，新聞極度樂觀但股價已偷漲完畢，追高風險極大"
        combo_border_color = "rgba(239, 68, 68, 0.4)"
        combo_bg = "rgba(239, 68, 68, 0.08)"
    elif signal_class == "green":
        combo_icon = "🟢"
        combo_result = "綠燈提示 — 超賣反彈，新聞極度恐慌且股價已連跌，歷史統計反彈機率高"
        combo_border_color = "rgba(16, 185, 129, 0.4)"
        combo_bg = "rgba(16, 185, 129, 0.08)"
    elif signal_class == "amber":
        combo_icon = "🟡"
        combo_result = "黃燈觀望 — 情緒與股價方向不一致，不確定性高，建議等待確認"
        combo_border_color = "rgba(245, 158, 11, 0.4)"
        combo_bg = "rgba(245, 158, 11, 0.08)"
    else:
        combo_icon = "⚪"
        combo_result = "正常 — 情緒與股價走勢一致，無明顯背離，依個人策略操作"
        combo_border_color = "rgba(148, 163, 184, 0.2)"
        combo_bg = "rgba(148, 163, 184, 0.05)"

    st.markdown(f"""
    <div style="
        margin-top: 8px;
        padding: 16px 20px;
        background: {combo_bg};
        border: 1px solid {combo_border_color};
        border-radius: var(--radius-md);
        font-size: 17px;
        color: var(--text-secondary);
        line-height: 1.7;
    ">
        <div style="font-size: 15px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;">📐 組合研判 Combination Analysis</div>
        <div>{combo_text} → <span style="font-size: 19px;">{combo_icon}</span> <b>{combo_result}</b></div>
        <div style="font-size: 14px; color: var(--text-muted); margin-top: 8px;">💡 當情緒進入極端區（P90以上或P10以下），且漲跌方向與情緒一致時，即觸發背離訊號。</div>
    </div>
    """, unsafe_allow_html=True)
