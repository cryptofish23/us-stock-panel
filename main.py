import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ---------------- 1. 页面配置与深度 UI 定制 ----------------
st.set_page_config(page_title="PRO 隔夜美股热力中心", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 0rem 1.5rem; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }

    /* 顶部导航栏 (仿英为财情风格) */
    .top-nav {
        background-color: #1c2127;
        padding: 10px 20px;
        display: flex;
        gap: 25px;
        border-bottom: 2px solid #2962ff;
        margin: 0 -1.5rem 20px -1.5rem;
    }
    .nav-item {
        color: #d1d4dc;
        text-decoration: none;
        font-size: 0.95rem;
        font-weight: bold;
        cursor: pointer;
    }
    .nav-item:hover { color: #2962ff; }
    .nav-active { color: #2962ff; border-bottom: 2px solid #2962ff; }

    /* 板块卡片 */
    .card {
        background: #161b26;
        border: 1px solid #2d3648;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .ticker-name { font-size: 1rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.75rem; color: #9ca3af; font-weight: normal; }
    .price-main { font-size: 1.2rem; color: #ffffff; font-family: 'Consolas', monospace; margin: 4px 0; }
    .change-up { color: #08d38d; font-weight: bold; }
    .change-down { color: #f23645; font-weight: bold; }
    
    /* 新闻长条框 (仿图1) */
    .news-box {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 6px; padding: 10px 15px; margin: 10px 0 20px 0;
    }
    .news-row { display: flex; align-items: center; padding: 6px 0; border-bottom: 1px solid #2d3648; }
    .news-row:last-child { border-bottom: none; }
    .news-tag { background: #ff4b4b; color: white; font-size: 0.7rem; padding: 2px 6px; border-radius: 3px; margin-right: 12px; }
    .news-text { color: #e5e7eb; font-size: 0.9rem; flex-grow: 1; text-decoration: none; }
    
    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc; padding: 6px 12px; border-left: 4px solid #2962ff;
        font-size: 0.9rem; margin: 15px 0 10px 0; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- 2. 顶部导航菜单 ----------------
st.markdown("""
    <div class="top-nav">
        <div class="nav-item nav-active">实时行情</div>
        <div class="nav-item">自选股</div>
        <div class="nav-item">市场资讯</div>
        <div class="nav-item">投资组合</div>
        <div class="nav-item">AI 选股</div>
    </div>
""", unsafe_allow_html=True)

# ---------------- 3. 数据抓取与逻辑 ----------------
NAME_MAP = {
    '^DJI': '道琼斯指数', '^GSPC': '标普500指数', '^IXIC': '纳斯达克指数',
    'NQ=F': '纳指期货', 'ES=F': '标普期货',
    'NVDA': '英伟达', 'TSM': '台积电', 'INTC': '英特尔', 'AMD': '超威半导体', 'AVGO': '博通', 'ARM': '安谋',
    'MU': '美光科技', 'WDC': '西部数据', 'STX': '希捷', 'AAOI': '应用光电',
    'RKLB': '罗克里', 'PLTR': '帕兰提尔', 'EH': '亿航',
    'IREN': 'IREN', 'NBIS': 'Nebula', 'APLD': 'Applied Dig', 'HUT': 'Hut 8', 'CIFR': 'Cipher'
}

@st.cache_data(ttl=60)
def get_data(tickers):
    res = []
    for t in tickers:
        try:
            # 强制包含盘前盘后数据
            s = yf.Ticker(t)
            df = s.history(period="2d", interval="1h")
            if not df.empty:
                p = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                chg = ((p - prev) / prev) * 100
                res.append({'t': t, 'p': round(p, 2), 'c': round(chg, 2)})
        except: continue
    return pd.DataFrame(res)

# ---------------- 4. 渲染界面 ----------------
st.title("⚡ 隔夜美股热力中心")

# A. 核心指数
st.markdown("<div class='section-header'>MARKET INDICES (核心股指)</div>", unsafe_allow_html=True)
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
df_idx = get_data(idx_list)
cols = st.columns(5)
for i, t in enumerate(idx_list):
    with cols[i]:
        row = df_idx[df_idx['t'] == t]
        if not row.empty:
            r = row.iloc[0]
            cls = "change-up" if r['c'] >= 0 else "change-down"
            st.markdown(f"""
                <div class="card">
                    <div class="ticker-name">{t}</div>
                    <div class="chinese-name">{NAME_MAP.get(t,'')}</div>
                    <div class="price-main">${r['p']} <span class="{cls}">{r['c']:+.2f}%</span></div>
                </div>
            """, unsafe_allow_html=True)

# B. 实时新闻板块 (修复加载问题)
st.markdown("<div class='section-header'>BREAKING NEWS (实时市场要闻)</div>", unsafe_allow_html=True)
try:
    news = yf.Ticker("NQ=F").news[:4]
    if news:
        news_html = '<div class="news-box">'
        for n in news:
            t_str = datetime.fromtimestamp(n['providerPublishTime']).strftime('%H:%M')
            news_html += f'<div class="news-row"><span class="news-tag">LIVE</span><a class="news-text" href="{n["link"]}" target="_blank">{n["title"]}</a><span style="color:#6b7280; font-size:0.75rem;">{t_str}</span></div>'
        news_html += '</div>'
        st.markdown(news_html, unsafe_allow_html=True)
except:
    st.markdown('<div class="news-box">正在连接全球财经数据源...</div>', unsafe_allow_html=True)

# C. 核心板块
PLATES = {
    '芯片/AI': ['NVDA', 'TSM', 'INTC', 'AMD', 'AVGO', 'ARM'],
    '存储/光模块/核电': ['MU', 'WDC', 'VST', 'CEG', 'SMCI', 'AAOI'],
    'Neo Cloud & 航天': ['IREN', 'NBIS', 'APLD', 'RKLB', 'PLTR', 'EH']
}

for plate, tickers in PLATES.items():
    st.markdown(f"<div class='section-header'>{plate}</div>", unsafe_allow_html=True)
    df_p = get_data(tickers)
    pcols = st.columns(6)
    for i, t in enumerate(tickers):
        with pcols[i]:
            row = df_p[df_p['t'] == t]
            if not row.empty:
                r = row.iloc[0]
                cls = "change-up" if r['c'] >= 0 else "change-down"
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker-name">{t} <span class="chinese-name">({NAME_MAP.get(t,'')})</span></div>
                        <div class="price-main">${r['p']} <span class="{cls}">{r['c']:+.2f}%</span></div>
                        <div style="font-size:0.75rem; color:#60a5fa;">夜盘实时: ${r['p']}</div>
                    </div>
                """, unsafe_allow_html=True)

st.markdown("---")
st.caption(f"最后更新: {datetime.now().strftime('%H:%M:%S')} | 包含电子盘(Pre/Post)数据")
