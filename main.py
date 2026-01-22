import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. UI 深度定制（消除乱码与对齐布局） ---
st.set_page_config(page_title="PRO 美股热力中心", page_icon="⚡", layout="wide")

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
    
    /* 趋势线 SVG */
    .spark-box { line-height: 0; margin-top: -2px; width: 100%; background: rgba(255,255,255,0.02); }
    svg { display: block; width: 100%; }

    /* 板块标题 */
    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc; padding: 6px 12px; border-left: 4px solid #2962ff;
        font-size: 0.85rem; margin: 18px 0 10px 0; font-weight: bold;
    }
    
    /* 新闻长条框（仿图1样式） */
    .news-box {
        background: rgba(59, 130, 246, 0.05);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 6px; padding: 12px; margin: 10px 0;
    }
    .news-item {
        display: flex; align-items: center; border-bottom: 1px solid #2d3648;
        padding: 6px 0; text-decoration: none;
    }
    .news-item:last-child { border-bottom: none; }
    .news-tag {
        background: #3b82f6; color: white; font-size: 0.65rem; padding: 1px 5px;
        border-radius: 3px; margin-right: 10px; font-weight: bold;
    }
    .news-title { color: #e5e7eb; font-size: 0.85rem; flex-grow: 1; }
    .news-time { color: #6b7280; font-size: 0.7rem; min-width: 50px; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 增强型全板块配置 ---
SECTIONS = {
    "MARKET INDICES (核心股指)": {
        '^DJI': '道琼斯', '^GSPC': '标普500', '^IXIC': '纳斯达克', 'NQ=F': '纳指期货', 'ES=F': '标普期货'
    },
    "CHIPS & AI (半导体)": {
        'NVDA': '英伟达', 'TSM': '台积电', 'AMD': '超威', 'AVGO': '博通', 'ASML': '阿斯麦', 'ARM': '安谋'
    },
    "STORAGE & OPTICS (存储/光模块)": {
        'MU': '美光', 'WDC': '西数', 'SMCI': '超微', 'VRT': '维谛技术', 'COHR': '相干', 'AAOI': '应用光电'
    },
    "NEO CLOUD & MINING (AI基础设施)": {
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

# --- 3. 数据与新闻抓取 ---
@st.cache_data(ttl=60)
def get_full_market_data(tickers):
    results = {}
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            # 抓取包含夜盘/小时级别的数据
            df = stock.history(period="5d", interval="1h")
            if not df.empty:
                last_p = df['Close'].iloc[-1]
                prev_p = df['Close'].iloc[-2]
                chg = ((last_p - prev_p) / prev_p) * 100
                hist = df['Close'].tail(20).tolist()
                results[t] = {'p': round(last_p, 2), 'c': round(chg, 2), 'h': hist}
        except: continue
    return results

def make_spark(data, color):
    if not data or len(data) < 2: return ""
    mi, ma = min(data), max(data)
    ran = ma - mi if ma != mi else 1
    pts = " ".join([f"{(i/(len(data)-1))*100},{30-((v-mi)/ran)*25}" for i, v in enumerate(data)])
    return f'<div class="spark-box"><svg viewBox="0 0 100 30" preserveAspectRatio="none" height="35"><polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" vector-effect="non-scaling-stroke"/></svg></div>'

# --- 4. 界面渲染 ---
st.title("⚡ 隔夜美股热力中心 (Pro Fix)")

# A. 核心指数
st.markdown("<div class='section-header'>MARKET INDICES (核心股指)</div>", unsafe_allow_html=True)
idx_dict = SECTIONS["MARKET INDICES (核心股指)"]
idx_data = get_full_market_data(list(idx_dict.keys()))
cols = st.columns(len(idx_dict))

for i, (sym, cname) in enumerate(idx_dict.items()):
    with cols[i]:
        if sym in idx_data:
            d = idx_data[sym]
            color = "#08d38d" if d['c'] >= 0 else "#f23645"
            cls = "up" if d['c'] >= 0 else "down"
            card_html = f'<div class="stock-card"><div class="card-top"><div class="ticker-header"><span class="symbol">{sym}</span><span class="chinese-name">{cname}</span></div><div class="price-main">${d["p"]} <span class="{cls}">{d["c"]:+.2f}%</span></div></div>{make_spark(d["h"], color)}</div>'
            st.markdown(card_html, unsafe_allow_html=True)

# B. 重要新闻 (仿图1样式，位于指数下方)
st.markdown("<div class='section-header'>BREAKING NEWS (实时市场要闻)</div>", unsafe_allow_html=True)
try:
    # 抓取综合新闻
    news_feed = yf.Ticker("^GSPC").news
    if news_feed:
        news_html = '<div class="news-box">'
        for n in news_feed[:4]: # 展示4条最新新闻
            t_str = datetime.fromtimestamp(n['providerPublishTime']).strftime('%H:%M')
            news_html += f"""
                <a href="{n['link']}" target="_blank" class="news-item">
                    <span class="news-tag">BREAKING</span>
                    <span class="news-title">{n['title']}</span>
                    <span class="news-time">{t_str}</span>
                </a>
            """
        news_html += '</div>'
        st.markdown(news_html, unsafe_allow_html=True)
    else:
        st.write("新闻接口暂时繁忙，请刷新重试...")
except:
    st.write("新闻加载失败，建议检查 GitHub Actions 部署状态")

# C. 其他板块
for section, tickers in SECTIONS.items():
    if section == "MARKET INDICES (核心股指)": continue
    st.markdown(f"<div class='section-header'>{section}</div>", unsafe_allow_html=True)
    sec_data = get_full_market_data(list(tickers.keys()))
    scols = st.columns(len(tickers))
    for j, (sym, cname) in enumerate(tickers.items()):
        with scols[j]:
            if sym in sec_data:
                sd = sec_data[sym]
                scol = "#08d38d" if sd['c'] >= 0 else "#f23645"
                scls = "up" if sd['c'] >= 0 else "down"
                s_card = f'<div class="stock-card"><div class="card-top"><div class="ticker-header"><span class="symbol">{sym}</span><span class="chinese-name">{cname}</span></div><div class="price-main">${sd["p"]} <span class="{scls}">{sd["c"]:+.2f}%</span></div></div>{make_spark(sd["h"], scol)}</div>'
                st.markdown(s_card, unsafe_allow_html=True)

st.markdown("---")
st.caption(f"最后自动刷新: {datetime.now().strftime('%H:%M:%S')} | 数据源: Yahoo Finance API")
