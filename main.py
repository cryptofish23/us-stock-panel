import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta

# 注入自定义 CSS 让卡片更美观（类似 TradingView）
st.markdown("""
    <style>
    .card {
        background-color: #1e1e1e;
        border-radius: 12px;
        padding: 16px;
        margin: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
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
        font-size: 1.6rem;
        font-weight: bold;
    }
    .change-down {
        color: #ef5350;
        font-size: 1.6rem;
        font-weight: bold;
    }
    .volume {
        font-size: 0.9rem;
        color: #aaa;
    }
    .stApp {
        background-color: #0e1117;
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit 配置（暗色主题支持）
st.set_page_config(page_title="美股隔夜热门面板", page_icon="📈", layout="wide")

API_KEY = "TL754C8EQKUU5XH3"

st.title("美股隔夜热门面板")
st.caption("基于前一交易日涨幅榜 · 仅供参考，非投资建议 · 数据来源于 Alpha Vantage")

# 日期
def get_previous_trading_day():
    day = date.today() - timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day

prev_day = get_previous_trading_day()
st.subheader(f"分析日期：{prev_day.strftime('%Y-%m-%d')}")

with st.spinner("加载涨幅榜数据..."):
    try:
        url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "top_gainers" not in data or not data["top_gainers"]:
            st.warning("暂无数据或限额已用，请稍后重试。")
            st.stop()

        gainers = data["top_gainers"][:12]  # 取前12个做网格

        data_list = []
        for item in gainers:
            change_pct = float(item["change_percentage"].rstrip("%"))
            volume = int(item["volume"]) if item["volume"].isdigit() else 0

            data_list.append({
                "Ticker": item["ticker"],
                "涨幅 %": round(change_pct, 2),
                "最新价": round(float(item["price"]), 2),
                "成交量": f"{volume:,}",
                "变化金额": item["change_amount"]
            })

        df = pd.DataFrame(data_list)

        # 网格布局：3列卡片
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                change_class = "change-up" if row["涨幅 %"] > 0 else "change-down"
                st.markdown(f"""
                    <div class="card">
                        <div class="ticker">{row['Ticker']}</div>
                        <div class="price">${row['最新价']:.2f}</div>
                        <div class="{change_class}">{row['涨幅 %']:+.2f}%</div>
                        <div class="volume">成交量: {row['成交量']}</div>
                    </div>
                """, unsafe_allow_html=True)

                # 迷你线图占位（未来可加真实 mini chart）
                st.caption("迷你走势（占位）")
                st.line_chart([1, row["涨幅 %"]/10 + 1, row["涨幅 %"]/5 + 1], height=80, use_container_width=True)

        # 高成交量区（资金流入代理）
        st.subheader("资金流入活跃个股（成交量前5）")
        high_vol = df.sort_values("成交量", ascending=False).head(5)
        st.dataframe(high_vol, use_container_width=True)

        st.subheader("市场要点（示例）")
        st.info("昨晚存储/半导体板块大涨，MU/SNDK/INTC 等资金流入明显。")

    except Exception as e:
        st.error(f"错误：{str(e)}")
        st.info("检查 API key 或限额（Alpha Vantage 免费每天500次）。")

st.markdown("---")
st.caption("Powered by Streamlit + Alpha Vantage | 更新：" + date.today().strftime("%Y-%m-%d"))
