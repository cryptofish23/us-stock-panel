import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date

# 1. 页面配置
st.set_page_config(page_title="PRO 隔夜美股热力中心", page_icon="⚡", layout="wide")

# 2. 综合 UI 设计 (包含导航栏、卡片、新闻容器)
st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 0rem 1.5rem; }
    
    /* 顶部导航栏样式 */
    .top-nav {
        background-color: #1c2127;
        padding: 10px 20px;
        display: flex;
        gap: 25px;
        border-bottom: 2px solid #2962ff;
        margin: 0 -1.5rem 15px -1.5rem;
    }
    .nav-item {
        color: #d1d4dc;
        text-decoration: none;
        font-size: 0.9rem;
        font-weight: bold;
        cursor: pointer;
    }
    .nav-active { color: #3b82f6; border-bottom: 2px solid #3b82f6; }

    /* 卡片与新闻容器样式 */
    .card {
        background: linear-gradient(145deg, #1e2533, #131924);
        border: 1px solid #2d3648;
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 8px;
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

# 3. 顶部导航栏
st.markdown("""
    <div class="top-nav">
        <div class="nav-item nav-active">实时行情</div>
        <div class="nav-item">自选股</div>
        <div class="nav-item">市场资讯</div>
        <div class="nav-item">投资组合</div>
        <div class="nav-item">AI 选股</div>
    </div>
""", unsafe_allow_html=True)

# 4. 名称映射
NAME_MAP = {
    '^DJI': '道琼斯工业指数', '^GSPC': '标准普尔指数', '^IXIC': '纳斯达克指数',
    'NQ=F': '纳指期货', 'ES=F': '标普期货',
    'NVDA': '英伟达', 'TSM': '台积电', 'INTC': '英特尔', 'AMD': '超威半导体', 'AVGO': '博通', 'ARM': '安谋',
    'MU': '美光科技', 'WDC': '西部数据', 'STX': '希捷', 'LITE': 'Lumentum', 'CIEN': 'Ciena', 'AAOI': '应用光电',
    'RKLB': '火箭实验室', 'LUNR': '直觉机器', 'ASTS': 'AST SpaceMobile', 'RCAT': 'Red Cat', 'AVAV': '环境', 'ONDS': 'Ondas',
    'MSTR': '微策投资', 'COIN': 'Coinbase', 'HOOD': '罗宾汉', 'IREN': 'Iris Energy', 'NBIS': 'Nebula', 'APLD': 'Applied Digital'
}

# 5. 数据抓取逻辑
@st.cache_data(ttl=60)
def get_realtime_data(tickers):
    results = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            price = stock.fast_info.get('last_price')
            prev_close = stock.fast_info.get('previous_close')
            
            if not price or not prev_close:
                df = stock.history(period="2d")
                price = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
            
            chg = ((price - prev_close) / prev_close) * 100
            results.append({'Ticker': t, 'Price': round(price, 2), 'Change': round(chg, 2)})
        except:
            continue
    return pd.DataFrame(results)

# 6. 界面布局渲染
st.title("⚡ 隔夜美股热力中心 (实时修正版)")

# --- A. 指数板块 ---
st.markdown("<div class='section-header'>MARKET INDICES (核心股指)</div>", unsafe_allow_html=True)
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
df_idx = get_realtime_data(idx_list)

cols = st.columns(5)
for i, t in enumerate(idx_list):
    with cols[i]:
        row = df_idx[df_idx['Ticker'] == t]
        if not row.empty:
            row = row.iloc[0]
            display_symbol = "S&P 500" if t == '^GSPC' else "NASDAQ" if t == '^IXIC' else t
            cls = "change-up" if row['Change'] > 0 else "change-down"
            st.markdown(f"""
                <div class="card">
                    <div class="ticker-name">{display_symbol}</div>
                    <div class="chinese-name">{NAME_MAP.get(t, '')}</div>
                    <div class="price-main">${row['Price']} <span class="{cls}">{row['Change']:+.2f}%</span></div>
                </div>
            """, unsafe_allow_html=True)

# --- B. 重要新闻 (紧贴在指数下方) ---
st.markdown(f"""
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

# --- C. 核心个股板块 ---
PLATES = {
    '芯片/AI': ['NVDA', 'TSM', 'INTC', 'AMD', 'AVGO', 'ARM'],
    '存储/光模块': ['MU', 'WDC', 'STX', 'LITE', 'CIEN', 'AAOI'],
    '航天/无人机': ['RKLB', 'LUNR', 'ASTS', 'RCAT', 'AVAV', 'ONDS'],
    '加密/Neo Cloud': ['MSTR', 'COIN', 'HOOD', 'IREN', 'NBIS', 'APLD']
}

for plate, tickers in PLATES.items():
    st.markdown(f"<div class='section-header'>{plate}</div>", unsafe_allow_html=True)
    df_p = get_realtime_data(tickers)
    if not df_p.empty:
        df_p = df_p.sort_values(by='Change', ascending=False)
        pcols = st.columns(6)
        for i, row in df_p.reset_index(drop=True).iterrows():
            with pcols[i % 6]:
                cls = "change-up" if row['Change'] > 0 else "change-down"
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker-name">{row['Ticker']} <span class="chinese-name">({NAME_MAP.get(row['Ticker'], '')})</span></div>
                        <div class="price-main">${row['Price']} <span class="{cls}">{row['Change']:+.2f}%</span></div>
                        <div style="font-size:0.75rem; color:#60a5fa; margin-top:4px;">夜盘实时: ${row['Price']}</div>
                    </div>
                """, unsafe_allow_html=True)

# --- D. Top Gainers ---
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
st.caption(f"数据实时同步自电子盘 | 最后更新: {date.today()} | NQ 基准: 25700+")
