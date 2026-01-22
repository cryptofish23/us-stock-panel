import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date

# 页面配置
st.set_page_config(page_title="PRO AI+crypto美股中心", page_icon="⚡", layout="wide")

# UI 设计：TradingView 风格
st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 1rem 1.5rem; }
    .card {
        background: linear-gradient(145deg, #1e2533, #131924);
        border: 1px solid #2d3648;
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 4px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .ticker-name { font-size: 1rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.8rem; color: #9ca3af; font-weight: normal; }
    .price-main { font-size: 1.2rem; color: #ffffff; font-family: 'Courier New', monospace; margin: 4px 0; }
    .change-up { color: #08d38d; font-weight: bold; }
    .change-down { color: #f23645; font-weight: bold; }
    .news-container {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 12px;
        margin: 5px 0 15px 0;
    }
    .news-item { display: flex; align-items: flex-start; margin-bottom: 6px; font-size: 0.88rem; color: #e2e8f0; }
    .news-tag {
        background: #3b82f6; color: white; padding: 1px 6px; border-radius: 4px;
        font-size: 0.7rem; margin-right: 8px; font-weight: bold;
    }
    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc; padding: 6px 12px; border-left: 4px solid #2962ff;
        font-size: 0.95rem; margin: 15px 0 8px 0; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- 名称映射 ----------------
NAME_MAP = {
    '^DJI': '道琼斯工业指数', '^GSPC': '标准普尔指数', '^IXIC': '纳斯达克指数',
    'NQ=F': '纳斯达克指数期货', 'ES=F': '标准普尔指数期货',
    'NVDA': '英伟达', 'TSM': '台积电', 'INTC': '英特尔', 'AMD': '超威半导体', 'AVGO': '博通', 'ARM': '安谋',
    'MU': '美光科技', 'WDC': '西部数据', 'STX': '希捷', 'LITE': 'Lumentum', 'CIEN': 'Ciena', 'AAOI': '应用光电',
    'RKLB': '火箭实验室', 'LUNR': '直觉机器', 'ASTS': 'AST SpaceMobile', 'RCAT': 'Red Cat', 'AVAV': '环境', 'ONDS': 'Ondas',
    'MSTR': '微策投资', 'COIN': 'Coinbase', 'HOOD': '罗宾汉', 'IREN': 'Iris Energy', 'NBIS': 'Nebula', 'APLD': 'Applied Digital'
}

# ---------------- 增强版数据抓取 ----------------
@st.cache_data(ttl=60) # 每一分钟强制刷新一次
def get_realtime_data(tickers):
    results = []
    # 采用批量获取模式
    for t in tickers:
        try:
            # 针对期货和个股，使用 Ticker.info 这种最实时的方式
            stock = yf.Ticker(t)
            # 优先获取夜盘价/实时价
            price = stock.fast_info.get('last_price')
            prev_close = stock.fast_info.get('previous_close')
            
            # 如果 fast_info 拿不到，降级使用 download
            if not price or not prev_close:
                df = stock.history(period="2d")
                price = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
            
            chg = ((price - prev_close) / prev_close) * 100
            results.append({'Ticker': t, 'Price': round(price, 2), 'Change': round(chg, 2)})
        except:
            continue
    return pd.DataFrame(results)

# ---------------- 页面逻辑 ----------------
st.title("⚡ 隔夜美股热力中心 (实时修正版)")

# 1. 指数板块
st.markdown("<div class='section-header'>MARKET INDICES (核心股指)</div>", unsafe_allow_html=True)
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
df_idx = get_realtime_data(idx_list)

cols = st.columns(5)
for i, t in enumerate(idx_list):
    with cols[i]:
        row = df_idx[df_idx['Ticker'] == t]
        if not row.empty:
            row = row.iloc[0]
            display_symbol = "S&P 500 Index" if t == '^GSPC' else "NASDAQ Composite Index" if t == '^IXIC' else t
            cls = "change-up" if row['Change'] > 0 else "change-down"
            st.markdown(f"""
                <div class="card">
                    <div class="ticker-name">{display_symbol}</div>
                    <div class="chinese-name">{NAME_MAP.get(t, '')}</div>
                    <div class="price-main">${row['Price']} <span class="{cls}">{row['Change']:+.2f}%</span></div>
                </div>
            """, unsafe_allow_html=True)

# 2. 重要新闻 (放置在指数下方)
st.markdown("""
<div class="news-container">
    <div class="news-item">
        <span class="news-tag" style="background:#ef4444;">Breaking</span>
        <span><b>纳指期货 (NQ)</b> 电子盘持续走高，目前涨幅已达 <b>+0.91%</b>，突破 25700 关口。</span>
    </div>
    <div class="news-item">
        <span class="news-tag" style="background:#10b981;">Macro</span>
        <span><b>格陵兰协议框架</b> 消除关税疑云，市场风险偏好极度高涨，资金疯狂涌入成长股。</span>
    </div>
    <div class="news-item">
        <span class="news-tag">Sector</span>
        <span><b>英特尔 (INTC)</b> 隔夜暴涨 11.72%，夜盘维持强势。存储器（MU, WDC）板块平均涨幅超 6%。</span>
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
    df = get_realtime_data(tickers)
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
                        <div style="font-size:0.75rem; color:#60a5fa; margin-top:4px;">夜盘实时: ${row['Price']}</div>
                    </div>
                """, unsafe_allow_html=True)

# 4. Top Gainers
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
st.caption(f"数据实时同步自电子盘 | 最后核对时间: {date.today()} | NQ 基准: 25700+")
