import streamlit as st

def apply_custom_css():
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
        padding: 12px 16px !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition-normal) !important;
        margin-bottom: 4px !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > label p,
    section[data-testid="stSidebar"] .stRadio > label div {
        font-size: 18px !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
        background: rgba(148, 163, 184, 0.08) !important;
        color: var(--text-primary) !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[aria-checked="true"] {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.1)) !important;
        color: var(--accent-green) !important;
        border-left: 4px solid var(--accent-green) !important;
        font-weight: 700 !important;
    }
    
    .sidebar-brand {
        padding: 16px 8px 32px 8px !important;
        text-align: center !important;
    }
    
    .sidebar-brand .logo {
        font-size: 64px !important;
        margin-bottom: 8px !important;
        line-height: 1.1 !important;
    }
    
    .sidebar-brand .name {
        font-size: 32px !important;
        font-weight: 900 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 4px !important;
        line-height: 1.2 !important;
    }
    
    .sidebar-brand .tagline {
        font-size: 16px !important;
        color: var(--text-muted) !important;
        font-weight: 500 !important;
    }
    
    .sidebar-brand * {
        font-size: inherit;
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
        padding: 20px 28px;
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
    
    .hero-banner.red { border-color: rgba(239, 68, 68, 0.35); box-shadow: 0 4px 40px rgba(239, 68, 68, 0.1); }
    .hero-banner.red::before { background: linear-gradient(90deg, #EF4444, #F87171, #EF4444); }
    .hero-banner.green { border-color: rgba(16, 185, 129, 0.35); box-shadow: 0 4px 40px rgba(16, 185, 129, 0.1); }
    .hero-banner.green::before { background: linear-gradient(90deg, #10B981, #34D399, #10B981); }
    .hero-banner.amber { border-color: rgba(245, 158, 11, 0.35); box-shadow: 0 4px 40px rgba(245, 158, 11, 0.08); }
    .hero-banner.amber::before { background: linear-gradient(90deg, #F59E0B, #FBBF24, #F59E0B); }
    .hero-banner.neutral { border-color: var(--border-subtle); }
    .hero-banner.neutral::before { background: linear-gradient(90deg, #64748B, #94A3B8, #64748B); }
    
    .hero-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .hero-stock {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .hero-stock-name {
        font-size: 32px;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.01em;
    }
    
    .hero-stock-id {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-muted);
        background: rgba(148, 163, 184, 0.1);
        padding: 3px 12px;
        border-radius: 20px;
    }
    
    .hero-date {
        font-size: 16px;
        color: var(--text-secondary);
        font-weight: 600;
    }
    
    .hero-content {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        gap: 48px;
    }
    
    .hero-main {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .hero-light-wrap {
        flex-shrink: 0;
    }
    
    .hero-light {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
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
        font-size: 15px;
        font-weight: 700;
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
        line-height: 1.1;
        margin-bottom: 4px;
    }
    
    .hero-banner.red .hero-label { color: #EF4444; }
    .hero-banner.green .hero-label { color: #10B981; }
    .hero-banner.amber .hero-label { color: #F59E0B; }
    .hero-banner.neutral .hero-label { color: var(--text-primary); }
    
    .hero-desc {
        font-size: 16px;
        color: var(--text-secondary);
        line-height: 1.4;
    }
    
    .hero-kpi-row {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        gap: 20px;
        padding-left: 20px;
        border-left: 1px solid rgba(148, 163, 184, 0.15);
    }
    
    .hero-kpi {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 2px;
    }
    
    .hero-kpi-divider {
        width: 2px;
        height: 36px;
        background: rgba(148, 163, 184, 0.2);
        margin: 0 4px;
    }
    
    .hero-kpi-name {
        font-size: 14px;
        color: var(--text-muted);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 2px;
    }
    
    .hero-kpi-val {
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.01em;
        line-height: 1.1;
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
        font-size: 13px;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        white-space: nowrap;
        padding-top: 1px;
    }
    
    .ai-compact-text {
        font-size: 16px;
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
        font-size: 19px;
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
    
    /* ── Streamlit Tabs Overrides ── */
    button[data-baseweb="tab"] {
        font-family: 'Inter', 'Noto Sans TC', sans-serif !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding-bottom: 12px !important;
        padding-top: 12px !important;
        color: var(--text-muted) !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--accent-cyan) !important;
        border-bottom-color: var(--accent-cyan) !important;
    }
    
    button[data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    




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
