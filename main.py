import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. 深度 UI 定制 (解决白边与间隙) ---
st.set_page_config(page_title="PRO 隔夜美股热力中心", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* 页面背景与基础间距 */
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 1rem 1.5rem; }
    
    /* 消除 Streamlit 默认纵向间隙 */
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* 个股卡片整体容器 */
    .stock-card {
        background: #161b26;
        border: 1px solid #2d3648;
        border-radius: 6px;
        padding: 0;
        margin: 5px 0;
        overflow: hidden;
    }
    .card-top { padding: 12px 12px 4px 12px; }
    .ticker-name { font-size: 1rem; font-weight: 800; color: #ffffff; display: flex; justify-content: space-between; }
    .chinese-name { font-size: 0.75rem; color: #9ca3af; font-weight: normal; }
    .price-main { font-size: 1.25rem; color: #ffffff; font-family: 'Courier New', monospace; margin: 4px 0; font-weight: bold; }
    .change-up { color: #08d38d; font-weight: bold; }
    .change-down { color: #f23645; font-weight: bold; }
    
    /* 趋势图 SVG 样式 */
    .spark-box { line-height: 0; margin-top: -2px; }
    
    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc; padding: 6px 12px; border-left: 4px solid #2962ff;
        font-size: 0.9rem; margin: 15px 0 8px 0; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 映射表与数据抓取 (修正三大股指) ---
NAME_MAP = {
    '^DJI': '道琼斯指数', '^GSPC': '标普500指数', '^IXIC': '纳斯达克指数', 'NQ=F': '纳指期货', 'ES=F': '标普期货',
    'NVDA': '英伟达', 'TSLA': '特斯拉', 'AAPL': '苹果', 'MSTR': '微策投资', 'AMD': '超威', 'TSM': '台积电',
    'INTC': '英特尔', 'AVGO': '博通', 'ARM': '安谋', 'MU': '美光', 'WDC': '西数', 'STX': '希捷'
}

@st.cache_data(ttl=60)
def get_realtime_data(tickers):
    results = {}
    for t in tickers:
        try:
            # 抓取 5 天数据确保包含夜盘
            ticker = yf.Ticker(t)
            df = ticker.history(period="5d", interval="1h")
            if not df.empty:
                last_p = df['Close'].iloc[-1]
                prev_p = df['Close'].iloc[-2]
                chg = ((last_p - prev_p) / prev_p) * 100
                hist = df['Close'].tail(20).tolist()
                results[t] = {'p': round(last_p, 2), 'c': round(chg, 2), 'h': hist}
        except: continue
    return results

# --- 3. 生成 0 边距趋势图 (SVG 方案) ---
def get_sparkline_svg(data, color):
    if not data or len(data) < 2: return ""
    v_min, v_max = min(data), max(data)
    v_range = v_max - v_min if v_max != v_min else 1
    points = ""
    for i, v in enumerate(data):
        x = (i / (len(data) - 1)) * 100
        y = 30 - ((v - v_min) / v_range) * 25
        points += f"{x},{y} "
    return f"""
    <div class="spark-box">
        <svg width="100%" height="40" viewBox="0 0 100 30" preserveAspectRatio="none">
            <polyline points="{points}" fill="none" stroke="{color}" stroke-width="2" vector-effect="non-scaling-stroke"/>
        </svg>
    </div>
    """

# --- 4. 界面逻辑 ---
st.title("⚡ 隔夜美股热力中心 (Pro Fix)")

# 指数板块
st.markdown("<div class='section-header'>MARKET INDICES (核心股指)</div>", unsafe_allow_html=True)
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
idx_data = get_realtime_data(idx_list)
cols = st.columns(len(idx_list))

for i, t in enumerate(idx_list):
    with cols[i]:
        if t in idx_data:
            d = idx_data[t]
            color = "#08d38d" if d['c'] >= 0 else "#f23645"
            cls = "change-up" if d['c'] >= 0 else "change-down"
            st.markdown(f"""
                <div class="stock-card">
                    <div class="card-top">
                        <div class="ticker-name"><span>{t}</span><span class="chinese-name">{NAME_MAP.get(t,'')}</span></div>
                        <div class="price-main">${d['p']} <span class="{cls}">{d['c']:+.2f}%</span></div>
                    </div>
                    {get_sparkline_svg(d['h'], color)}
                </div>
            """, unsafe_allow_html=True)

# 芯片/AI 板块
st.markdown("<div class='section-header'>CHIPS & AI (核心芯片)</div>", unsafe_allow_html=True)
chip_list = ['NVDA', 'TSM', 'AMD', 'AVGO', 'ARM', 'INTC']
chip_data = get_realtime_data(chip_list)
ccols = st.columns(6)

for j, t in enumerate(chip_list):
    with ccols[j]:
        if t in chip_data:
            cd = chip_data[t]
            c_color = "#08d38d" if cd['c'] >= 0 else "#f23645"
            c_cls = "change-up" if cd['c'] >= 0 else "change-down"
            st.markdown(f"""
                <div class="stock-card">
                    <div class="card-top">
                        <div class="ticker-name"><span>{t}</span><span class="chinese-name">{NAME_MAP.get(t,'')}</span></div>
                        <div class="price-main">${cd['p']} <span style="font-size:0.8rem" class="{c_cls}">{cd['c']:+.2f}%</span></div>
                    </div>
                    {get_sparkline_svg(cd['h'], c_color)}
                </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption(f"最后刷新: {datetime.now().strftime('%H:%M:%S')} | 数据源: Yahoo Finance")
