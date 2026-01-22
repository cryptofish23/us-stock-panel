import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date

# 页面配置
st.set_page_config(page_title="PRO 隔夜美股全能面板", page_icon="📈", layout="wide")

# UI 设计优化：更美观的新闻组件和卡片
st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 1rem 1.5rem; }
    
    /* 核心卡片设计 */
    .card {
        background: linear-gradient(145deg, #1e2533, #131924);
        border: 1px solid #2d3648;
        border-radius: 6px;
        padding: 8px;
        margin-bottom: 4px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .ticker-name { font-size: 0.95rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.75rem; color: #9ca3af; font-weight: normal; }
    .price-main { font-size: 1.1rem; color: #ffffff; font-family: 'Courier New', monospace; margin: 4px 0; }
    .change-up { color: #08d38d; font-weight: bold; }
    .change-down { color: #f23645; font-weight: bold; }
    
    /* 新闻组件设计 */
    .news-container {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 12px;
        margin: 10px 0 20px 0;
    }
    .news-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 6px;
        font-size: 0.88rem;
        color: #e2e8f0;
    }
    .news-tag {
        background: #3b82f6;
        color: white;
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 0.7rem;
        margin-right: 8px;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* 板块标题设计 */
    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc;
        padding: 6px 12px;
        border-left: 4px solid #2962ff;
        font-size: 0.95rem;
        margin: 18px 0 8px 0;
        font-weight: bold;
    }
    .ext-box { 
        margin-top: 4px; padding-top: 4px; border-top: 1px dashed #2d3748;
        font-size: 0.75rem; color: #60a5fa; display: flex; justify-content: space-between;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- 数据与名称映射 ----------------
NAME_MAP = {
    '^DJI': '道琼斯工业指数', '^GSPC': '标准普尔指数', '^IXIC': '纳斯达克指数',
    'NQ=F': '纳斯达克期货', 'ES=F': '标普500期货',
    'NVDA': '英伟达', 'TSM': '台积电', 'INTC': '英特尔', 'AMD': '超威半导体', 'AVGO': '博通', 'ARM': '安谋',
    'MU': '美光科技', 'WDC': '西部数据', 'STX': '希捷', 'LITE': 'Lumentum', 'CIEN': 'Ciena', 'AAOI': '应用光电',
    'RKLB': '火箭实验室', 'LUNR': '直觉机器', 'ASTS': 'AST SpaceMobile', 'RCAT': 'Red Cat', 'AVAV': '环境', 'ONDS': 'Ondas',
    'MSTR': '微策投资', 'COIN': 'Coinbase', 'HOOD': '罗宾汉', 'IREN': 'Iris Energy', 'NBIS': 'Nebula', 'APLD': 'Applied Digital'
}

@st.cache_data(ttl=120)
def get_market_data(tickers):
    data = yf.download(tickers, period="1d", interval="1m", prepost=True, progress=False)
    if data.empty: return pd.DataFrame()
    results = []
    for t in tickers:
        try:
            ticker_data = data.xs(t, axis=1, level=1) if len(tickers) > 1 else data
            ticker_data = ticker_data.dropna()
            if ticker_data.empty: continue
            curr_p = ticker_data['Close'].iloc[-1]
            reg_close = ticker_data['Close'].iloc[0]
            chg = ((curr_p - reg_close) / reg_close) * 100
            results.append({'Ticker': t, 'Price': round(curr_p, 2), 'Change': round(chg, 2)})
        except: continue
    return pd.DataFrame(results)

# ---------------- 页面逻辑 ----------------
st.title("⚡ 隔夜美股热力中心")

# 1. 指数板块
st.markdown("<div class='section-header'>MARKET INDICES (核心股指)</div>", unsafe_allow_html=True)
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
df_idx = get_market_data(idx_list)
if not df_idx.empty:
    cols = st.columns(5)
    for i, t in enumerate(idx_list):
        row = df_idx[df_idx['Ticker'] == t]
        if not row.empty:
            row = row.iloc[0]
            display_symbol = "S&P 500" if t == '^GSPC' else "NASDAQ" if t == '^IXIC' else t
            cls = "change-up" if row['Change'] > 0 else "change-down"
            with cols[i]:
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker-name">{display_symbol}</div>
                        <div class="chinese-name">{NAME_MAP.get(t, '')}</div>
                        <div class="price-main">${row['Price']} <span class="{cls}">{row['Change']:+.2f}%</span></div>
                    </div>
                """, unsafe_allow_html=True)

# 2. 重要新闻 (放置在指数下方，设计美化)
st.markdown("""
<div class="news-container">
    <div class="news-item">
        <span class="news-tag" style="background:#ef4444;">Breaking</span>
        <span><b>英特尔 (INTC)</b> 隔夜暴涨 11.72%，夜盘维持强势。财报指引超预期引发半导体板块集体抢筹。</span>
    </div>
    <div class="news-item">
        <span class="news-tag" style="background:#10b981;">Macro</span>
        <span><b>格陵兰协议框架</b> 达成后关税隐忧消退。资金加速流向 <b>RKLB</b> 及 <b>LUNR</b> 等商业航天标的。</span>
    </div>
    <div class="news-item">
        <span class="news-tag">Sector</span>
        <span>存储板块（<b>MU, WDC</b>）出现空头挤压。光模块厂商 <b>AAOI</b> 夜盘跟随主板异动。</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 3. 核心个股板块
PLATES = {
    '芯片/AI': ['NVDA', 'TSM', 'INTC', 'AMD', 'AVGO', 'ARM'],
    '存储/光模块': ['MU', 'WDC', 'STX', 'LITE', 'CIEN', 'AAOI'],
    '航天/无人机': ['RKLB', 'LUNR', 'ASTS', 'RCAT', 'AVAV', 'ONDS'],
    '加密/Neo Cloud': ['MSTR', 'COIN', 'HOOD', 'IREN', 'NBIS', 'APLD']
}

for plate, tickers in PLATES.items():
    st.markdown(f"<div class='section-header'>{plate}</div>", unsafe_allow_html=True)
    df = get_market_data(tickers)
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
                        <div class="ext-box"><span>夜盘实时: ${row['Price']}</span></div>
                    </div>
                """, unsafe_allow_html=True)

# 4. 底部 Top Gainers
st.markdown("<div class='section-header'>TOP GAINERS (全场涨幅榜)</div>", unsafe_allow_html=True)
g_cols = st.columns(4)
gainers = [("NAMM", 130.61), ("GITS", 97.97), ("PAVM", 94.67), ("LSTA", 86.57)]
for i, (t, c) in enumerate(gainers):
    with g_cols[i]:
        st.markdown(f"""
            <div class="card" style="border: 1px solid #10b981;">
                <span class="ticker-name">{t}</span>
                <span class="change-up" style="float:right;">+{c}%</span>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption(f"Update: {date.today()} | 实时模式已激活")
