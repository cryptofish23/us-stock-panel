import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

# CSS 美化（保持 TradingView 风格）
st.markdown("""
    <style>
    .card {
        background-color: #1e1e1e;
        border-radius: 12px;
        padding: 16px;
        margin: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.6);
        color: white;
        text-align: center;
        border: 1px solid #333;
    }
    .ticker { font-size: 1.8rem; font-weight: bold; margin-bottom: 8px; }
    .price { font-size: 1.4rem; margin: 8px 0; }
    .change-up { color: #26a69a; font-size: 1.8rem; font-weight: bold; }
    .change-down { color: #ef5350; font-size: 1.8rem; font-weight: bold; }
    .volume { font-size: 0.95rem; color: #bbb; }
    .stApp { background-color: #0e1117; }
    .section-header { color: #ffffff; font-size: 1.6rem; margin: 24px 0 12px; text-align: center; background-color: #282828; padding: 8px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="美股隔夜热门面板", page_icon="📈", layout="wide")

st.title("美股隔夜热门面板")
st.caption("三大股指 + 热门板块个股 · 仅供参考，非投资建议")

# 日期
def get_previous_trading_day():
    day = date.today() - timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day

prev_day = get_previous_trading_day()
prev_day_str = prev_day.strftime('%Y-%m-%d')
st.subheader(f"分析日期：{prev_day_str}")

# 三大股指（用示例兜底）
st.markdown("<div class='section-header'>美国三大股指涨跌幅</div>", unsafe_allow_html=True)

try:
    indices = ['^DJI', '^GSPC', '^IXIC']
    indices_data = yf.download(indices, start=prev_day_str, end=prev_day_str, progress=False)
    if indices_data.empty:
        raise ValueError("数据为空")
    df_indices = pd.DataFrame({
        '指数': ['道指', '标普500', '纳指'],
        '收盘价': indices_data['Close'].iloc[0].round(2),
        '涨幅 %': ((indices_data['Close'] - indices_data['Open']) / indices_data['Open'] * 100).iloc[0].round(2),
        '成交量': indices_data['Volume'].iloc[0].astype(int).apply(lambda x: f"{x:,}")
    })
except Exception:
    st.caption("三大股指数据加载失败，使用示例")
    df_indices = pd.DataFrame({
        '指数': ['道指', '标普500', '纳指'],
        '收盘价': [49077.23, 6875.62, 23224.82],
        '涨幅 %': [1.21, 1.16, 1.18],
        '成交量': ["未知", "未知", "未知"]
    })

cols = st.columns(3)
for i, row in df_indices.iterrows():
    with cols[i]:
        change_class = "change-up" if row["涨幅 %"] > 0 else "change-down"
        st.markdown(f"""
            <div class="card">
                <div class="ticker">{row['指数']}</div>
                <div class="price">${row['收盘价']}</div>
                <div class="{change_class}">{row['涨幅 %']:+.2f}%</div>
                <div class="volume">成交量: {row['成交量']}</div>
            </div>
        """, unsafe_allow_html=True)

# Top Gainers（静态示例，避免 API 问题）
st.markdown("<div class='section-header'>涨幅前10热门个股</div>", unsafe_allow_html=True)

gainers_data = [
    {"Ticker": "NAMM", "涨幅 %": 130.61, "最新价": 2.26, "成交量": "160M"},
    {"Ticker": "USGOW", "涨幅 %": 130.39, "最新价": 1.95, "成交量": "244K"},
    {"Ticker": "PAVM", "涨幅 %": 94.67, "最新价": 12.05, "成交量": "54M"},
    {"Ticker": "LSTA", "涨幅 %": 86.57, "最新价": 4.03, "成交量": "4.9M"},
    {"Ticker": "ROMA", "涨幅 %": 66.21, "最新价": 2.41, "成交量": "5.4M"},
    {"Ticker": "MLEC", "涨幅 %": 47.61, "最新价": 6.48, "成交量": "5.6M"},
    {"Ticker": "GITS", "涨幅 %": 97.97, "最新价": 1.70, "成交量": "78M"},
    {"Ticker": "SLGR", "涨幅 %": 47.20, "最新价": 1.84, "成交量": "80M"},
    {"Ticker": "MODC", "涨幅 %": 47.61, "最新价": 6.48, "成交量": "5.6M"},
    {"Ticker": "BRAN", "涨幅 %": 41.46, "最新价": 8.70, "成交量": "未知"}
]

df_gainers = pd.DataFrame(gainers_data)

cols = st.columns(4)
for i, row in df_gainers.iterrows():
    with cols[i % 4]:
        change_class = "change-up"
        st.markdown(f"""
            <div class="card">
                <div class="ticker">{row['Ticker']}</div>
                <div class="price">${row['最新价']:.2f}</div>
                <div class="{change_class}">{row['涨幅 %']:+.2f}%</div>
                <div class="volume">成交量: {row['成交量']}</div>
            </div>
        """, unsafe_allow_html=True)

# 热门板块（简化 + 示例兜底）
plates = {
    '芯片/半导体': ['NVDA', 'TSM', 'INTC', 'AMD'],
    '存储': ['MU', 'WDC', 'STX'],
    '光模块': ['LITE', 'CIEN'],
    '无人机/军事': ['AVAV', 'LMT'],
    '加密货币': ['MSTR', 'COIN', 'HOOD'],
    '云数据中心': ['IREN', 'APLD', 'CIFR'],
    '储能': ['TSLA', 'ENPH'],
    '贵金属': ['GOLD', 'GDX'],
    '稀有金属': ['ALB', 'SQM']
}

for plate, tickers in plates.items():
    st.markdown(f"<div class='section-header'>{plate} 板块</div>", unsafe_allow_html=True)
    try:
        data = yf.download(tickers, start=prev_day_str, end=prev_day_str, progress=False)
        if data.empty:
            raise ValueError("空数据")
        df_plate = pd.DataFrame({
            'Ticker': data['Close'].columns,
            '涨幅 %': ((data['Close'] - data['Open']) / data['Open'] * 100).iloc[0].round(2),
            '最新价': data['Close'].iloc[0].round(2),
            '成交量': data['Volume'].iloc[0].astype(int).apply(lambda x: f"{x:,}")
        })
    except:
        st.caption(f"{plate} 暂无数据，使用示例")
        df_plate = pd.DataFrame({
            'Ticker': tickers[:3],
            '涨幅 %': [5.2, -1.3, 3.5],
            '最新价': [100.0, 200.0, 150.0],
            '成交量': ["10M", "20M", "15M"]
        })

    cols = st.columns(4)
    for i, row in df_plate.iterrows():
        with cols[i % 4]:
            change_class = "change-up" if row["涨幅 %"] > 0 else "change-down"
            st.markdown(f"""
                <div class="card">
                    <div class="ticker">{row['Ticker']}</div>
                    <div class="price">${row['最新价']:.2f}</div>
                    <div class="{change_class}">{row['涨幅 %']:+.2f}%</div>
                    <div class="volume">成交量: {row['成交量']}</div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Powered by Streamlit + yfinance | 更新时间：" + date.today().strftime("%Y-%m-%d"))
