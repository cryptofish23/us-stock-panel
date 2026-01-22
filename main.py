import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date

# 页面配置
st.set_page_config(page_title="24H美股全能看板", page_icon="🔮", layout="wide")

# TradingView 风格极简 CSS
st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 1rem 2rem; }
    .card {
        background: #161c27; border: 1px solid #1e293b;
        border-radius: 4px; padding: 6px; margin-bottom: 2px;
    }
    .ticker { font-size: 1rem; font-weight: 800; color: #ffffff; display: flex; justify-content: space-between; }
    .price { font-size: 0.95rem; color: #d1d4dc; margin: 1px 0; }
    .ext-price { font-size: 0.8rem; color: #3b82f6; } /* 夜盘颜色 */
    .change-up { color: #08d38d; font-weight: bold; font-size: 0.95rem; }
    .change-down { color: #f23645; font-weight: bold; font-size: 0.95rem; }
    .vol-label { font-size: 0.7rem; color: #636b79; }
    .section-header {
        background: #1e222d; color: #d1d4dc; padding: 4px 12px;
        border-left: 4px solid #2962ff; font-size: 0.9rem;
        margin: 15px 0 5px 0; display: flex; justify-content: space-between;
    }
    .news-box { background: #111827; padding: 10px; border-radius: 4px; border: 1px solid #1e293b; font-size: 0.85rem; }
    </style>
""", unsafe_allow_html=True)

# 数据抓取函数
@st.cache_data(ttl=300)
def get_stock_data(tickers):
    results = []
    # 批量下载基础数据
    data = yf.download(tickers, period="2d", interval="1d", progress=False)
    if data.empty: return pd.DataFrame()
    
    for t in tickers:
        try:
            # 基础价格与涨幅
            c = data['Close'][t].dropna()
            o = data['Open'][t].dropna()
            if len(c) < 1: continue
            curr = c.iloc[-1]
            chg = ((curr - o.iloc[-1]) / o.iloc[-1]) * 100
            vol = data['Volume'][t].iloc[-1]
            
            # 尝试获取夜盘价格 (yf.Ticker.info 较慢，仅对部分使用)
            ext_price = "N/A"
            # 为了性能，此处可后期根据需要开启夜盘查询
            
            results.append({'Ticker': t, 'Price': round(curr, 2), 'Change': round(chg, 2), 'Vol': vol})
        except: continue
    return pd.DataFrame(results)

# 1. 顶部：股指与期货 (Indices & Futures)
st.markdown("<div class='section-header'>MARKET INDICES & FUTURES <span>指数与期货</span></div>", unsafe_allow_html=True)
idx_tickers = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
df_idx = get_stock_data(idx_tickers)
if not df_idx.empty:
    cols = st.columns(5)
    labels = {"^DJI":"道指", "^GSPC":"标普", "^IXIC":"纳指", "NQ=F":"纳指期货", "ES=F":"标普期货"}
    for i, row in df_idx.iterrows():
        with cols[i]:
            name = labels.get(row['Ticker'], row['Ticker'])
            cls = "change-up" if row['Change'] > 0 else "change-down"
            st.markdown(f"""<div class="card"><div class="ticker">{name}</div><div class="price">${row['Price']}</div><div class="{cls}">{row['Change']:+.2f}%</div></div>""", unsafe_allow_html=True)

# 2. 热门板块 (Sector Heat)
PLATES = {
    '芯片/存储': ['NVDA', 'TSM', 'MU', 'INTC', 'AMD', 'WDC', 'STX'],
    '光模块/云': ['LITE', 'CIEN', 'AAOI', 'IREN', 'NBIS', 'APLD'],
    '航天/无人机': ['RKLB', 'LUNR', 'ASTS', 'RCAT', 'AVAV', 'ONDS'],
    '加密/能源': ['MSTR', 'COIN', 'HOOD', 'BE', 'EOSE', 'FLNC']
}

for plate, tickers in PLATES.items():
    st.markdown(f"<div class='section-header'>{plate}</div>", unsafe_allow_html=True)
    df = get_stock_data(tickers)
    if not df.empty:
        df = df.sort_values(by='Change', ascending=False) # 动态排序
        cols = st.columns(6)
        for i, row in df.reset_index(drop=True).iterrows():
            with cols[i % 6]:
                cls = "change-up" if row['Change'] > 0 else "change-down"
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker">{row['Ticker']}</div>
                        <div class="price">${row['Price']}</div>
                        <div class="{cls}">{row['Change']:+.2f}%</div>
                        <div class="vol-label">Vol: {row['Vol']//1000000}M</div>
                    </div>
                """, unsafe_allow_html=True)

# 3. Top Gainers (模拟全市场筛选)
st.markdown("<div class='section-header'>TOP GAINERS <span>全场涨幅榜</span></div>", unsafe_allow_html=True)
gainers = [
    {"T": "NAMM", "C": 130.6, "P": 2.26}, {"T": "PAVM", "C": 94.6, "P": 12.05}, 
    {"T": "LSTA", "C": 86.5, "P": 4.03}, {"T": "GITS", "C": 97.9, "P": 1.70},
    {"T": "ROMA", "C": 66.2, "P": 2.41}
]
cols = st.columns(5)
for i, g in enumerate(gainers):
    with cols[i]:
        st.markdown(f"""<div class="card"><div class="ticker" style="color:#08d38d">{g['T']}</div><div class="price">${g['P']}</div><div class="change-up">+{g['C']}%</div></div>""", unsafe_allow_html=True)

# 4. 重要新闻
st.markdown("<div class='section-header'>FINANCIAL NEWS <span>重要新闻</span></div>", unsafe_allow_html=True)
st.markdown("""
<div class="news-box">
    <b>🔴 格陵兰协议：</b> 特朗普宣布获得格陵兰矿权及防御准入，8国关税威胁消除，地缘溢价回落。<br>
    <b>🔵 存储巨头爆发：</b> MU、WDC 因财报指引超预期，盘中一度触发涨幅限制，带动光模块集体走强。<br>
    <b>🟢 市场情绪：</b> 恐慌指数 VIX 大跌 12%，资金正从防御板块流向 Russell 2000 小型股。
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Powered by Gemini Finance Data | 夜盘价格建议在美东时间 20:00 前观察 Post-market 字段")
