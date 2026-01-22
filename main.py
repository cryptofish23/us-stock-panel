import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date

# 页面配置
st.set_page_config(page_title="PRO 隔夜美股全能面板", page_icon="📈", layout="wide")

# 极致紧凑 UI CSS
st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 1rem 1.5rem; }
    .card {
        background: #161c27; border: 1px solid #1e293b;
        border-radius: 4px; padding: 8px; margin-bottom: 4px;
    }
    .ticker-name { font-size: 1rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.8rem; color: #9ca3af; font-weight: normal; }
    .price-main { font-size: 1.1rem; color: #ffffff; font-family: monospace; margin: 4px 0; }
    .change-up { color: #08d38d; font-weight: bold; font-size: 1rem; }
    .change-down { color: #f23645; font-weight: bold; font-size: 1rem; }
    .section-header {
        background: #1e222d; color: #d1d4dc; padding: 6px 12px;
        border-left: 4px solid #2962ff; font-size: 0.95rem;
        margin: 18px 0 8px 0; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- 中文映射表 ----------------
NAME_MAP = {
    '^DJI': '道琼斯工业指数', '^GSPC': '标准普尔指数', '^IXIC': '纳斯达克指数',
    'NQ=F': '纳斯达克指数期货', 'ES=F': '标准普尔指数期货',
    'NVDA': '英伟达', 'TSM': '台积电', 'INTC': '英特尔', 'AMD': '超威半导体', 'AVGO': '博通', 'ARM': '安谋',
    'MU': '美光科技', 'WDC': '西部数据', 'STX': '希捷', 'LITE': 'Lumentum', 'CIEN': 'Ciena', 'AAOI': '应用光电',
    'RKLB': '火箭实验室', 'LUNR': '直觉机器', 'ASTS': 'AST SpaceMobile', 'RCAT': 'Red Cat', 'AVAV': '无人机环境', 'ONDS': 'Ondas',
    'MSTR': '微策投资', 'COIN': 'Coinbase', 'HOOD': '罗宾汉', 'IREN': 'Iris Energy', 'NBIS': 'Nebula', 'APLD': 'Applied Digital'
}

# ---------------- 数据获取 ----------------
@st.cache_data(ttl=300)
def get_data(tickers):
    # 使用 download 获取更稳定的基础数据
    data = yf.download(tickers, period="2d", interval="1d", progress=False)
    if data.empty: return pd.DataFrame()
    
    results = []
    for t in tickers:
        try:
            close = data['Close'][t].dropna()
            open_p = data['Open'][t].dropna()
            if len(close) < 1: continue
            
            p = close.iloc[-1]
            o = open_p.iloc[-1]
            chg = ((p - o) / o) * 100
            results.append({'Ticker': t, 'Price': round(p, 2), 'Change': round(chg, 2)})
        except: continue
    return pd.DataFrame(results)

# ---------------- 页面渲染 ----------------
st.title("PRO 隔夜美股全能面板")

# 1. 指数与期货
st.markdown("<div class='section-header'>MARKET INDICES & FUTURES (指数与期货)</div>", unsafe_allow_html=True)
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
df_idx = get_data(idx_list)

if not df_idx.empty:
    cols = st.columns(5)
    for i, t in enumerate(idx_list):
        row = df_idx[df_idx['Ticker'] == t]
        if not row.empty:
            row = row.iloc[0]
            display_symbol = "S&P 500 Index" if t == '^GSPC' else "NASDAQ Composite Index" if t == '^IXIC' else t
            cls = "change-up" if row['Change'] > 0 else "change-down"
            with cols[i]:
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker-name">{display_symbol}</div>
                        <div class="chinese-name">{NAME_MAP.get(t, '')}</div>
                        <div class="price-main">${row['Price']} <span class="{cls}">{row['Change']:+.2f}%</span></div>
                    </div>
                """, unsafe_allow_html=True)

# 2. 核心板块
PLATES = {
    '芯片/AI': ['NVDA', 'TSM', 'INTC', 'AMD', 'AVGO', 'ARM'],
    '存储/光模块': ['MU', 'WDC', 'STX', 'LITE', 'CIEN', 'AAOI'],
    '航天/无人机': ['RKLB', 'LUNR', 'ASTS', 'RCAT', 'AVAV', 'ONDS'],
    '加密/Neo Cloud': ['MSTR', 'COIN', 'HOOD', 'IREN', 'NBIS', 'APLD']
}

for plate, tickers in PLATES.items():
    st.markdown(f"<div class='section-header'>{plate}</div>", unsafe_allow_html=True)
    df = get_data(tickers)
    if not df.empty:
        df = df.sort_values(by='Change', ascending=False)
        cols = st.columns(6)
        for i, row in df.reset_index(drop=True).iterrows():
            with cols[i % 6]:
                cls = "change-up" if row['Change'] > 0 else "change-down"
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker-name">{row['Ticker']} <span class="chinese-name">({NAME_MAP.get(row['Ticker'], '')})</span></div>
                        <div class="price-main">${row['Price']} <span class="{cls}">{row['Change']:+.2f}%</span></div>
                    </div>
                """, unsafe_allow_html=True)

# 3. 底部：Top Gainers 与 新闻
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("<div class='section-header'>🔥 重要新闻回顾</div>", unsafe_allow_html=True)
    st.info("""
    - **英特尔 (INTC)**：隔夜涨幅 11.72%，受到财报与市场份额利好提振。
    - **格陵兰协议**：特朗普与北约协议降低了市场避险情绪，小盘股显著回升。
    - **存储板块**：美光 (MU) 与 西部数据 (WDC) 持续受 AI 需求驱动。
    """)

with col2:
    st.markdown("<div class='section-header'>TOP GAINERS (隔夜涨幅榜)</div>", unsafe_allow_html=True)
    gainers = [("NAMM", 130.6), ("PAVM", 94.6), ("LSTA", 86.5), ("GITS", 97.9)]
    for t, c in gainers:
        st.markdown(f"""<div class="card" style="padding:4px 8px;"><b style="color:#ffffff;">{t}</b> <b class="change-up" style="float:right;">+{c}%</b></div>""", unsafe_allow_html=True)

st.markdown("---")
st.caption(f"数据更新于: {date.today()} | 模式：稳定兼容模式")
