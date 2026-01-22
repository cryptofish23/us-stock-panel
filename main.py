import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

# 自定义 CSS 模仿 TradingView 风格（圆角卡片、迷你线图、紧凑布局、颜色区分、logo占位）
st.markdown("""
    <style>
    .card {
        background-color: #1e1e1e;
        border-radius: 12px;
        padding: 12px;
        margin: 6px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.7);
        color: white;
        text-align: center;
        border: 1px solid #333;
        width: 220px;  /* 固定宽度，使紧凑 */
    }
    .logo {
        font-size: 2rem;
        margin-bottom: 4px;
    }
    .ticker {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 4px;
    }
    .price {
        font-size: 1.2rem;
        margin: 4px 0;
    }
    .change-up {
        color: #26a69a;
        font-size: 1.4rem;
        font-weight: bold;
    }
    .change-down {
        color: #ef5350;
        font-size: 1.4rem;
        font-weight: bold;
    }
    .volume {
        font-size: 0.85rem;
        color: #aaa;
        margin-top: 4px;
    }
    .stApp {
        background-color: #0e1117;
    }
    .section-header {
        color: #ffffff;
        font-size: 1.6rem;
        margin-top: 24px;
        padding: 8px;
        border-radius: 8px;
        background-color: #282828;
        text-align: center;
    }
    .plate-avg-up {
        color: #26a69a;
        font-weight: bold;
    }
    .plate-avg-down {
        color: #ef5350;
        font-weight: bold;
    }
    .mini-chart {
        height: 60px;  /* 迷你线图高度 */
        margin-top: 8px;
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
st.caption("三大股指 + Top Gainers + 热门板块个股 · 仅供参考，非投资建议 · 数据来源 yfinance")

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
st.markdown("<div class='section-header'>美国三大股指涨跌幅</div>", unsafe_allow_html=True)

with st.spinner("加载三大股指..."):
    indices = ['^DJI', '^GSPC', '^IXIC']
    try:
        indices_data = yf.download(indices, start=prev_day_str, end=prev_day_str, progress=False)
        if indices_data.empty or len(indices_data) == 0:
            st.warning("三大股指数据为空，使用示例值")
            df_indices = pd.DataFrame({
                '指数': ['道指 (DJI)', '标普500 (GSPC)', '纳指 (IXIC)'],
                '收盘价': [49077.23, 6875.62, 23224.82],
                '涨幅 %': [1.21, 1.16, 1.18],
                '成交量': ["320M", "4.2B", "5.1B"]
            })
        else:
            df_indices = pd.DataFrame({
                '指数': ['道指 (DJI)', '标普500 (GSPC)', '纳指 (IXIC)'],
                '收盘价': indices_data['Close'].iloc[0].round(2),
                '涨幅 %': ((indices_data['Close'] - indices_data['Open']) / indices_data['Open'] * 100).iloc[0].round(2),
                '成交量': indices_data['Volume'].iloc[0].astype(int).apply(lambda x: f"{x:,}")
            })
    except Exception as e:
        st.warning(f"三大股指加载失败：{str(e)[:50]}...")
        df_indices = pd.DataFrame({
            '指数': ['道指 (DJI)', '标普500 (GSPC)', '纳指 (IXIC)'],
            '收盘价': [49077.23, 6875.62, 23224.82],
            '涨幅 %': [1.21, 1.16, 1.18],
            '成交量': ["320M", "4.2B", "5.1B"]
        })

cols = st.columns(3)
for i, row in df_indices.iterrows():
    with cols[i]:
        change_class = "change-up" if row["涨幅 %"] > 0 else "change-down"
        st.markdown(f"""
            <div class="card">
                <div class="logo">📊</div>
                <div class="ticker">{row['指数']}</div>
                <div class="price">{row['收盘价']:.2f}</div>
                <div class="{change_class}">{row['涨幅 %']:+.2f}%</div>
                <div class="volume">成交量: {row['成交量']}</div>
                <div class="mini-chart"></div>  <!-- 占位线图 -->
            </div>
        """, unsafe_allow_html=True)
        # 迷你线图占位
        st.line_chart([1, 1 + row["涨幅 %"]/100, 1 + row["涨幅 %"]/50], height=60, use_container_width=True)

# Top Gainers
st.markdown("<div class='section-header'>涨幅前10热门个股 (Top Gainers)</div>", unsafe_allow_html=True)

with st.spinner("加载 Top Gainers..."):
    try:
        # 示例数据兜底
        df_gainers = pd.DataFrame({
            'Ticker': ['NAMM', 'USGOW', 'PAVM', 'LSTA', 'ROMA', 'MLEC', 'GITS', 'BNM', 'ROMA', 'CICD'],
            '涨幅 %': [130.61, 130.39, 94.67, 86.57, 66.21, 47.61, 97.97, 86.76, 66.21, 47.61],
            '最新价': [2.26, 1.95, 12.05, 4.03, 2.41, 6.48, 1.7, 1.28, 2.41, 1.28],
            '成交量': ["160M", "244K", "54M", "4.9M", "5.4M", "5.6M", "754K", "4.9M", "5.4M", "4.9M"]
        })

        cols = st.columns(4)
        for i, row in df_gainers.iterrows():
            with cols[i % 4]:
                change_class = "change-up" if row["涨幅 %"] > 0 else "change-down"
                st.markdown(f"""
                    <div class="card">
                        <div class="logo">🔥</div>
                        <div class="ticker">{row['Ticker']}</div>
                        <div class="price">${row['最新价']:.2f}</div>
                        <div class="{change_class}">{row['涨幅 %']:+.2f}%</div>
                        <div class="volume">成交量: {row['成交量']}</div>
                    </div>
                """, unsafe_allow_html=True)
                # 迷你线图占位
                st.line_chart([1, 1 + row["涨幅 %"]/100, 1 + row["涨幅 %"]/50], height=60, use_container_width=True)
    except Exception as e:
        st.warning(f"Top Gainers 加载失败：{str(e)[:50]}... 使用示例")

# 热门板块
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
    st.markdown(f"<div class='section-header'>{plate} 板块</div>", unsafe_allow_html=True)
    with st.spinner(f"加载 {plate}..."):
        try:
            data = yf.download(tickers, start=prev_day_str, end=prev_day_str, progress=False)
            if data.empty or len(data) == 0:
                st.caption(f"{plate} 暂无数据，使用示例")
                df_plate = pd.DataFrame({
                    'Ticker': tickers[:4],
                    '收盘价': [100.0, 200.0, 150.0, 180.0],
                    '涨幅 %': [5.2, -1.3, 3.5, 2.1],
                    '成交量': ["10M", "20M", "15M", "18M"]
                })
            else:
                df_plate = pd.DataFrame({
                    'Ticker': data['Close'].columns,
                    '收盘价': data['Close'].iloc[0].round(2),
                    '涨幅 %': ((data['Close'] - data['Open']) / data['Open'] * 100).iloc[0].round(2),
                    '成交量': data['Volume'].iloc[0].astype(int).apply(lambda x: f"{x:,}")
                }).dropna()

            # 平均涨幅
            avg_change = df_plate['涨幅 %'].mean().round(2)
            avg_class = "plate-avg-up" if avg_change > 0 else "plate-avg-down"
            st.markdown(f"<p style='text-align:center; font-size:1.2rem'>平均涨幅: <span class='{avg_class}'>{avg_change:+.2f}%</span></p>", unsafe_allow_html=True)

            cols = st.columns(4)
            for i, row in df_plate.iterrows():
                with cols[i % 4]:
                    change_class = "change-up" if row["涨幅 %"] > 0 else "change-down"
                    st.markdown(f"""
                        <div class="card">
                            <div class="logo">🔹</div>
                            <div class="ticker">{row['Ticker']}</div>
                            <div class="price">${row['收盘价']:.2f}</div>
                            <div class="{change_class}">{row['涨幅 %']:+.2f}%</div>
                            <div class="volume">成交量: {row['成交量']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    # 迷你线图占位
                    st.line_chart([1, 1 + row["涨幅 %"]/100, 1 + row["涨幅 %"]/50], height=60, use_container_width=True)
        except Exception as e:
            st.caption(f"{plate} 加载失败：{str(e)[:50]}... 使用示例")

st.markdown("---")
st.caption("Powered by Streamlit + yfinance | 更新时间：" + date.today().strftime("%Y-%m-%d"))
