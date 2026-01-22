import streamlit as st
import pandas as pd
import requests
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
    .volume {
        font-size: 0.95rem;
        color: #bbb;
    }
    .stApp {
        background-color: #0e1117;
    }
    </style>
""", unsafe_allow_html=True)

# 页面配置
st.set_page_config(
    page_title="美股隔夜热门面板",
    page_icon="📈",
    layout="wide"
)

API_KEY = "TL754C8EQKUU5XH3"

st.title("美股隔夜热门面板")
st.caption("涨幅榜 + 热门板块个股参考 · 仅供参考，非投资建议")

# 日期显示
def get_previous_trading_day():
    day = date.today() - timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day

prev_day = get_previous_trading_day()
st.subheader(f"分析日期：{prev_day.strftime('%Y-%m-%d')}")

# 静态示例数据（防止 API 失败导致白屏）
example_data = [
    {"Ticker": "NAMM", "涨幅 %": 130.61, "最新价": 2.26, "成交量": "160M"},
    {"Ticker": "USGOW", "涨幅 %": 130.39, "最新价": 1.95, "成交量": "244K"},
    {"Ticker": "PAVM", "涨幅 %": 94.67, "最新价": 12.05, "成交量": "54M"},
    {"Ticker": "LSTA", "涨幅 %": 86.57, "最新价": 4.03, "成交量": "4.9M"},
    {"Ticker": "ROMA", "涨幅 %": 66.21, "最新价": 2.41, "成交量": "5.4M"},
    {"Ticker": "MLEC", "涨幅 %": 47.61, "最新价": 6.48, "成交量": "5.6M"},
]

df_example = pd.DataFrame(example_data)

# 刷新按钮
if st.button("点击刷新实时涨幅榜（Alpha Vantage）", type="primary"):
    with st.spinner("正在拉取实时数据..."):
        try:
            url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={API_KEY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "top_gainers" not in data or not data["top_gainers"]:
                st.warning("API 未返回涨幅数据（可能非交易日或限额已用）")
                st.stop()

            gainers = data["top_gainers"][:12]
            data_list = []

            for item in gainers:
                try:
                    change_pct = float(item.get("change_percentage", "0").rstrip("%"))
                    price = float(item.get("price", 0))
                    volume = item.get("volume", "0")
                    data_list.append({
                        "Ticker": item["ticker"],
                        "涨幅 %": round(change_pct, 2),
                        "最新价": round(price, 2),
                        "成交量": volume
                    })
                except:
                    continue

            if data_list:
                df = pd.DataFrame(data_list)
                st.success("数据刷新成功！")
            else:
                df = df_example
                st.warning("实时数据为空，使用示例数据展示")

        except Exception as e:
            st.error(f"刷新失败：{str(e)}")
            st.info("使用示例数据继续展示")
            df = df_example
else:
    st.info("点击上方按钮获取最新涨幅榜（否则显示示例数据）")
    df = df_example

# 卡片式网格展示（像 TradingView 热门股卡片）
st.subheader("热门个股卡片展示")
cols = st.columns(4)  # 每行4个卡片
for i, row in df.iterrows():
    with cols[i % 4]:
        change_class = "change-up" if row["涨幅 %"] > 0 else ""
        st.markdown(f"""
            <div class="card">
                <div class="ticker">{row['Ticker']}</div>
                <div class="price">${row['最新价']:.2f}</div>
                <div class="{change_class}">{row['涨幅 %']:+.2f}%</div>
                <div class="volume">成交量: {row['成交量']}</div>
            </div>
        """, unsafe_allow_html=True)

# 表格展示（备用）
st.subheader("涨幅榜表格（含成交量排序）")
st.dataframe(
    df.sort_values("成交量", ascending=False),
    use_container_width=True,
    column_config={
        "涨幅 %": st.column_config.NumberColumn(format="%.2f%%"),
        "最新价": st.column_config.NumberColumn(format="%.2f USD")
    }
)

# 页脚
st.markdown("---")
st.caption("Powered by Streamlit + Alpha Vantage | 更新时间：" + date.today().strftime("%Y-%m-%d"))
