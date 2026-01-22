import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

# 页面配置
st.set_page_config(page_title="AI美股热力看板", page_icon="⚡", layout="wide")

# 极简紧凑 CSS (TradingView Dark Style)
st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 1rem 2rem; }
    .card {
        background: #161c27;
        border: 1px solid #1e293b;
        border-radius: 4px;
        padding: 8px;
        margin-bottom: 2px;
        position: relative;
    }
    .ticker { font-size: 1.1rem; font-weight: 800; color: #ffffff; display: flex; justify-content: space-between;}
    .hot-icon { color: #ff9800; font-size: 0.8rem; }
    .price { font-size: 1.0rem; color: #d1d4dc; margin: 2px 0; }
    .change-up { color: #08d38d; font-weight: bold; }
    .change-down { color: #f23645; font-weight: bold; }
    .vol-label { font-size: 0.7rem; color: #636b79; }
    .section-header {
        background: #1e222d;
        color: #d1d4dc;
        padding: 4px 12px;
        border-left: 4px solid #2962ff;
        font-size: 0.95rem;
        font-weight: 600;
        margin: 18px 0 6px 0;
        display: flex; justify-content: space-between;
    }
    </style>
""", unsafe_allow_html=True)

# 1. 动态板块配置
PLATES = {
    '半导体/AI': ['NVDA', 'TSM', 'INTC', 'AMD', 'AVGO', 'QCOM', 'ASML', 'ARM', 'MRVL'],
    '存储': ['MU', 'WDC', 'STX'],
    '航空航天': ['RKLB', 'LUNR', 'ASTS', 'PL', 'BA', 'SPCE'],
    '加密概念': ['MSTR', 'COIN', 'HOOD', 'BMNR', 'MARA', 'RIOT'],
    '能源/储能': ['BE', 'EOSE', 'FLNC', 'TSLA', 'ENPH'],
    '光模块': ['LITE', 'CIEN', 'AAOI', 'COHR']
}

# 2. 数据获取与缓存 (缓存10分钟)
@st.cache_data(ttl=600)
def get_market_data(tickers):
    try:
        data = yf.download(tickers, period="2d", interval="1d", progress=False)
        if data.empty: return None
        
        result = []
        for t in tickers:
            try:
                # 计算涨跌幅
                close_prices = data['Close'][t].dropna()
                open_prices = data['Open'][t].dropna()
                if len(close_prices) < 1: continue
                
                curr_price = close_prices.iloc[-1]
                prev_open = open_prices.iloc[-1]
                change_pct = ((curr_price - prev_open) / prev_open) * 100
                volume = data['Volume'][t].iloc[-1]
                
                result.append({
                    'Ticker': t,
                    'Price': round(curr_price, 2),
                    'Change': round(change_pct, 2),
                    'Volume': volume,
                    'Hot': volume > 5000000 # 简单逻辑：成交量大于5M视为高关注
                })
            except: continue
        return pd.DataFrame(result)
    except:
        return None

# 3. 界面渲染
st.title("⚡ 美股隔夜热力看板")
st.caption(f"实时监测：动态排序板块领涨股 | 更新时间: {date.today()}")

for plate, tickers in PLATES.items():
    df = get_market_data(tickers)
    
    if df is not None and not df.empty:
        # --- 核心逻辑：按涨幅排序 ---
        df = df.sort_values(by='Change', ascending=False)
        
        avg_chg = df['Change'].mean()
        avg_color = "color: #08d38d" if avg_chg > 0 else "color: #f23645"
        
        st.markdown(f"""
            <div class='section-header'>
                <span>{plate}</span>
                <span style='{avg_color}'>板块均幅: {avg_chg:+.2f}%</span>
            </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(5)
        for i, row in df.iterrows():
            with cols[i % 5]:
                cls = "change-up" if row['Change'] > 0 else "change-down"
                hot_tag = "<span class='hot-icon'>🔥</span>" if row['Hot'] else ""
                
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker">
                            {row['Ticker']} {hot_tag}
                        </div>
                        <div class="price">${row['Price']}</div>
                        <div class="{cls}">{row['Change']:+.2f}%</div>
                        <div class="vol-label">Vol: {row['Volume']//1000000}M</div>
                    </div>
                """, unsafe_allow_html=True)
                # 迷你趋势
                c_color = "#08d38d" if row['Change'] > 0 else "#f23645"
                st.line_chart([1, 1 + row['Change']/100], height=20, use_container_width=True, color=c_color)
    else:
        st.warning(f"{plate} 正在等待 API 响应...")

# 重要新闻流
st.markdown("<div class='section-header'>MARKET FOCUS</div>", unsafe_allow_html=True)
st.info("💡 系统已自动将各板块涨幅最高的个股置顶展示。带 🔥 标志表示该股当前成交活跃度极高。")

st.markdown("---")
st.caption("Data provided by yfinance. 排序逻辑：(Today Close - Today Open) / Today Open")
