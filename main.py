import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, datetime

# 1. 页面配置
st.set_page_config(page_title="PRO 财经资讯终端", page_icon="📈", layout="wide")

# 2. UI 样式深度定制
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
    .nav-item { color: #d1d4dc; text-decoration: none; font-size: 0.9rem; font-weight: bold; }
    .nav-active { color: #3b82f6; border-bottom: 2px solid #3b82f6; }

    /* 指数卡片 */
    .card {
        background: linear-gradient(145deg, #1e2533, #131924);
        border: 1px solid #2d3648;
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 8px;
    }
    .ticker-name { font-size: 1rem; font-weight: 800; color: #ffffff; }
    .price-main { font-size: 1.2rem; color: #ffffff; font-family: 'Courier New', monospace; }
    .up { color: #08d38d; font-weight: bold; }
    .down { color: #f23645; font-weight: bold; }
    
    /* 新闻卡片（带图片） */
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
        width: 120px;
        height: 80px;
        border-radius: 4px;
        object-fit: cover;
        margin-right: 15px;
    }
    .news-content { flex: 1; }
    .news-title { color: #e2e8f0; font-size: 1rem; font-weight: bold; margin-bottom: 5px; display: block; }
    .news-meta { color: #64748b; font-size: 0.75rem; }

    .section-header {
        color: #d1d4dc; padding: 6px 0; border-bottom: 1px solid #2d3648;
        font-size: 1rem; margin: 10px 0 15px 0; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 顶部导航栏渲染
st.markdown("""
    <div class="top-nav">
        <div class="nav-item nav-active">实时行情</div>
        <div class="nav-item">自选股</div>
        <div class="nav-item">市场资讯</div>
        <div class="nav-item">投资组合</div>
        <div class="nav-item">AI 选股</div>
    </div>
""", unsafe_allow_html=True)

# 4. 数据抓取
@st.cache_data(ttl=60)
def get_market_data(tickers):
    results = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            price = stock.fast_info.get('last_price')
            prev = stock.fast_info.get('previous_close')
            if not price:
                df = stock.history(period="2d")
                price, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
            chg = ((price - prev) / prev) * 100
            results.append({'t': t, 'p': round(price, 2), 'c': round(chg, 2)})
        except: continue
    return pd.DataFrame(results)

# --- 核心布局开始 ---

# A. 指数模块
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
df_idx = get_market_data(idx_list)
cols = st.columns(5)
for i, t in enumerate(idx_list):
    with cols[i]:
        row = df_idx[df_idx['t'] == t]
        if not row.empty:
            r = row.iloc[0]
            cls = "up" if r['c'] >= 0 else "down"
            st.markdown(f"""
                <div class="card">
                    <div class="ticker-name">{t}</div>
                    <div class="price-main">${r['p']} <span class="{cls}">{r['c']:+.2f}%</span></div>
                </div>
            """, unsafe_allow_html=True)

# B. 重要新闻模块 (带图片并链接)
st.markdown("<div class='section-header'>BREAKING NEWS (重要新闻资讯)</div>", unsafe_allow_html=True)

try:
    # 获取纳指期货相关新闻，通常带有图片链接
    news_items = yf.Ticker("NQ=F").news[:4]
    if news_items:
        for n in news_items:
            # 尝试获取缩略图，如果没有则使用默认财经图片
            img_url = n.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', 'https://images.unsplash.com/photo-1611974717482-58a00f968bc5?w=200&q=80')
            pub_time = datetime.fromtimestamp(n['providerPublishTime']).strftime('%Y-%m-%d %H:%M')
            
            st.markdown(f"""
                <a href="{n['link']}" target="_blank" class="news-card">
                    <img src="{img_url}" class="news-img">
                    <div class="news-content">
                        <span class="news-title">{n['title']}</span>
                        <div class="news-meta">{n['publisher']} • {pub_time}</div>
                    </div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.info("正在更新新闻流...")
except:
    st.warning("资讯接口连接中，请稍后刷新...")

# C. 行业板块
st.markdown("<div class='section-header'>SECTORS (热门板块)</div>", unsafe_allow_html=True)
stocks = ['NVDA', 'TSM', 'AMD', 'MSTR', 'COIN', 'RKLB']
df_s = get_market_data(stocks)
scols = st.columns(6)
for i, t in enumerate(stocks):
    with scols[i]:
        row = df_s[df_s['t'] == t]
        if not row.empty:
            r = row.iloc[0]
            st.markdown(f"""
                <div class="card">
                    <div class="ticker-name" style="font-size:0.8rem;">{t}</div>
                    <div class="price-main" style="font-size:1rem;">${r['p']} <span class="{"up" if r['c']>=0 else "down"}">{r['c']:+.2f}%</span></div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption(f"最后刷新时间: {datetime.now().strftime('%H:%M:%S')} | 数据源: Yahoo Finance")
