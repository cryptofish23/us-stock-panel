import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

# 自定义 CSS（保持美观卡片风格）
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
    .ticker {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .price {
        font-size: 1.4rem;
        margin: 8px 0;
    }
    .change-up {
        color: #26a69a;
        font-size: 1.8rem;
        font-weight: bold;
    }
    .change-down {
        color: #ef5350;
        font-size: 1.8rem;
        font-weight: bold;
    }
    .volume {
        font-size: 0.95rem;
        color: #bbb;
    }
    .stApp {
        background-color: #0e1117;
    }
    .section-header {
        color: #ffffff;
        font-size: 1.5rem;
        margin-top: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="美股隔夜热门面板", page_icon="📈", layout="wide")

st.title("美股隔夜热门面板")
st.caption("三大股指 + 热门板块个股涨幅 · 仅供参考，非投资建议")

# 日期函数
def get_previous_trading_day():
    day = date.today() - timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day

prev_day = get_previous_trading_day()
prev_day_str = prev_day.strftime('%Y-%m-%d')
st.subheader(f"分析日期：{prev_day_str}（若为空，使用示例数据）")

# 三大股指
st.markdown("<div class='section-header'>美国三大股指涨跌幅</div>", unsafe_allow_html=True)

with st.spinner("加载三大股指..."):
    indices = ['^DJI', '^GSPC', '^IXIC']  # Dow, S&P500, Nasdaq
    try:
        indices_data = yf.download(indices, start=prev_day_str, end=prev_day_str, progress=False, group_by='ticker')
        
        if indices_data.empty or indices_data.shape[0] == 0:
            st.warning("三大股指数据为空（可能非交易日或数据延迟），使用示例值。")
            df_indices = pd.DataFrame({
                '指数': ['道指 (DJI)', '标普500 (GSPC)', '纳指 (IXIC)'],
                '收盘价': [49077.23, 6875.62, 23224.82],
                '涨幅 %': [1.21, 1.16, 1.18],
                '成交量': ["未知", "未知", "未知"]
            })
        else:
            df_indices = pd.DataFrame({
                '指数': ['道指 (DJI)', '标普500 (GSPC)', '纳指 (IXIC)'],
                '收盘价': indices_data['Close'].iloc[0].round(2),
                '涨幅 %': ((indices_data['Close'] - indices_data['Open']) / indices_data['Open'] * 100).iloc[0].round(2),
                '成交量': indices_data['Volume'].iloc[0].astype(int).apply(lambda x: f"{x:,}")
            })
    except Exception as e:
        st.error(f"三大股指加载失败：{str(e)}")
        df_indices = pd.DataFrame({
            '指数': ['道指 (DJI)', '标普500 (GSPC)', '纳指 (IXIC)'],
            '收盘价': ["N/A", "N/A", "N/A"],
            '涨幅 %': ["N/A", "N/A", "N/A"],
            '成交量': ["N/A", "N/A", "N/A"]
        })

cols = st.columns(3)
for i, row in df_indices.iterrows():
    with cols[i]:
        change_class = "change-up" if isinstance(row["涨幅 %"], (int, float)) and row["涨幅 %"] > 0 else "change-down" if isinstance(row["涨幅 %"], (int, float)) else ""
        st.markdown(f"""
            <div class="card">
                <div class="ticker">{row['指数']}</div>
                <div class="price">{row['收盘价'] if row['收盘价'] != 'N/A' else 'N/A'}</div>
                <div class="{change_class}">{row['涨幅 %'] if row['涨幅 %'] != 'N/A' else 'N/A'}</div>
                <div class="volume">成交量: {row['成交量']}</div>
            </div>
        """, unsafe_allow_html=True)

# 热门板块（你的需求）
plates = {
    '芯片/半导体': ['NVDA', 'TSM', 'INTC', 'AMD', 'QCOM', 'ASML', 'AVGO', 'TXN'],
    '存储': ['MU', 'WDC', 'STX'],
    '光模块': ['LITE', 'CIEN', 'AAOI'],
    '无人机/军事': ['KTOS', 'AVAV', 'LMT', 'NOC'],
    '加密货币': ['MSTR', 'HOOD', 'COIN', 'RIOT'],
    '云数据中心': ['IREN', 'APLD', 'CIFR', 'EQIX', 'DLR'],
    '储能': ['TSLA', 'ENPH', 'SEDG', 'FSLR'],
    '贵金属': ['GOLD', 'GDX', 'SLV'],
    '稀有金属': ['MP', 'ALB', 'SQM']
}

for plate, tickers in plates.items():
    st.markdown(f"<div class='section-header'>{plate} 板块个股涨幅</div>", unsafe_allow_html=True)
    with st.spinner(f"加载 {plate}..."):
        try:
            data = yf.download(tickers, start=prev_day_str, end=prev_day_str, progress=False, group_by='ticker')
            
            if data.empty or data.shape[0] == 0:
                st.caption(f"{plate} 暂无数据")
                continue

            df_plate = pd.DataFrame({
                'Ticker': data.columns.levels[1] if data.columns.nlevels > 1 else data.columns,
                '收盘价': data['Close'].iloc[0].round(2) if 'Close' in data else pd.Series(["N/A"] * len(tickers)),
                '涨幅 %': ((data['Close'] - data['Open']) / data['Open'] * 100).iloc[0].round(2) if 'Close' in data and 'Open' in data else pd.Series(["N/A"] * len(tickers)),
                '成交量': data['Volume'].iloc[0].astype(int).apply(lambda x: f"{x:,}") if 'Volume' in data else pd.Series(["N/A"] * len(tickers))
            }).dropna(how='all')

            cols = st.columns(4)
            for i, row in df_plate.iterrows():
                with cols[i % 4]:
                    change_class = "change-up" if isinstance(row["涨幅 %"], (int, float)) and row["涨幅 %"] > 0 else "change-down" if isinstance(row["涨幅 %"], (int, float)) else ""
                    st.markdown(f"""
                        <div class="card">
                            <div class="ticker">{row['Ticker']}</div>
                            <div class="price">{row['收盘价'] if row['收盘价'] != 'N/A' else 'N/A'}</div>
                            <div class="{change_class}">{row['涨幅 %'] if row['涨幅 %'] != 'N/A' else 'N/A'}</div>
                            <div class="volume">成交量: {row['成交量']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.caption(f"{plate} 加载失败：{str(e)[:50]}...")

st.markdown("---")
st.caption("Powered by Streamlit + yfinance | 更新时间：" + date.today().strftime("%Y-%m-%d"))
