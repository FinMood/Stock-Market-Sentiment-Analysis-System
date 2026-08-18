import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ================= Configuration =================
st.set_page_config(
    page_title="FinMood | 股市情緒防呆決策系統",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
API_BASE = "http://localhost:8079/api"

# ================= CSS Design System =================
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

/* ── CSS Variables (Design Tokens) ── */
:root {
    --bg-primary: #0B1120;
    --bg-secondary: #111827;
    --bg-card: rgba(15, 23, 42, 0.7);
    --bg-card-hover: rgba(30, 41, 59, 0.8);
    --border-subtle: rgba(148, 163, 184, 0.12);
    --border-glow-green: rgba(16, 185, 129, 0.4);
    --border-glow-red: rgba(239, 68, 68, 0.4);
    --border-glow-amber: rgba(245, 158, 11, 0.4);
    --accent-green: #10B981;
    --accent-green-dim: #065F46;
    --accent-red: #EF4444;
    --accent-red-dim: #7F1D1D;
    --accent-amber: #F59E0B;
    --accent-amber-dim: #78350F;
    --accent-cyan: #06B6D4;
    --text-primary: #F1F5F9;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
    --shadow-glow-green: 0 0 20px rgba(16, 185, 129, 0.15);
    --shadow-glow-red: 0 0 20px rgba(239, 68, 68, 0.15);
    --transition-fast: 0.2s ease;
    --transition-normal: 0.3s ease;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans TC', sans-serif !important;
}

.stApp {
    background: linear-gradient(145deg, var(--bg-primary) 0%, #0F172A 50%, #111827 100%) !important;
}

/* ── Sidebar Branding ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F1724 0%, #0B1120 100%) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

section[data-testid="stSidebar"] .stRadio > label {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 8px 12px !important;
    border-radius: var(--radius-sm) !important;
    transition: var(--transition-normal) !important;
    margin-bottom: 4px !important;
}

section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
    background: rgba(148, 163, 184, 0.08) !important;
    color: var(--text-primary) !important;
}

section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"],
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[aria-checked="true"] {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.1)) !important;
    color: var(--accent-green) !important;
    border-left: 3px solid var(--accent-green) !important;
}

/* ── Headers ── */
h1, h2, h3 {
    font-family: 'Inter', 'Noto Sans TC', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
}

h1 { font-weight: 800 !important; font-size: 2rem !important; }
h2 { font-weight: 700 !important; }
h3 { font-weight: 600 !important; color: var(--text-secondary) !important; }

/* ── Streamlit Metric Override ── */
div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    padding: 20px 24px !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    box-shadow: var(--shadow-card) !important;
    transition: var(--transition-normal) !important;
}

div[data-testid="stMetric"]:hover {
    border-color: rgba(6, 182, 212, 0.3) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-card), 0 0 15px rgba(6, 182, 212, 0.1) !important;
}

div[data-testid="stMetric"] label {
    color: var(--text-secondary) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}

/* ── Custom Glassmorphism Card ── */
.glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 28px 32px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: var(--shadow-card);
    margin-bottom: 24px;
    transition: var(--transition-normal);
}

.glass-card:hover {
    border-color: rgba(148, 163, 184, 0.2);
    transform: translateY(-1px);
}

/* ── Signal Light Component ── */
.signal-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 36px 24px;
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.6));
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: var(--shadow-card);
    position: relative;
    overflow: hidden;
}

.signal-container::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
    opacity: 0.6;
}

.signal-light {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    font-weight: 800;
    position: relative;
    margin-bottom: 16px;
}

