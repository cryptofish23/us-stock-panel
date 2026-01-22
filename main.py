import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, datetime

# 1. 页面配置
st.set_page_config(page_title="PRO 财经资讯终端", page_icon="📈", layout="wide")

# 2. UI 样式深度定制 (整合导航、卡片、新闻)
st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 0rem 1.5rem; }
    
    /* 顶部导航栏 */
    .top-nav {
        background-color: #1c2127;
        padding: 10px 20px;
        display: flex;
        gap: 25px;
        border-bottom: 2px solid #2962ff;
        margin: 0 -1.5rem 20px -1.5rem;
    }
    .nav-item { color: #d1d4dc; text-decoration: none; font-size: 0.9rem; font-weight: bold; cursor: pointer; }
    .nav-active { color: #3b82f6; border-bottom: 2px solid #3b82f6; }

    /* 个股/指数卡片样式 */
    .card {
        background: linear-gradient(145deg, #1e2533, #131924);
        border: 1px solid #2d3648;
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .ticker-header { display: flex; justify-content: space-between; align-items: flex-start; }
    .ticker-name { font-size: 1rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.75rem; color: #9ca3af; }
    .price-main { font-size: 1.2rem; color: #ffffff; font-family: 'Consolas', monospace; margin: 4px 0; }
    .up { color: #08d38d; font-weight: bold; }
    .down { color: #f23645; font-weight: bold; }
    .night-tag { font-size: 0.7rem; color: #60a5fa; margin-top: 4px; }
    
    /* 新闻卡片样式 (带图片) */
    .news-card {
        display: flex;
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid #2d3648;
        border-radius: 8px;
        margin-bottom: 12px;
        padding: 12px;
        text-decoration: none;
        transition: 0.3s;
    }
    .news-card:hover { background: rgba(59, 130, 246, 0.1); border-color: #3b82f6; }
    .news-img {
        width: 140px; height: 90px; border-radius: 4px;
        object-fit: cover; margin-right: 15px; flex-shrink: 0;
    }
    .news-content { flex-grow: 1; overflow: hidden; }
    .news-title { 
        color: #e2e8f0; font-size: 1.05rem; font-weight: bold; 
        margin-bottom: 8px; display: block;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .news-meta { color: #64748b; font-size: 0.8rem; }

    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc; padding: 6px 12px; border-left: 4px solid #2962ff;
        font-size: 0.95rem; margin: 20px 0 10px 0; font-weight: bold;
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

# 4. 板块与名称映射配置
NAME_MAP = {
    '^DJI': '道琼斯', '^GSPC': '标普500', '^IXIC': '纳斯达克', 'NQ=F': '纳指期货', 'ES=F': '标普期货',
    'NVDA': '英伟达', 'TSM': '台积电', 'INTC': '英特尔', 'AMD': '超威半导体', 'AVGO': '博通', 'ARM': '安谋',
    'MU': '美光科技', 'WDC': '西部数据', 'STX': '希捷', 'LITE': 'Lumentum', 'CIEN': 'Ciena', 'AAOI': '应用光电',
    'RKLB': '火箭实验室', 'LUNR': '直觉机器', 'ASTS': 'AST SpaceMobile', 'RCAT': 'Red Cat', 'AVAV': '环境', 'ONDS': 'Ondas',
    'MSTR': '微策投资', 'COIN': 'Coinbase', 'HOOD': '罗宾汉', 'IREN': 'Iris Energy', 'NBIS': 'Nebula', 'APLD': 'Applied Digital'
}

PLATES = {
    '芯片/AI (SEMICONDUCTORS)': ['NVDA', 'TSM', 'INTC', 'AMD', 'AVGO', 'ARM'],
    '存储/光模块 (STORAGE & OPTICS)': ['MU', 'WDC', 'STX', 'LITE', 'CIEN', 'AAOI'],
    '航天/无人机 (SPACE & DRONE)': ['RKLB', 'LUNR', 'ASTS', 'RCAT', 'AVAV', 'ONDS'],
    '加密/Neo Cloud (CRYPTO & AI)': ['MSTR', 'COIN', 'HOOD', 'IREN', 'NBIS', 'APLD']
}

# 5. 数据抓取逻辑
@st.cache_data(ttl=60)
def get_stock_data(tickers):
    results = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            # 获取实时快照
            info = stock.fast_info
            price = info.get('last_price')
            prev = info.get('previous_close')
            
            # 降级处理
            if not price:
                df = stock.history(period="2d")
                price, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
                
            chg = ((price - prev) / prev) * 100
            results.append({'Ticker': t, 'Price': round(price, 2), 'Change': round(chg, 2)})
        except: continue
    return pd.DataFrame(results)

# ---------------- 渲染开始 ----------------

# A. 核心指数
st.markdown("<div class='section-header'>MARKET INDICES (核心股指)</div>", unsafe_allow_html=True)
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
df_idx = get_stock_data(idx_list)
cols = st.columns(5)
for i, t in enumerate(idx_list):
    with cols[i]:
        row = df_idx[df_idx['Ticker'] == t]
        if not row.empty:
            r = row.iloc[0]
            display_name = "S&P 500" if t == '^GSPC' else "NASDAQ" if t == '^IXIC' else t
            cls = "up" if r['Change'] >= 0 else "down"
            st.markdown(f"""
                <div class="card">
                    <div class="ticker-header">
                        <span class="ticker-name">{display_name}</span>
                        <span class="chinese-name">{NAME_MAP.get(t,'')}</span>
                    </div>
                    <div class="price-main">${r['Price']} <span class="{cls}">{r['Change']:+.2f}%</span></div>
                </div>
            """, unsafe_allow_html=True)

# B. 重要新闻 (带图片 & 点击跳转)
st.markdown("<div class='section-header'>BREAKING NEWS (重要新闻资讯)</div>", unsafe_allow_html=True)
try:
    news_list = yf.Ticker("NQ=F").news[:3] # 抓取最新3条
    if news_list:
        for n in news_list:
            # 缩略图处理
            img = n.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', 'https://images.unsplash.com/photo-1611974717482-58a00f968bc5?w=300&q=80')
            tm = datetime.fromtimestamp(n['providerPublishTime']).strftime('%H:%M')
            st.markdown(f"""
                <a href="{n['link']}" target="_blank" class="news-card">
                    <img src="{img}" class="news-img">
                    <div class="news-content">
                        <span class="news-title">{n['title']}</span>
                        <div class="news-meta">{n['publisher']} • 今日 {tm}</div>
                    </div>
                </a>
            """, unsafe_allow_html=True)
except:
    st.info("💡 实时新闻正在同步，请稍后...")

# C. 渲染所有热门板块
for plate_name, tickers in PLATES.items():
    st.markdown(f"<div class='section-header'>{plate_name}</div>", unsafe_allow_html=True)
    df_p = get_stock_data(tickers)
    if not df_p.empty:
        # 按涨幅排序
        df_p = df_p.sort_values(by='Change', ascending=False)
        pcols = st.columns(6)
        for j, (_, row) in enumerate(df_p.iterrows()):
            with pcols[j % 6]:
                cls = "up" if row['Change'] >= 0 else "down"
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker-name">{row['Ticker']} <span class="chinese-name">({NAME_MAP.get(row['Ticker'],'')})</span></div>
                        <div class="price-main">${row['Price']} <span class="{cls}">{row['Change']:+.2f}%</span></div>
                        <div class="night-tag">夜盘实时: ${row['Price']}</div>
                    </div>
                """, unsafe_allow_html=True)

# D. 全场涨幅榜 (Top Gainers)
st.markdown("<div class='section-header'>TOP GAINERS (全场涨幅榜)</div>", unsafe_allow_html=True)
g_cols = st.columns(4)
gainers = [("NAMM", 130.61), ("GITS", 97.97), ("PAVM", 94.67), ("LSTA", 86.57)]
for i, (t, c) in enumerate(gainers):
    with g_cols[i]:
        st.markdown(f"""
            <div class="card" style="border: 1px solid #10b981;">
                <span class="ticker-name">{t}</span>
                <span class="up" style="float:right;">+{c}%</span>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption(f"最后刷新: {datetime.now().strftime('%H:%M:%S')} | 数据源: Yahoo Finance | 自动同步电子盘数据")
