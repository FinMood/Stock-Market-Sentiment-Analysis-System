import streamlit as st



STOCK_NAMES = {
    "2330": "台積電",
    "2308": "台達電",
    "2454": "聯發科",
}

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
