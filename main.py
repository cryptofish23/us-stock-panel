import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. UI 深度定制（修复乱码与布局） ---
st.set_page_config(page_title="PRO 隔夜美股热力中心", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 1rem 1.5rem; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* 板块卡片样式 */
    .stock-card {
        background: #161b26; border: 1px solid #2d3648; border-radius: 6px;
        padding: 0; margin: 5px 0; overflow: hidden;
    }
    .card-top { padding: 10px 10px 2px 10px; }
    .ticker-header { display: flex; justify-content: space-between; align-items: baseline; }
    .symbol { font-size: 0.9rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.7rem; color: #9ca3af; }
    .price-main { font-size: 1.1rem; color: #ffffff; font-family: 'Consolas', monospace; margin: 4px 0; font-weight: bold; }
    .up { color: #08d38d; }
    .down { color: #f23645; }
    
    /* 迷你图 */
    .spark-box { line-height: 0; margin-top: -2px; width: 100%; background: rgba(255,255,255,0.02); }
    svg { display: block; width: 100%; }

    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc; padding: 6px 12px; border-left: 4px solid #2962ff;
        font-size: 0.85rem; margin: 18px 0 10px 0; font-weight: bold;
    }
    
    /* 新闻长条框样式（仿图1） */
    .news-box {
        background: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 6px; padding: 8px 12px; margin: 5px 0 15px 0;
    }
    .news-item {
        display: flex; align-items: center; border-bottom: 1px solid #2d3648;
        padding: 8px 0; text-decoration: none; transition: 0.2s;
    }
    .news-item:last-child { border-bottom: none; }
    .news-item:hover { background: rgba(255,255,255,0.02); }
    .news-tag {
        background: #ff4b4b; color: white; font-size: 0.65rem; padding: 1px 5px;
        border-radius: 3px; margin-right: 12px; font-weight: bold; flex-shrink: 0;
    }
    .news-title { color: #e5e7eb; font-size: 0.88rem; flex-grow: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .news-time { color: #6b7280; font-size: 0.75rem; margin-left: 15px; flex-shrink: 0; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 全板块配置 ---
SECTIONS = {
    "MARKET INDICES (核心股指)": {
        '^DJI': '道琼斯', '^GSPC': '标普500', '^IXIC': '纳斯达克', 'NQ=F': '纳指期货', 'ES=F': '标普期货'
    },
    "CHIPS & AI (半导体)": {
        'NVDA': '英伟达', 'TSM': '台积电', 'AMD': '超威', 'AVGO': '博通', 'ASML': '阿斯麦', 'ARM': '安谋'
    },
    "STORAGE & OPTICS (存储/光模块)": {
        'MU': '美光', 'WDC': '西数', 'SMCI': '超微', 'VRT': '维谛', 'COHR': '相干', 'AAOI': '应用光电'
    },
    "NEO CLOUD & MINING (AI算力)": {
        'IREN': 'IREN', 'WULF': 'WULF', 'APLD': 'Applied', 'HUT': 'Hut 8', 'CIFR': 'Cipher', 'CORZ': 'CoreSci'
    },
    "ENERGY & NUCLEAR (核电/储能)": {
        'VST': 'Vistra', 'CEG': 'Constell', 'OKLO': 'Oklo', 'SMR': 'NuScale', 'NNE': 'NanoNu', 'TLN': 'Talen'
    },
    "SPACE & DRONE (航天/无人机)": {
        'RKLB': '罗克里', 'PLTR': '帕兰提尔', 'EH': '亿航', 'UAVS': 'AgEagle', 'BA': '波音', 'LMT': '洛克希德'
    },
    "CHINA STOCKS (热门中概)": {
        'BABA': '阿里巴巴', 'PDD': '拼多多', 'JD': '京东', 'BIDU': '百度', 'NIO': '蔚来', 'LI': '理想'
    }
}

# --- 3. 数据抓取逻辑 ---
@st.cache_data(ttl=60)
def fetch_market_data(tickers):
    results = {}
    for t in tickers:
        try:
            # 抓取 5 天数据以计算最后 24 小时波动
            s = yf.Ticker(t)
            df = s.history(period="5d", interval="1h")
            if not df.empty:
                p_curr = df['Close'].iloc[-1]
                p_prev = df['Close'].iloc[-2]
                chg = ((p_curr - p_prev) / p_prev) * 100
                hist = df['Close'].tail(20).tolist()
                results[t] = {'p': round(p_curr, 2), 'c': round(chg, 2), 'h': hist}
        except: continue
    return results

def get_spark(data, color):
    if not data or len(data) < 2: return ""
    mi, ma = min(data), max(data)
    ran = (ma - mi) if ma != mi else 1
    pts = " ".join([f"{(i/(len(data)-1))*100},{30-((v-mi)/ran)*25}" for i, v in enumerate(data)])
    return f'<div class="spark-box"><svg viewBox="0 0 100 30" preserveAspectRatio="none" height="35"><polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" vector-effect="non-scaling-stroke"/></svg></div>'

# --- 4. 界面渲染 ---
st.title("⚡ 隔夜美股热力中心 (Pro Fix)")

# A. 核心指数
st.markdown("<div class='section-header'>MARKET INDICES (核心股指)</div>", unsafe_allow_html=True)
idx_map = SECTIONS["MARKET INDICES (核心股指)"]
idx_res = fetch_market_data(list(idx_map.keys()))
cols = st.columns(len(idx_map))

for i, (sym, cname) in enumerate(idx_map.items()):
    with cols[i]:
        if sym in idx_res:
            d = idx_res[sym]
            color = "#08d38d" if d['c'] >= 0 else "#f23645"
            st.markdown(f'<div class="stock-card"><div class="card-top"><div class="ticker-header"><span class="symbol">{sym}</span><span class="chinese-name">{cname}</span></div><div class="price-main">${d["p"]} <span class="{"up" if d["c"]>=0 else "down"}">{d["c"]:+.2f}%</span></div></div>{get_spark(d["h"], color)}</div>', unsafe_allow_html=True)

# B. 实时新闻 (位于指数下方长条框)
st.markdown("<div class='section-header'>BREAKING NEWS (美股重要实时要闻)</div>", unsafe_allow_html=True)
try:
    # 尝试从纳指期货获取新闻，它通常更新最快
    news_data = yf.Ticker("NQ=F").news
    if not news_data: # 备用源
        news_data = yf.Ticker("^GSPC").news
        
    if news_data:
        news_html = '<div class="news-box">'
        for n in news_data[:4]: # 仅显示最新4条
            tm = datetime.fromtimestamp(n['providerPublishTime']).strftime('%H:%M')
            news_html += f'<a href="{n["link"]}" target="_blank" class="news-item"><span class="news-tag">LIVE</span><span class="news-title">{n["title"]}</span><span class="news-time">{tm}</span></a>'
        news_html += '</div>'
        st.markdown(news_html, unsafe_allow_html=True)
    else:
        st.info("💡 正在同步全球财经接口，请稍后刷新...")
except Exception as e:
    st.markdown('<div class="news-box" style="color:#6b7280; font-size:0.8rem;">⚠️ 财经要闻接口响应中，请稍后手动刷新页面。</div>', unsafe_allow_html=True)

# C. 渲染其他板块
for name, tickers in SECTIONS.items():
    if name == "MARKET INDICES (核心股指)": continue
    st.markdown(f"<div class='section-header'>{name}</div>", unsafe_allow_html=True)
    data_res = fetch_market_data(list(tickers.keys()))
    scols = st.columns(len(tickers))
    for j, (sym, cn) in enumerate(tickers.items()):
        with scols[j]:
            if sym in data_res:
                sd = data_res[sym]
                scolor = "#08d38d" if sd['c'] >= 0 else "#f23645"
                st.markdown(f'<div class="stock-card"><div class="card-top"><div class="ticker-header"><span class="symbol">{sym}</span><span class="chinese-name">{cn}</span></div><div class="price-main">${sd["p"]} <span class="{"up" if sd["c"]>=0 else "down"}">{sd["c"]:+.2f}%</span></div></div>{get_spark(sd["h"], scolor)}</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption(f"最后自动刷新: {datetime.now().strftime('%H:%M:%S')} | 数据源: Yahoo Finance (包含盘前盘后实时价)")
