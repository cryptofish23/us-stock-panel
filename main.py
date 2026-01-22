import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date

# 页面配置
st.set_page_config(page_title="精准美股看板", page_icon="🎯", layout="wide")

# 极致紧凑 UI CSS
st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .card {
        background: #161c27; border: 1px solid #1e293b;
        border-radius: 4px; padding: 6px; margin-bottom: 2px;
    }
    .ticker-row { display: flex; justify-content: space-between; align-items: center; }
    .ticker { font-size: 1.1rem; font-weight: 800; color: #ffffff; }
    .price-main { font-size: 1rem; color: #ffffff; font-family: monospace; }
    .change-up { color: #08d38d; font-weight: bold; font-size: 1rem; }
    .change-down { color: #f23645; font-weight: bold; font-size: 1rem; }
    .ext-box { 
        margin-top: 4px; padding-top: 4px; border-top: 1px dashed #2d3748;
        font-size: 0.8rem; color: #3b82f6; display: flex; justify-content: space-between;
    }
    .section-header {
        background: #1e222d; color: #d1d4dc; padding: 5px 12px;
        border-left: 4px solid #2962ff; font-size: 0.9rem;
        margin: 15px 0 5px 0; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- 核心数据抓取函数 ----------------
def get_accurate_data(tickers):
    results = []
    # 获取基础行情
    # yf.download 可能存在延迟，改用 Tickers 批量获取 info 
    group = yf.Tickers(' '.join(tickers))
    
    for t in tickers:
        try:
            info = group.tickers[t].info
            # 1. 核心价格与日内涨幅 (收盘价 vs 昨收)
            regular_price = info.get('regularMarketPrice', 0)
            prev_close = info.get('regularMarketPreviousClose', 1)
            day_change_pct = ((regular_price - prev_close) / prev_close) * 100
            
            # 2. 夜盘价格与变动 (盘后)
            post_price = info.get('postMarketPrice') or info.get('preMarketPrice') or regular_price
            post_change_pct = ((post_price - regular_price) / regular_price) * 100 if regular_price > 0 else 0
            
            results.append({
                'Ticker': t,
                'Price': round(regular_price, 2),
                'DayChange': round(day_change_pct, 2),
                'ExtPrice': round(post_price, 2),
                'ExtChange': round(post_change_pct, 2),
                'Vol': info.get('regularMarketVolume', 0)
            })
        except Exception as e:
            continue
    return pd.DataFrame(results)

# ---------------- UI 渲染 ----------------
st.title("🎯 精准隔夜热门面板")

# 1. 指数与期货
st.markdown("<div class='section-header'>MARKET INDICES & FUTURES</div>", unsafe_allow_html=True)
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
df_idx = get_accurate_data(idx_list)

if not df_idx.empty:
    cols = st.columns(5)
    for i, row in df_idx.iterrows():
        with cols[i]:
            cls = "change-up" if row['DayChange'] > 0 else "change-down"
            st.markdown(f"""
                <div class="card">
                    <div class="ticker-row"><span class="ticker">{row['Ticker']}</span></div>
                    <div class="price-main">${row['Price']} <span class="{cls}">{row['DayChange']:+.2f}%</span></div>
                    <div class="ext-box">
                        <span>夜盘: ${row['ExtPrice']}</span>
                        <span style="color:{'#08d38d' if row['ExtChange']>=0 else '#f23645'}">{row['ExtChange']:+.2f}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# 2. 动态板块 (自动排序)
PLATES = {
    '芯片/AI (核对版)': ['NVDA', 'TSM', 'INTC', 'AMD', 'AVGO', 'ARM'],
    '存储/光模块': ['MU', 'WDC', 'STX', 'LITE', 'CIEN', 'AAOI'],
    '航天/无人机': ['RKLB', 'LUNR', 'ASTS', 'RCAT', 'AVAV', 'ONDS'],
    '加密/Neo Cloud': ['MSTR', 'COIN', 'HOOD', 'IREN', 'NBIS', 'APLD']
}

for plate, tickers in PLATES.items():
    st.markdown(f"<div class='section-header'>{plate}</div>", unsafe_allow_html=True)
    df = get_accurate_data(tickers)
    if not df.empty:
        # 核心逻辑：按日内涨幅降序排列
        df = df.sort_values(by='DayChange', ascending=False).reset_index(drop=True)
        cols = st.columns(6)
        for i, row in df.iterrows():
            with cols[i % 6]:
                cls = "change-up" if row['DayChange'] > 0 else "change-down"
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker">{row['Ticker']}</div>
                        <div class="price-main">${row['Price']} <span class="{cls}">{row['DayChange']:+.2f}%</span></div>
                        <div class="ext-box">
                            <span>夜盘: ${row['ExtPrice']}</span>
                            <span>{row['ExtChange']:+.2f}%</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

# 3. 重要新闻模块
st.markdown("<div class='section-header'>🔥 重要新闻 / MARKET FLASH</div>", unsafe_allow_html=True)
st.info("""
- **INTC (英特尔)**：日内大涨 11.72%，夜盘维持强势上涨 1.38%，受益于财报展望及晶圆代工新订单。
- **存储板块**：MU (美光) 日内领涨，夜盘价格保持平稳，全行业正在消化 2026 Q1 的强劲指引。
- **宏观**：格陵兰协议框架下，稀土与稀有金属（MP, ALB）夜盘出现异动，建议重点关注。
""")

st.markdown("---")
st.caption("数据来源：Yahoo Finance Real-time API | 核对时间：2026-01-22")
