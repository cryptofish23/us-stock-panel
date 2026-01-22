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
    
    .stock-card {
        background: #161b26;
        border: 1px solid #2d3648;
        border-radius: 6px;
        padding: 0;
        margin: 5px 0;
        overflow: hidden;
    }
    .card-top { padding: 12px 12px 4px 12px; }
    .ticker-header { display: flex; justify-content: space-between; align-items: baseline; }
    .symbol { font-size: 1rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.72rem; color: #9ca3af; }
    .price-main { font-size: 1.25rem; color: #ffffff; font-family: 'Consolas', monospace; margin: 4px 0; font-weight: bold; }
    .up { color: #08d38d; }
    .down { color: #f23645; }
    
    .spark-box { line-height: 0; margin-top: -2px; width: 100%; }
    svg { display: block; width: 100%; }

    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc; padding: 6px 12px; border-left: 4px solid #2962ff;
        font-size: 0.9rem; margin: 20px 0 10px 0; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 增强版板块配置 ---
SECTIONS = {
    "MARKET INDICES (核心股指)": {
        '^DJI': '道琼斯', '^GSPC': '标普500', '^IXIC': '纳斯达克', 'NQ=F': '纳指期货', 'ES=F': '标普期货'
    },
    "CHIPS & AI (核心芯片)": {
        'NVDA': '英伟达', 'TSM': '台积电', 'AMD': '超威', 'AVGO': '博通', 'ARM': '安谋', 'ASML': '阿斯麦'
    },
    "AI & TECH (科技巨头)": {
        'AAPL': '苹果', 'MSFT': '微软', 'GOOGL': '谷歌', 'AMZN': '亚马逊', 'META': '脸书', 'TSLA': '特斯拉'
    },
    "STORAGE & OPTICS (存储与光模块)": {
        'MU': '美光', 'WDC': '西数', 'STX': '希捷', 'SMCI': '超微电脑', 'VRT': '维谛技术', 'COHR': '相干'
    },
    "SPACE & DEFENSE (航天国防)": {
        'LMT': '洛克希德', 'RTX': '雷神', 'BA': '波音', 'NOC': '诺斯罗普', 'PLTR': '帕兰提尔'
    },
    "CHINA STOCKS (核心中概)": {
        'BABA': '阿里巴巴', 'PDD': '拼多多', 'JD': '京东', 'BIDU': '百度', 'NIO': '蔚来', 'LI': '理想'
    }
}

@st.cache_data(ttl=60)
def get_bulk_data(tickers):
    results = {}
    for t in tickers:
        try:
            # 抓取 5 天数据确保平滑
            df = yf.Ticker(t).history(period="5d", interval="1h")
            if not df.empty:
                last = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                chg = ((last - prev) / prev) * 100
                hist = df['Close'].tail(20).tolist()
                results[t] = {'p': round(last, 2), 'c': round(chg, 2), 'h': hist}
        except: continue
    return results

def draw_sparkline(data, color):
    if not data or len(data) < 2: return ""
    v_min, v_max = min(data), max(data)
    v_range = v_max - v_min if v_max != v_min else 1
    points = ""
    for i, v in enumerate(data):
        x = (i / (len(data) - 1)) * 100
        y = 30 - ((v - v_min) / v_range) * 25
        points += f"{x},{y} "
    # 返回纯 SVG 字符串，避免多层 div 嵌套导致解析错误
    return f'<div class="spark-box"><svg viewBox="0 0 100 30" preserveAspectRatio="none" height="40"><polyline points="{points}" fill="none" stroke="{color}" stroke-width="2" vector-effect="non-scaling-stroke"/></svg></div>'

# --- 3. 页面渲染逻辑 ---
st.title("⚡ 隔夜美股热力中心 (Pro Fix v2)")

for section_name, tickers in SECTIONS.items():
    st.markdown(f"<div class='section-header'>{section_name}</div>", unsafe_allow_html=True)
    
    # 抓取当前板块数据
    data_map = get_bulk_data(list(tickers.keys()))
    
    # 动态创建列（每行最多 6 个）
    cols = st.columns(len(tickers))
    for i, (symbol, c_name) in enumerate(tickers.items()):
        with cols[i]:
            if symbol in data_map:
                d = data_map[symbol]
                color = "#08d38d" if d['c'] >= 0 else "#f23645"
                cls = "up" if d['c'] >= 0 else "down"
                
                # 构建完整的 HTML 字符串，一次性渲染减少出错概率
                card_html = f"""
                <div class="stock-card">
                    <div class="card-top">
                        <div class="ticker-header">
                            <span class="symbol">{symbol}</span>
                            <span class="chinese-name">{c_name}</span>
                        </div>
                        <div class="price-main">${d['p']} <span class="{cls}">{d['c']:+.2f}%</span></div>
                    </div>
                    {draw_sparkline(d['h'], color)}
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

st.caption(f"最后刷新: {datetime.now().strftime('%H:%M:%S')} | 实时同步自 Yahoo Finance")
