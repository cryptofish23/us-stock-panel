import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

# 自定义 CSS 让卡片看起来像 TradingView 风格
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
    }
    </style>
""", unsafe_allow_html=True)

# 页面配置
st.set_page_config(
    page_title="美股隔夜热门面板",
    page_icon="📈",
    layout="wide"
)

st.title("美股隔夜热门面板")
st.caption("三大股指 + 热门板块个股 + 涨幅榜 · 仅供参考，非投资建议")

# 日期
def get_previous_trading_day():
    day = date.today() - timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day

prev_day = get_previous_trading_day()
prev_day_str = prev_day.strftime('%Y-%m-%d')
st.subheader(f"分析日期：{prev_day_str}")

# 三大股指
with st.spinner("加载三大股指数据..."):
    indices = ['^DJI', '^GSPC', '^IXIC']  # Dow, S&P500, Nasdaq
    indices_data = yf.download(indices, start=prev_day_str, end=prev_day_str)
    df_indices = pd.DataFrame({
        '指数': ['道指 (DJI)', '标普500 (GSPC)', '纳指 (IXIC)'],
        '收盘价': indices_data['Close'].iloc[0].round(2),
        '涨幅 %': ((indices_data['Close'] - indices_data['Open']) / indices_data['Open'] * 100).iloc[0].round(2),
        '成交量': indices_data['Volume'].iloc[0].astype(int).apply(lambda x: f"{x:,}")
    })

    st.markdown("<div class='section-header'>美国三大股指涨跌幅</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, row in df_indices.iterrows():
        with cols[i]:
            change_class = "change-up" if row["涨幅 %"] > 0 else "change-down"
            st.markdown(f"""
                <div class="card">
                    <div class="ticker">{row['指数']}</div>
                    <div class="price">${row['收盘价']:.2f}</div>
                    <div class="{change_class}">{row['涨幅 %']:+.2f}%</div>
                    <div class="volume">成交量: {row['成交量']}</div>
                </div>
            """, unsafe_allow_html=True)

# 热门板块
plates = {
    '芯片半导体': ['NVDA', 'TSM', 'INTC', 'AMD', 'QCOM', 'ASML', 'AVGO', 'TXN'],
    '存储': ['MU', 'WDC', 'STX', 'SNDK'],
    '光模块': ['LITE', 'CIEN', 'AAOI', 'IIVI'],
    '无人机军事': ['KTOS', 'AVAV', 'LMT', 'NOC'],
    '加密': ['MSTR', 'HOOD', 'COIN', 'RIOT', 'BITO'],
    '云数据中心': ['IREN', 'APLD', 'CIFR', 'EQIX', 'DLR'],
    '储能': ['TSLA', 'ENPH', 'SEDG', 'FSLR'],
    '贵金属': ['GOLD', 'GDX', 'SLV', 'PAAS'],
    '稀有金属': ['MP', 'ALB', 'SQM', 'LAC']
}

for plate, tickers in plates.items():
    with st.spinner(f"加载 {plate} 板块数据..."):
        data = yf.download(tickers, start=prev_day_str, end=prev_day_str)
        df_plate = pd.DataFrame({
            'Ticker': data['Close'].columns,
            '收盘价': data['Close'].iloc[0].round(2),
            '涨幅 %': ((data['Close'] - data['Open']) / data['Open'] * 100).iloc[0].round(2),
            '成交量': data['Volume'].iloc[0].astype(int).apply(lambda x: f"{x:,}")
        }).dropna()

        if df_plate.empty:
            st.warning(f"{plate} 板块暂无数据。")
            continue

        st.markdown(f"<div class='section-header'>{plate} 板块个股涨幅</div>", unsafe_allow_html=True)
        cols = st.columns(4)
        for i, row in df_plate.iterrows():
            with cols[i % 4]:
                change_class = "change-up" if row["涨幅 %"] > 0 else "change-down"
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker">{row['Ticker']}</div>
                        <div class="price">${row['收盘价']:.2f}</div>
                        <div class="{change_class}">{row['涨幅 %']:+.2f}%</div>
                        <div class="volume">成交量: {row['成交量']}</div>
                    </div>
                """, unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.caption("Powered by Streamlit + yfinance | 更新时间：" + date.today().strftime("%Y-%m-%d"))