.signal-light.red {
    background: radial-gradient(circle, #EF4444 0%, #991B1B 70%);
    box-shadow: 0 0 30px rgba(239, 68, 68, 0.5), 0 0 60px rgba(239, 68, 68, 0.2), inset 0 -4px 8px rgba(0,0,0,0.3);
    animation: pulse-red 2s ease-in-out infinite;
}

.signal-light.green {
    background: radial-gradient(circle, #10B981 0%, #065F46 70%);
    box-shadow: 0 0 30px rgba(16, 185, 129, 0.5), 0 0 60px rgba(16, 185, 129, 0.2), inset 0 -4px 8px rgba(0,0,0,0.3);
    animation: pulse-green 2s ease-in-out infinite;
}

.signal-light.amber {
    background: radial-gradient(circle, #F59E0B 0%, #78350F 70%);
    box-shadow: 0 0 30px rgba(245, 158, 11, 0.5), 0 0 60px rgba(245, 158, 11, 0.2), inset 0 -4px 8px rgba(0,0,0,0.3);
    animation: pulse-amber 2s ease-in-out infinite;
}

.signal-light.neutral {
    background: radial-gradient(circle, #64748B 0%, #334155 70%);
    box-shadow: 0 0 20px rgba(100, 116, 139, 0.3), inset 0 -4px 8px rgba(0,0,0,0.3);
}

@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 30px rgba(239, 68, 68, 0.5), 0 0 60px rgba(239, 68, 68, 0.2); }
    50% { box-shadow: 0 0 40px rgba(239, 68, 68, 0.7), 0 0 80px rgba(239, 68, 68, 0.35); }
}

@keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 30px rgba(16, 185, 129, 0.5), 0 0 60px rgba(16, 185, 129, 0.2); }
    50% { box-shadow: 0 0 40px rgba(16, 185, 129, 0.7), 0 0 80px rgba(16, 185, 129, 0.35); }
}

@keyframes pulse-amber {
    0%, 100% { box-shadow: 0 0 30px rgba(245, 158, 11, 0.5), 0 0 60px rgba(245, 158, 11, 0.2); }
    50% { box-shadow: 0 0 40px rgba(245, 158, 11, 0.7), 0 0 80px rgba(245, 158, 11, 0.35); }
}

.signal-label {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    margin-top: 8px;
    letter-spacing: -0.01em;
}

.signal-sublabel {
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 4px;
}

/* ── AI Commentary Card ── */
.ai-comment-card {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.6));
    border: 1px solid;
    border-radius: var(--radius-lg);
    padding: 20px 24px;
    margin: 16px 0 24px 0;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}

.ai-comment-card.red-border { border-color: var(--border-glow-red); }
.ai-comment-card.green-border { border-color: var(--border-glow-green); }
.ai-comment-card.amber-border { border-color: var(--border-glow-amber); }
.ai-comment-card.neutral-border { border-color: var(--border-subtle); }

.ai-comment-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 3px;
}

.ai-comment-card.red-border::before { background: var(--accent-red); }
.ai-comment-card.green-border::before { background: var(--accent-green); }
.ai-comment-card.amber-border::before { background: var(--accent-amber); }
.ai-comment-card.neutral-border::before { background: var(--text-muted); }

.ai-comment-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}

.ai-comment-text {
    font-size: 15px;
    color: var(--text-primary);
    line-height: 1.7;
}

/* ── KPI Card ── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 24px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: var(--shadow-card);
    transition: var(--transition-normal);
    text-align: center;
}

.kpi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(6, 182, 212, 0.25);
}

.kpi-icon {
    font-size: 28px;
    margin-bottom: 8px;
}

.kpi-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}

.kpi-value.positive { color: var(--accent-green); }
.kpi-value.negative { color: var(--accent-red); }
.kpi-value.neutral { color: var(--text-primary); }

.kpi-sub {
    font-size: 12px;
    color: var(--text-muted);
}

/* ── HERO Signal Banner ── */
.hero-banner {
    position: relative;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.6));
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    padding: 28px 32px 20px;
    margin-bottom: 16px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.3s;
}

.hero-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}

