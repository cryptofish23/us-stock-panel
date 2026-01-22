import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta

# Streamlit 页面配置
st.set_page_config(
    page_title="美股隔夜热门面板",
    page_icon="📈",
    layout="wide"
)

# 你的 Alpha Vantage API Key（免费，已填入）
API_KEY = "TL754C8EQKUU5XH3"

st.title("美股隔夜热门面板")
st.caption("基于前一交易日涨幅榜 · 仅供参考，非投资建议 · 数据来源于 Alpha Vantage")

# 获取前一交易日日期（跳过周末）
def get_previous_trading_day():
    day = date.today() - timedelta(days=1)
    while day.weekday() >= 5:  # 5=周六, 6=周日
        day -= timedelta(days=1)
    return day

prev_day = get_previous_trading_day()
st.subheader(f"分析日期：{prev_day.strftime('%Y-%m-%d')}")

# 加载数据
with st.spinner("正在从 Alpha Vantage 获取涨幅榜数据..."):
    try:
        # Alpha Vantage TOP_GAINERS_LOSERS 端点
        url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # 抛出 HTTP 错误
        data = response.json()

        # 检查是否返回了 gainers 数据
        if "top_gainers" not in data or not data["top_gainers"]:
            st.warning("暂无涨幅数据或 API 返回为空（可能非交易日或限额已用完），请稍后再试。")
            st.stop()

        # 取 top gainers 前10
        gainers = data["top_gainers"][:10]

        data_list = []
        for item in gainers:
            change_pct = float(item["change_percentage"].rstrip("%"))  # 去掉 % 转 float
            volume = int(item["volume"]) if item["volume"].isdigit() else 0

            data_list.append({
                "Ticker": item["ticker"],
                "名称": item["ticker"],  # Alpha Vantage 不直接给名称，可后续加
                "涨幅 %": round(change_pct, 2),
                "最新价": round(float(item["price"]), 2),
                "成交量": f"{volume:,}",
                "变化金额": item["change_amount"]
            })

        df = pd.DataFrame(data_list)

        # 显示热门个股表格（按涨幅排序）
        st.subheader("涨幅前10热门个股（Top Gainers）")
        st.dataframe(
            df.sort_values("涨幅 %", ascending=False),
            use_container_width=True,
            column_config={
                "涨幅 %": st.column_config.NumberColumn(format="%.2f%%"),
                "最新价": st.column_config.NumberColumn(format="%.2f USD"),
                "成交量": st.column_config.TextColumn()
            }
        )

        # 高成交量个股（资金流入代理）
        st.subheader("资金流入活跃个股（按成交量排序，前5）")
        high_volume_df = df.sort_values("成交量", ascending=False).head(5)
        st.dataframe(high_volume_df, use_container_width=True)

        # 简单消息区（可手动更新或未来加新闻API）
        st.subheader("今日市场要点（示例）")
        st.info("""
        - 美股三大指数隔夜反弹，道指+1.21%，纳指+1.18%。
        - 生物科技、半导体/存储板块领涨（MU、SNDK、INTC 等高成交）。
        - 注意：数据实时性取决于 Alpha Vantage，市场波动大，请自行验证。
        - 热门板块个股参考：存储/半导体（MU +6.54%, SNDK +10.63%, WDC 类似）资金流入明显。
        """)

    except Exception as e:
        st.error(f"数据获取失败：{str(e)}")
        st.info("""
        可能原因：
        1. API Key 无效或过期（请确认是否正确复制）
        2. 免费额度已用完（Alpha Vantage 每天 500 calls，5 calls/min）
        3. 网络问题或市场非交易日/数据未更新
        请稍后再试，或检查 https://www.alphavantage.co/documentation/
        """)

# 页脚
st.markdown("---")
st.caption("Powered by Streamlit + Alpha Vantage | Created by Jakob | 更新时间：" + date.today().strftime("%Y-%m-%d"))
