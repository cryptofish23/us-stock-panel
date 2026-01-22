import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. UI 深度定制 ---
st.set_page_config(page_title="PRO 隔夜美股热力中心", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 1rem 1.5rem; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* 板块卡片样式 */
    .stock-card {
        background: #161b26;
        border: 1px solid #2d3648;
        border-radius: 6px;
        padding: 0;
        margin: 5px 0;
        overflow: hidden;
    }
    .card-top { padding: 10px 10px 2px 10px; }
    .ticker-header { display: flex; justify-content: space-between; align-items: baseline; }
    .symbol { font-size: 0.9rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.7rem; color: #9ca3af; }
    .price-main { font-size: 1.1rem; color: #ffffff; font-family: 'Consolas', monospace; margin: 4px 0; font-weight: bold; }
    .up { color: #08d38d; }
    .down { color: #f23645; }
    
    /* 迷你图容器 */
    .spark-box { line-height: 0; margin-top: -2px; width: 100%; background: rgba(255,255,255,0.02); }
    svg { display: block; width: 100%; }

    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc; padding: 6px 12px; border-left: 4px solid #2962ff;
        font-size: 0.85rem; margin: 18px 0 10px 0; font-weight: bold;
    }
    
    /* 新闻卡片样式 */
    .news-container { margin: 10px 0 20px 0; }
    .news-card {
        background: #1e222d;
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 8px;
        border: 1px solid #2d3648;
        border-left: 4px solid #3b82f6;
    }
    .news-title { color: #ffffff; font-size: 0.9rem; font-weight: bold; text-decoration: none; display: block; margin-bottom: 4px; }
    .news-meta { color: #6b7280; font-size: 0.75rem; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 增强版全板块配置 ---
SECTIONS = {
    "MARKET INDICES (核心股指)": {
        '^DJI': '道琼斯', '^GSPC': '标普500', '^IXIC': '纳斯达克', 'NQ=F': '纳指期货', 'ES=F': '标普期货'
    },
    "CHIPS & AI (半导体)": {
        'NVDA': '英伟达', 'TSM': '台积电', 'AMD': '超威', 'AVGO': '博通', 'ASML': '阿斯麦', 'ARM': '安谋'
    },
    "STORAGE & OPTICS (存储/光模块)": {
        'MU': '美光', 'WDC': '西数', 'SMCI': '超微电脑', 'VRT': '维谛技术', 'COHR': '相干', 'AAOI': '应用光电'
    },
    "NEO CLOUD & MINING (AI算力基础设施)": {
        'IREN': 'IREN', 'WULF': 'WULF', 'APLD': 'Applied', 'HUT': 'Hut 8', 'CIFR': 'Cipher', 'CORZ': 'CoreSci'
    },
    "ENERGY & NUCLEAR (核电/储能)": {
        'VST': 'Vistra', 'CEG': 'Constell', 'OKLO': 'Oklo', 'SMR': 'NuScale', 'NNE': 'NanoNu', 'TLN': 'Talen'
    },
    "SPACE & DRONE (航天/无人机/国防)": {
        'RKLB': '罗克里', 'PLTR': '帕兰提尔', 'EH': '亿航', 'UAVS': 'AgEagle', 'BA': '波音', 'LMT': '洛克希德'
    },
    "CHINA STOCKS (核心中概)": {
        'BABA': '阿里巴巴', 'PDD': '拼多多', 'JD': '京东', 'BIDU': '百度', 'NIO': '蔚来', 'LI': '理想'
    }
}

# --- 3. 数据与新闻抓取函数 ---
@st.cache_data(ttl=60)
def get_stock_data(tickers):
    results = {}
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            df = stock.history(period="5d", interval="1h")
            if not df.empty:
                curr = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                chg = ((curr - prev) / prev) * 100
                hist = df['Close'].tail(20).tolist()
                results[t] = {'p': round(curr, 2), 'c': round(chg, 2), 'h': hist}
        except: continue
    return results

def draw_spark(data, color):
    if not data or len(data) < 2: return ""
    mi, ma = min(data), max(data)
    ran = ma - mi if ma != mi else 1
    pts = " ".join([f"{(i/(len(data)-1))*100},{30-((v-mi)/ran)*25}" for i, v in enumerate(data)])
    return f'<div class="spark-box"><svg viewBox="0 0 100 30" preserveAspectRatio="none" height="35"><polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" vector-effect="non-scaling-stroke"/></svg></div>'

# --- 4. 界面渲染 ---
st.title("⚡ 隔夜美股热力中心 (实时版)")

# A. 核心指数区
st.markdown("<div class='section-header'>MARKET INDICES (核心股指)</div>", unsafe_allow_html=True)
idx_tickers = SECTIONS["MARKET INDICES (核心股指)"]
idx_data = get_stock_data(list(idx_tickers.keys()))
cols = st.columns(len(idx_tickers))

for i, (sym, cname) in enumerate(idx_tickers.items()):
    with cols[i]:
        if sym in idx_data:
            d = idx_data[sym]
            color = "#08d38d" if d['c'] >= 0 else "#f23645"
            cls = "up" if d['c'] >= 0 else "down"
            html = f'<div class="stock-card"><div class="card-top"><div class="ticker-header"><span class="symbol">{sym}</span><span class="chinese-name">{cname}</span></div><div class="price-main">${d["p"]} <span class="{cls}">{d["c"]:+.2f}%</span></div></div>{draw_spark(d["h"], color)}</div>'
            st.markdown(html, unsafe_allow_html=True)

# B. 重要新闻区 (放在指数正下方)
st.markdown("<div class='section-header'>MARKET NEWS (美股重要实时要闻)</div>", unsafe_allow_html=True)
try:
    # 获取标普500相关新闻
    news_list = yf.Ticker("^GSPC").news
    if news_list:
        st.markdown('<div class="news-container">', unsafe_allow_html=True)
        # 展示前5条最重要新闻
        for n in news_list[:5]:
            time_str = datetime.fromtimestamp(n['providerPublishTime']).strftime('%Y-%m-%d %H:%M')
            st.markdown(f"""
                <div class="news-card">
                    <a href="{n['link']}" target="_blank" class="news-title">{n['title']}</a>
                    <div class="news-meta">{time_str} | 来源: {n['publisher']}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("暂无实时新闻数据")
except:
    st.error("无法加载新闻，请稍后刷新")

# C. 其他热门板块
for section_name, tickers in SECTIONS.items():
    if section_name == "MARKET INDICES (核心股指)": continue
    
    st.markdown(f"<div class='section-header'>{section_name}</div>", unsafe_allow_html=True)
    data_map = get_stock_data(list(tickers.keys()))
    scols = st.columns(len(tickers))
    
    for j, (sym, cname) in enumerate(tickers.items()):
        with scols[j]:
            if sym in data_map:
                sd = data_map[sym]
                scol = "#08d38d" if sd['c'] >= 0 else "#f23645"
                scls = "up" if sd['c'] >= 0 else "down"
                s_html = f'<div class="stock-card"><div class="card-top"><div class="ticker-header"><span class="symbol">{sym}</span><span class="chinese-name">{cname}</span></div><div class="price-main">${sd["p"]} <span class="{scls}">{sd["c"]:+.2f}%</span></div></div>{draw_spark(sd["h"], scol)}</div>'
                st.markdown(s_html, unsafe_allow_html=True)

st.markdown("---")
st.caption(f"最后自动刷新: {datetime.now().strftime('%H:%M:%S')} | 数据来源: Yahoo Finance API (实时盘前盘后)")