.hero-banner.red {
    border-color: rgba(239, 68, 68, 0.35);
    box-shadow: 0 4px 40px rgba(239, 68, 68, 0.1);
}
.hero-banner.red::before { background: linear-gradient(90deg, #EF4444, #F87171, #EF4444); }

.hero-banner.green {
    border-color: rgba(16, 185, 129, 0.35);
    box-shadow: 0 4px 40px rgba(16, 185, 129, 0.1);
}
.hero-banner.green::before { background: linear-gradient(90deg, #10B981, #34D399, #10B981); }

.hero-banner.amber {
    border-color: rgba(245, 158, 11, 0.35);
    box-shadow: 0 4px 40px rgba(245, 158, 11, 0.08);
}
.hero-banner.amber::before { background: linear-gradient(90deg, #F59E0B, #FBBF24, #F59E0B); }

.hero-banner.neutral {
    border-color: var(--border-subtle);
}
.hero-banner.neutral::before { background: linear-gradient(90deg, #64748B, #94A3B8, #64748B); }

.hero-top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.hero-stock {
    display: flex;
    align-items: baseline;
    gap: 10px;
}

.hero-stock-name {
    font-size: 22px;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}

.hero-stock-id {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-muted);
    background: rgba(148, 163, 184, 0.1);
    padding: 2px 10px;
    border-radius: 20px;
}

.hero-date {
    font-size: 12px;
    color: var(--text-muted);
}

.hero-main {
    display: flex;
    align-items: center;
    gap: 28px;
    margin-bottom: 24px;
}

.hero-light-wrap {
    flex-shrink: 0;
}

.hero-light {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
}

.hero-light.red {
    background: radial-gradient(circle, #EF4444 0%, #991B1B 70%);
    box-shadow: 0 0 24px rgba(239, 68, 68, 0.6), 0 0 60px rgba(239, 68, 68, 0.2);
    animation: pulse-red 2s ease-in-out infinite;
}

.hero-light.green {
    background: radial-gradient(circle, #10B981 0%, #065F46 70%);
    box-shadow: 0 0 24px rgba(16, 185, 129, 0.6), 0 0 60px rgba(16, 185, 129, 0.2);
    animation: pulse-green 2s ease-in-out infinite;
}

.hero-light.amber {
    background: radial-gradient(circle, #F59E0B 0%, #78350F 70%);
    box-shadow: 0 0 24px rgba(245, 158, 11, 0.6), 0 0 60px rgba(245, 158, 11, 0.2);
    animation: pulse-amber 2s ease-in-out infinite;
}

.hero-light.neutral {
    background: radial-gradient(circle, #64748B 0%, #334155 70%);
    box-shadow: 0 0 16px rgba(100, 116, 139, 0.3);
}

.hero-text {
    flex: 1;
}

.hero-subtitle {
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}

.hero-banner.red .hero-subtitle { color: #F87171; }
.hero-banner.green .hero-subtitle { color: #34D399; }
.hero-banner.amber .hero-subtitle { color: #FBBF24; }
.hero-banner.neutral .hero-subtitle { color: #94A3B8; }

.hero-label {
    font-size: 36px;
    font-weight: 900;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin-bottom: 6px;
}

.hero-banner.red .hero-label { color: #EF4444; }
.hero-banner.green .hero-label { color: #10B981; }
.hero-banner.amber .hero-label { color: #F59E0B; }
.hero-banner.neutral .hero-label { color: var(--text-primary); }

.hero-desc {
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.5;
}

.hero-kpi-row {
    display: flex;
    align-items: center;
    gap: 0;
    padding-top: 16px;
    border-top: 1px solid rgba(148, 163, 184, 0.08);
}

.hero-kpi {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
}

.hero-kpi-divider {
    width: 1px;
    height: 32px;
    background: rgba(148, 163, 184, 0.12);
}

.hero-kpi-name {
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 500;
}

.hero-kpi-val {
    font-size: 16px;
    font-weight: 800;
    letter-spacing: -0.01em;
}

.hero-kpi-val.positive { color: var(--accent-green); }
.hero-kpi-val.negative { color: var(--accent-red); }
.hero-kpi-val.neutral { color: var(--text-primary); }

/* ── Compact AI Comment ── */
.ai-compact {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.7), rgba(30, 41, 59, 0.5));
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 12px 18px;
    margin-bottom: 16px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    position: relative;
    overflow: hidden;
}

.ai-compact::before {
    content: '';
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 3px;
}

.ai-compact.red-border { border-color: rgba(239, 68, 68, 0.25); }
.ai-compact.red-border::before { background: var(--accent-red); }
.ai-compact.green-border { border-color: rgba(16, 185, 129, 0.25); }
.ai-compact.green-border::before { background: var(--accent-green); }
.ai-compact.amber-border { border-color: rgba(245, 158, 11, 0.25); }
.ai-compact.amber-border::before { background: var(--accent-amber); }
.ai-compact.neutral-border::before { background: var(--text-muted); }

.ai-compact-tag {
    font-size: 10px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    white-space: nowrap;
    padding-top: 2px;
}

.ai-compact-text {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
}

/* ── Stats Card (Page 2) ── */
.stats-row {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
}

.stat-card {
    flex: 1;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 24px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: var(--shadow-card);
    text-align: center;
    transition: var(--transition-normal);
}

.stat-card:hover {
    transform: translateY(-2px);
}

.stat-card.red-glow {
    border-color: rgba(239, 68, 68, 0.2);
}

.stat-card.red-glow:hover {
    box-shadow: var(--shadow-card), var(--shadow-glow-red);
}

.stat-card.green-glow {
    border-color: rgba(16, 185, 129, 0.2);
}

.stat-card.green-glow:hover {
    box-shadow: var(--shadow-card), var(--shadow-glow-green);
}

.stat-number {
    font-size: 36px;
    font-weight: 800;
    letter-spacing: -0.02em;
}

.stat-number.red { color: var(--accent-red); }
.stat-number.green { color: var(--accent-green); }
.stat-number.amber { color: var(--accent-amber); }

.stat-desc {
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 8px;
}

/* ── Section Title ── */
.section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 32px 0 16px 0;
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
}

.section-title.compact {
    margin: 16px 0 10px 0;
    font-size: 16px;
}

.section-title .icon {
    font-size: 22px;
}

.section-title .line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border-subtle), transparent);
}

/* ── Streamlit Overrides for info/warning/error ── */
div[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border: none !important;
    backdrop-filter: blur(8px) !important;
}

/* ── Dataframe Overrides ── */
.stDataFrame {
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
}

/* ── Plotly Chart Container ── */
div[data-testid="stPlotlyChart"] {
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
    border: 1px solid var(--border-subtle) !important;
    box-shadow: var(--shadow-card) !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--border-subtle), transparent) !important;
    margin: 28px 0 !important;
}

/* ── Selectbox ── */
div[data-testid="stSelectbox"] label {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
}

/* ── Page 3 placeholder ── */
.placeholder-card {
    background: var(--bg-card);
    border: 1px dashed rgba(148, 163, 184, 0.2);
    border-radius: var(--radius-xl);
    padding: 60px 40px;
    text-align: center;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.placeholder-icon {
    font-size: 64px;
    margin-bottom: 16px;
    opacity: 0.7;
}

.placeholder-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 12px;
}

.placeholder-desc {
    font-size: 15px;
    color: var(--text-muted);
    line-height: 1.7;
    max-width: 500px;
    margin: 0 auto;
}

/* ── Brand in Sidebar ── */
.sidebar-brand {
    text-align: center;
    padding: 24px 16px 32px 16px;
    margin-bottom: 8px;
    border-bottom: 1px solid var(--border-subtle);
}

.sidebar-brand .logo {
    font-size: 32px;
    margin-bottom: 4px;
}

.sidebar-brand .name {
    font-size: 24px;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
}

.sidebar-brand .tagline {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 4px;
    letter-spacing: 0.05em;
}

.sidebar-footer {
    position: fixed;
    bottom: 16px;
    padding: 12px 24px;
    font-size: 11px;
    color: var(--text-muted);
}
</style>
""", unsafe_allow_html=True)

# ================= Constants =================
STOCK_NAMES = {
    "2330": "台積電",
    "2308": "台達電",
    "2454": "聯發科",
}

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

def page_overview():
    """Page 1: 個股決策總覽"""

    # ── Stock Selector (compact) ──
    stock_options = [f"{sid} {STOCK_NAMES.get(sid, '')}" for sid in STOCK_NAMES]
    col_sel, _ = st.columns([1, 5])
    with col_sel:
        selected_label = st.selectbox("標的", stock_options, label_visibility="collapsed")
    selected_stock = selected_label.split(" ")[0]
    stock_name = STOCK_NAMES.get(selected_stock, "")

    df = fetch_stock_data(selected_stock)

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
                <span class="hero-stock-name">{stock_name}</span>
                <span class="hero-stock-id">{selected_stock}</span>
            </div>
            <span class="hero-date">{date_str} 更新</span>
        </div>
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
                <span class="hero-kpi-name">🧠 情緒分數</span>
                <span class="hero-kpi-val {sentiment_color}">{sentiment_val}</span>
            </div>
            <div class="hero-kpi-divider"></div>
            <div class="hero-kpi">
                <span class="hero-kpi-name">📊 T-3 漲跌</span>
                <span class="hero-kpi-val {return_color}">{return_val}</span>
            </div>
            <div class="hero-kpi-divider"></div>
            <div class="hero-kpi">
                <span class="hero-kpi-name">📰 新聞量</span>
                <span class="hero-kpi-val neutral">{int(latest.get('news_count', 0))} 篇</span>
            </div>
            <div class="hero-kpi-divider"></div>
            <div class="hero-kpi">
                <span class="hero-kpi-name">💰 收盤價</span>
                <span class="hero-kpi-val neutral">{latest.get('close', 'N/A')}</span>
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
    range_options = {"一週": 5, "一月": 22, "一年": 252, "全期間": None}
    _, _, _, col_range = st.columns([3, 1, 1, 2])
    with col_range:
        selected_range = st.radio(
            "時間範圍", list(range_options.keys()),
            index=1,  # default = 一月
            horizontal=True, label_visibility="collapsed",
        )

    n_days = range_options[selected_range]
    df_chart = df.tail(n_days) if n_days else df.copy()

    # ── Dual Axis Chart (immediately visible, no scrolling) ──
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Stock price — line with subtle fill
    fig.add_trace(go.Scatter(
        x=df_chart['date'], y=df_chart['close'], name='收盤價',
        mode='lines+markers',
        line=dict(color='#06B6D4', width=2.5),
        marker=dict(size=5),
        fill='tozeroy',
        fillcolor='rgba(6, 182, 212, 0.06)',
    ), secondary_y=False)

    # Sentiment — dual-colored area (positive red area above 0, negative green area below 0)
    sent_pos = df_chart['avg_sentiment'].clip(lower=0)
    sent_neg = df_chart['avg_sentiment'].clip(upper=0)

    fig.add_trace(go.Scatter(
        x=df_chart['date'], y=sent_pos, name='情緒 (偏多)',
        mode='lines+markers',
        line=dict(color='rgba(239, 68, 68, 0.8)', width=1.5),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.15)',
        hovertemplate='%{y:.3f}<extra>偏多</extra>',
    ), secondary_y=True)

    fig.add_trace(go.Scatter(
        x=df_chart['date'], y=sent_neg, name='情緒 (偏空)',
        mode='lines+markers',
        line=dict(color='rgba(16, 185, 129, 0.8)', width=1.5),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.15)',
        hovertemplate='%{y:.3f}<extra>偏空</extra>',
    ), secondary_y=True)

    # Signal markers
    signals_chart = df_chart[df_chart['signal'].astype(str).str.contains("🔴|🟢|🟡", na=False)]
    if not signals_chart.empty:
        marker_colors = []
        for s in signals_chart['signal']:
            s_str = str(s)
            if "🔴" in s_str:
                marker_colors.append('#EF4444')
            elif "🟢" in s_str:
                marker_colors.append('#10B981')
            else:
                marker_colors.append('#F59E0B')

        fig.add_trace(go.Scatter(
            x=signals_chart['date'], y=signals_chart['close'],
            mode='markers', name='防呆訊號',
            marker=dict(
                size=14, symbol='diamond',
                color=marker_colors,
                line=dict(width=2, color='white'),
            ),
            text=signals_chart['signal'], hoverinfo='text+x+y'
        ), secondary_y=False)

    fig.update_layout(
        height=460,
        title_text=f"<b>{selected_stock} {stock_name}</b>　情緒 × 股價（{selected_range}）",
        **PLOTLY_LAYOUT
    )
    fig.update_yaxes(title_text="收盤價 (TWD)", secondary_y=False, gridcolor="rgba(148,163,184,0.06)")
    fig.update_yaxes(title_text="情緒分數 [-1, 1]", secondary_y=True, range=[-1, 1], gridcolor="rgba(148,163,184,0.06)")
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.06)")

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Gauge Charts ──
    st.markdown('<div class="section-title compact"><span class="icon">🎛️</span>位階儀表板 Percentile Gauges<span class="line"></span></div>', unsafe_allow_html=True)

    # 針對使用者解釋燈號意義
    st.markdown("""
    <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 24px; padding: 12px 16px; background: rgba(148, 163, 184, 0.05); border-radius: var(--radius-sm); border-left: 3px solid var(--accent-cyan);">
        💡 <b>防呆燈號怎麼看？</b><br>
        【情緒熱度】若進入高溫區（紅色區塊），加上【漲跌位階】同在高點（近期偷漲完畢），系統就會亮起 <b>🔴 紅燈：代表高度警示的「利多出盡」</b>。<br>
        反觀若【情緒熱度】進入低溫區（藍色區塊），且【漲跌位階】也在低檔，則會點亮 <b>🟢 綠燈：代表可能是「超賣反彈機會」</b>。
    </div>
    """, unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        # 情緒儀表板改為「溫度」色系
        fig_gauge_sent = go.Figure(go.Indicator(
            mode="gauge+number",
            value=last_sentiment,
            number=dict(font=dict(size=32, color="#F1F5F9"), valueformat="+.3f"),
            title=dict(text="情緒熱度指標 (Temperature)", font=dict(size=13, color="#94A3B8")),
            gauge=dict(
                axis=dict(range=[-1, 1], tickcolor="#64748B", dtick=0.5),
                bar=dict(color="#F1F5F9", thickness=0.2), # 指針變細
                bgcolor="rgba(30, 41, 59, 0.5)",
                borderwidth=0,
                steps=[
                    dict(range=[-1, -0.5], color="#1E3A8A"), # 極寒
                    dict(range=[-0.5, 0], color="#3B82F6"),  # 微冷
                    dict(range=[0, 0.5], color="#F59E0B"),   # 微熱
                    dict(range=[0.5, 1], color="#EF4444"),   # 極熱
                ],
                threshold=dict(line=dict(color="#F1F5F9", width=2), thickness=0.8, value=last_sentiment),
            ),
        ))
        fig_gauge_sent.update_layout(hovermode=False, height=240, **{k: v for k, v in PLOTLY_LAYOUT.items() if k != 'xaxis' and k != 'yaxis'})
        st.plotly_chart(fig_gauge_sent, use_container_width=True, config={'staticPlot': True})

    with col_g2:
        return_val_num = float(last_return) if pd.notnull(last_return) else 0
        # 動態上限：預設至少展現 ±15%，若漲幅超過則動態擴大儀表範圍
        max_bound = max(0.15, abs(return_val_num) * 1.2)

        fig_gauge_ret = go.Figure(go.Indicator(
            mode="gauge+number",
            value=return_val_num,
            number=dict(font=dict(size=32, color="#F1F5F9"), valueformat="+.2%"),
            title=dict(text="近 3 日漲跌位階", font=dict(size=13, color="#94A3B8")),
            gauge=dict(
                axis=dict(range=[-max_bound, max_bound], tickcolor="#64748B", tickformat=".0%", dtick=round(max_bound/3, 2)),
                bar=dict(color="#F1F5F9", thickness=0.2),
                bgcolor="rgba(30, 41, 59, 0.5)",
                borderwidth=0,
                steps=[
                    dict(range=[-max_bound, -max_bound/3], color="rgba(16, 185, 129, 0.3)"), # 大跌
                    dict(range=[-max_bound/3, 0], color="rgba(16, 185, 129, 0.1)"),          # 小跌
                    dict(range=[0, max_bound/3], color="rgba(239, 68, 68, 0.1)"),            # 小漲
                    dict(range=[max_bound/3, max_bound], color="rgba(239, 68, 68, 0.3)"),    # 大漲
                ],
                threshold=dict(line=dict(color="#F1F5F9", width=2), thickness=0.8, value=return_val_num),
            ),
        ))
        fig_gauge_ret.update_layout(hovermode=False, height=240, **{k: v for k, v in PLOTLY_LAYOUT.items() if k != 'xaxis' and k != 'yaxis'})
        st.plotly_chart(fig_gauge_ret, use_container_width=True, config={'staticPlot': True})


def page_signals():
    """Page 2: 歷史背離訊號分析"""

    st.markdown('<div class="section-title"><span class="icon">🚦</span>歷史背離訊號分析 Divergence Analysis<span class="line"></span></div>', unsafe_allow_html=True)

    df_all = fetch_all_signals()

    if df_all.empty:
        st.markdown("""
        <div class="placeholder-card">
            <div class="placeholder-icon">📡</div>
            <div class="placeholder-title">請先啟動 API 服務</div>
            <div class="placeholder-desc">確認 FastAPI 後端已運行，並已完成資料管線。</div>
        </div>
        """, unsafe_allow_html=True)
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
            <div class="ai-comment-text">需計算 T+3 實際跌幅機率，此區域為回測統計預留欄位。連接歷史數據後將自動更新。</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="ai-comment-card green-border">
            <div class="ai-comment-title">🔺 綠燈後反彈機率</div>
            <div class="ai-comment-text">需計算 T+3 實際反彈機率，此區域為回測統計預留欄位。連接歷史數據後將自動更新。</div>
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
    )


def page_engines():
    """Page 3: 演算法引擎觀測站"""

    st.markdown('<div class="section-title"><span class="icon">🧠</span>演算法引擎觀測站 Engine Comparison<span class="line"></span></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="placeholder-card">
        <div class="placeholder-icon">🔬</div>
        <div class="placeholder-title">引擎比較分析 — 開發中</div>
        <div class="placeholder-desc">
            此頁面將展示 5 大核心引擎的個別預測對比矩陣與一致率（Consensus）分析。<br><br>
            <strong>規劃功能</strong><br>
            📊 多模型情緒熱區分佈圖（Heatmap）<br>
            📈 引擎一致性趨勢圖（Consensus Chart）<br>
            🔍 個別引擎偏差分析（Bias Analysis）
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature preview cards
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon">🤖</div>
            <div class="kpi-label">FinBERT</div>
            <div class="kpi-value neutral">—</div>
            <div class="kpi-sub">金融領域預訓練模型</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon">🔤</div>
            <div class="kpi-label">CKIP-BERT</div>
            <div class="kpi-value neutral">—</div>
            <div class="kpi-sub">繁體中文 NLP 模型</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon">🧬</div>
            <div class="kpi-label">RoBERTa</div>
            <div class="kpi-value neutral">—</div>
            <div class="kpi-sub">通用語意理解模型</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col4, col5 = st.columns(2)
    with col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon">📖</div>
            <div class="kpi-label">Jieba + NTUSD</div>
            <div class="kpi-value neutral">—</div>
            <div class="kpi-sub">字典斷詞統計方法</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon">💬</div>
            <div class="kpi-label">LLM (Groq)</div>
            <div class="kpi-value neutral">—</div>
            <div class="kpi-sub">大型語言模型深層判讀</div>
        </div>
        """, unsafe_allow_html=True)


# ================= Sidebar =================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="logo">🧠</div>
        <div class="name">FinMood</div>
        <div class="tagline">股市情緒防呆決策系統</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "導航",
        ["📈  總覽與決策儀表板", "🚦  歷史背離訊號分析", "🧠  演算法引擎觀測站"],
        label_visibility="collapsed",
    )

    st.markdown("""
    <div class="sidebar-footer">
        FinMood v1.0 · NLP × FinTech<br>
        Powered by FinBERT & Streamlit
    </div>
    """, unsafe_allow_html=True)

# ================= App Routing =================
if "總覽" in page:
    page_overview()
elif "背離" in page:
    page_signals()
elif "引擎" in page:
    page_engines()
