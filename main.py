import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. 页面配置与深度 UI 定制 ---
st.set_page_config(page_title="PRO 隔夜美股热力中心", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 1rem 1.5rem; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* 个股卡片 */
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
    .symbol { font-size: 0.95rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.7rem; color: #9ca3af; }
    .price-main { font-size: 1.15rem; color: #ffffff; font-family: 'Consolas', monospace; margin: 4px 0; font-weight: bold; }
    .up { color: #08d38d; }
    .down { color: #f23645; }
    
    /* 迷你图 */
    .spark-box { line-height: 0; margin-top: -2px; width: 100%; background: rgba(255,255,255,0.02); }
    svg { display: block; width: 100%; }

    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc; padding: 6px 12px; border-left: 4px solid #2962ff;
        font-size: 0.85rem; margin: 18px 0 8px 0; font-weight: bold;
    }
    
    /* 新闻样式 */
    .news-card {
        background: #1e222d; border-radius: 4px; padding: 8px; margin-bottom: 6px; border-left: 3px solid #3b82f6;
    }
    .news-title { color: #ffffff; font-size: 0.85rem; text-decoration: none; }
    .news-time { color: #6b7280; font-size: 0.7rem; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 增强型板块配置 ---
SECTIONS = {
    "MARKET INDICES (核心股指)": {
        '^DJI': '道琼斯', '^GSPC': '标普500', '^IXIC': '纳斯达克', 'NQ=F': '纳指期货', 'ES=F': '标普期货'
    },
    "CHIPS & AI (半导体)": {
        'NVDA': '英伟达', 'TSM': '台积电', 'AMD': '超威', 'AVGO': '博通', 'ASML': '阿斯麦', 'ARM': '安谋'
    },
    "NEO CLOUD & MINING (AI算力)": {
        'IREN': 'IREN', 'WULF': 'WULF', 'APLD': 'Applied', 'HUT': 'Hut 8', 'CIFR': 'Cipher', 'CORZ': 'CoreSci'
    },
    "STORAGE & OPTICS (存储/光模块)": {
        'MU': '美光', 'WDC': '西数', 'SMCI': '超微电脑', 'VRT': '维谛技术', 'COHR': '相干', 'AAOI': '应用光电'
    },
    "ENERGY & NUCLEAR (核电/储能)": {
        'VST': 'Vistra', 'CEG': 'Constell', 'OKLO': 'Oklo', 'SMR': 'NuScale', 'NNE': 'NanoNu', 'TLN': 'Talen'
    },
    "SPACE & DRONE (航天/无人机)": {
        'RKLB': '罗克里', 'PLTR': '帕兰提尔', 'EH': '亿航', 'UAVS': 'AgEagle', 'BA': '波音', 'LMT': '洛克希德'
    },
    "CHINA STOCKS (核心中概)": {
        'BABA': '阿里巴巴', 'PDD': '拼多多', 'JD': '京东', 'BIDU': '百度', 'NIO': '蔚来', 'LI': '理想'
    }
}

# --- 3. 数据抓取逻辑 (含夜盘与新闻) ---
@st.cache_data(ttl=60)
def get_market_full_data(tickers):
    results = {}
    for t in tickers:
        try:
            # 抓取 5 天数据，确保即使在非交易时段也能获得最后成交价
            stock = yf.Ticker(t)
            df = stock.history(period="5d", interval="1h")
            if not df.empty:
                last_val = df['Close'].iloc[-1]
                prev_val = df['Close'].iloc[-2]
                chg = ((last_val - prev_val) / prev_val) * 100
                hist = df['Close'].tail(20).tolist()
                results[t] = {'p': round(last_val, 2), 'c': round(chg, 2), 'h': hist}
        except: continue
    return results

def draw_sparkline(data, color):
    if not data or len(data) < 2: return ""
    v_min, v_max = min(data), max(data)
    v_range = v_max - v_min if v_max != v_min else 1
    points = " ".join([f"{(i/(len(data)-1))*100},{30-((v-v_min)/v_range)*25}" for i, v in enumerate(data)])
    return f'<div class="spark-box"><svg viewBox="0 0 100 30" preserveAspectRatio="none" height="35"><polyline points="{points}" fill="none" stroke="{color}" stroke-width="2" vector-effect="non-scaling-stroke"/></svg></div>'

# --- 4. 侧边栏：重要新闻 ---
with st.sidebar:
    st.markdown("<h3 style='color:white;'>实时财经要闻</h3>", unsafe_allow_html=True)
    try:
        # 抓取标普500相关新闻作为市场指标
        market_news = yf.Ticker("^GSPC").news
        for news in market_news[:10]:
            dt = datetime.fromtimestamp(news['providerPublishTime']).strftime('%H:%M')
            st.markdown(f"""
                <div class="news-card">
                    <a class="news-title" href="{news['link']}" target="_blank">{news['title'][:50]}...</a><br>
                    <span class="news-time">{dt} | {news['publisher']}</span>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.write("新闻加载中...")

# --- 5. 主界面渲染 ---
st.title("⚡ 隔夜美股热力中心 (全板块实时版)")

for section, tickers in SECTIONS.items():
    st.markdown(f"<div class='section-header'>{section}</div>", unsafe_allow_html=True)
    
    data_map = get_market_full_data(list(tickers.keys()))
    cols = st.columns(len(tickers))
    
    for i, (symbol, c_name) in enumerate(tickers.items()):
        with cols[i]:
            if symbol in data_map:
                d = data_map[symbol]
                color = "#08d38d" if d['c'] >= 0 else "#f23645"
                cls = "up" if d['c'] >= 0 else "down"
                
                # HTML 拼装，确保没有多余空格导致解析错误
                html_str = f'<div class="stock-card"><div class="card-top"><div class="ticker-header"><span class="symbol">{symbol}</span><span class="chinese-name">{c_name}</span></div><div class="price-main">${d["p"]} <span class="{cls}">{d["c"]:+.2f}%</span></div></div>{draw_sparkline(d["h"], color)}</div>'
                st.markdown(html_str, unsafe_allow_html=True)

st.markdown("---")
st.caption(f"数据更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (包含电子盘数据) | 自动刷新: 每 60s")
