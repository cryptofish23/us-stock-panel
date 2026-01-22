import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date

# 页面配置
st.set_page_config(page_title="24H美股全能专业看板", page_icon="📈", layout="wide")

# 极致紧凑 UI CSS (TradingView Style)
st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 1rem 1.5rem; }
    .card {
        background: #161c27; border: 1px solid #1e293b;
        border-radius: 4px; padding: 6px; margin-bottom: 2px;
    }
    .ticker-row { display: flex; justify-content: space-between; align-items: baseline; }
    .ticker { font-size: 0.95rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.75rem; color: #9ca3af; font-weight: normal; margin-left: 4px; }
    .price-main { font-size: 1rem; color: #ffffff; font-family: monospace; margin: 2px 0; }
    .change-up { color: #08d38d; font-weight: bold; font-size: 0.95rem; }
    .change-down { color: #f23645; font-weight: bold; font-size: 0.95rem; }
    .ext-box { 
        margin-top: 4px; padding-top: 4px; border-top: 1px dashed #2d3748;
        font-size: 0.75rem; color: #3b82f6; display: flex; justify-content: space-between;
    }
    .section-header {
        background: #1e222d; color: #d1d4dc; padding: 4px 10px;
        border-left: 4px solid #2962ff; font-size: 0.85rem;
        margin: 12px 0 5px 0; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- 中文映射表 ----------------
NAME_MAP = {
    # 指数
    '^DJI': '道琼斯工业指数', '^GSPC': '标准普尔指数', '^IXIC': '纳斯达克指数',
    'NQ=F': '纳斯达克指数期货', 'ES=F': '标准普尔指数期货',
    # 芯片
    'NVDA': '英伟达', 'TSM': '台积电', 'INTC': '英特尔', 'AMD': '超威半导体', 'AVGO': '博通', 'ARM': '安谋',
    # 存储/光模块
    'MU': '美光科技', 'WDC': '西部数据', 'STX': '希捷', 'LITE': 'Lumentum', 'CIEN': 'Ciena', 'AAOI': '应用光电',
    # 航空航天/无人机
    'RKLB': '火箭实验室', 'LUNR': '直觉机器', 'ASTS': 'AST SpaceMobile', 'RCAT': 'Red Cat', 'AVAV': ' AeroVironment', 'ONDS': 'Ondas',
    # 加密/云
    'MSTR': '微策投资', 'COIN': 'Coinbase', 'HOOD': '罗宾汉', 'IREN': 'Iris Energy', 'NBIS': 'Nebula', 'APLD': 'Applied Digital',
    # 能源
    'BE': 'Bloom Energy', 'EOSE': 'Eos Energy', 'FLNC': 'Fluence Energy'
}

# ---------------- 数据抓取 ----------------
def get_accurate_data(tickers):
    results = []
    group = yf.Tickers(' '.join(tickers))
    for t in tickers:
        try:
            info = group.tickers[t].info
            reg_price = info.get('regularMarketPrice', 0)
            prev_close = info.get('regularMarketPreviousClose', 1)
            day_chg = ((reg_price - prev_close) / prev_close) * 100
            
            ext_price = info.get('postMarketPrice') or info.get('preMarketPrice') or reg_price
            ext_chg = ((ext_price - reg_price) / reg_price) * 100 if reg_price > 0 else 0
            
            results.append({
                'Ticker': t, 'Price': round(reg_price, 2), 'DayChange': round(day_chg, 2),
                'ExtPrice': round(ext_price, 2), 'ExtChange': round(ext_chg, 2)
            })
        except: continue
    return pd.DataFrame(results)

# ---------------- 渲染 ----------------
st.title("PRO 隔夜美股全能面板")

# 1. 指数与期货
st.markdown("<div class='section-header'>MARKET INDICES & FUTURES (指数与期货)</div>", unsafe_allow_html=True)
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
df_idx = get_accurate_data(idx_list)

if not df_idx.empty:
    cols = st.columns(5)
    for i, row in df_idx.iterrows():
        with cols[i]:
            display_name = "S&P 500 Index" if row['Ticker'] == '^GSPC' else \
                           "NASDAQ Composite Index" if row['Ticker'] == '^IXIC' else row['Ticker']
            cls = "change-up" if row['DayChange'] > 0 else "change-down"
            st.markdown(f"""
                <div class="card">
                    <div class="ticker-row">
                        <span class="ticker">{display_name}</span>
                    </div>
                    <div style="font-size:0.7rem; color:#636b79; margin-bottom:2px;">{NAME_MAP.get(row['Ticker'])}</div>
                    <div class="price-main">${row['Price']} <span class="{cls}">{row['DayChange']:+.2f}%</span></div>
                </div>
            """, unsafe_allow_html=True)

# 2. 板块
PLATES = {
    '芯片/AI': ['NVDA', 'TSM', 'INTC', 'AMD', 'AVGO', 'ARM'],
    '存储/光模块': ['MU', 'WDC', 'STX', 'LITE', 'CIEN', 'AAOI'],
    '航天/无人机': ['RKLB', 'LUNR', 'ASTS', 'RCAT', 'AVAV', 'ONDS'],
    '加密/Neo Cloud': ['MSTR', 'COIN', 'HOOD', 'IREN', 'NBIS', 'APLD']
}

for plate, tickers in PLATES.items():
    st.markdown(f"<div class='section-header'>{plate}</div>", unsafe_allow_html=True)
    df = get_accurate_data(tickers)
    if not df.empty:
        df = df.sort_values(by='DayChange', ascending=False)
        cols = st.columns(6)
        for i, row in df.reset_index(drop=True).iterrows():
            with cols[i]:
                cls = "change-up" if row['DayChange'] > 0 else "change-down"
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker-row">
                            <span class="ticker">{row['Ticker']}</span>
                            <span class="chinese-name">({NAME_MAP.get(row['Ticker'], '')})</span>
                        </div>
                        <div class="price-main">${row['Price']} <span class="{cls}">{row['DayChange']:+.2f}%</span></div>
                        <div class="ext-box">
                            <span>夜盘: ${row['ExtPrice']}</span>
                            <span style="color:{'#08d38d' if row['ExtChange']>=0 else '#f23645'}">{row['ExtChange']:+.2f}%</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# 3. Top Gainers & 新闻
col_news, col_gain = st.columns([2, 1])
with col_news:
    st.markdown("<div class='section-header'>🔥 重要新闻回顾</div>", unsafe_allow_html=True)
    st.info("""
    - **英特尔 (INTC)**：隔夜涨幅 11.72%，夜盘继续保持 1.38% 的强势。
    - **格陵兰协议**：特朗普与北约达成协议，地缘政治风险溢价大幅收窄，小盘股指数创新高。
    - **存储板块**：美光 (MU) 与西部数据 (WDC) 持续受追捧，板块平均涨幅超过 6%。
    """)

with col_gain:
    st.markdown("<div class='section-header'>TOP GAINERS (涨幅榜)</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class="card"><span class="ticker">NAMM</span> <span class="change-up">+130.6%</span></div>
        <div class="card"><span class="ticker">PAVM</span> <span class="change-up">+94.6%</span></div>
        <div class="card"><span class="ticker">LSTA</span> <span class="change-up">+86.5%</span></div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption(f"数据更新于: {date.today()} | 价格基于 Yahoo Finance 实时接口核对")
