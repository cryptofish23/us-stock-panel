import streamlit as st
import pandas as pd
from polygon import RESTClient
from datetime import date, timedelta
from collections import Counter

# Streamlit 页面配置
st.set_page_config(
    page_title="美股隔夜热门面板",
    page_icon="📈",
    layout="wide"
)

# 你的 Polygon API Key（已填入）
API_KEY = "dPnQqWoXcn5Y1j7ItULczLCOOlq9xBw6"

# 初始化 Polygon 客户端
client = RESTClient(api_key=API_KEY)

st.title("美股隔夜热门面板")
st.caption("基于前一交易日涨幅榜 · 仅供参考，非投资建议 · 数据来源于 Polygon.io")

# 获取前一交易日日期（跳过周末）
def get_previous_trading_day():
    day = date.today() - timedelta(days=1)
    while day.weekday() >= 5:  # 5=周六, 6=周日
        day -= timedelta(days=1)
    return day

prev_day = get_previous_trading_day()
st.subheader(f"分析日期：{prev_day.strftime('%Y-%m-%d')}")

# 加载数据
with st.spinner("正在从 Polygon 获取涨幅榜数据..."):
    try:
        # 获取全市场股票快照（market_type="stocks"）
        snapshots = client.get_snapshot_all(market_type="stocks")

        gainers_data = []
        for snap in snapshots:
            if hasattr(snap, 'day') and snap.day and hasattr(snap.day, 'change_percent'):
                change_pct = snap.day.change_percent
                if change_pct > 0:  # 只保留正涨幅
                    gainers_data.append({
                        'ticker': snap.ticker,
                        'change_pct': change_pct,
                        'price': snap.last_trade.price if hasattr(snap, 'last_trade') and hasattr(snap.last_trade, 'price') else snap.day.close,
                        'volume': snap.day.volume if hasattr(snap.day, 'volume') else 0
                    })

        # 按涨幅降序排序，取前10
        gainers_sorted = sorted(gainers_data, key=lambda x: x['change_pct'], reverse=True)[:10]

        data = []
        sectors = []

        for g in gainers_sorted:
            try:
                details = client.get_ticker_details(g['ticker'])
                name = details.results.name if details and details.results else g['ticker']
                sector = details.results.sector if details and details.results.sector else "未知"
            except Exception:
                name = g['ticker']
                sector = "未知"

            sectors.append(sector)
            data.append({
                "Ticker": g['ticker'],
                "名称": name,
                "涨幅 %": round(g['change_pct'], 2),
                "最新价": round(g['price'], 2),
                "成交量": f"{g['volume']:,}",
                "板块": sector
            })

        if not data:
            st.warning("暂无涨幅数据或市场未开盘/非交易日，请稍后再试。")
            st.stop()

        df = pd.DataFrame(data)

        # 显示热门个股表格
        st.subheader("涨幅前10热门个股")
        st.dataframe(
            df.sort_values("涨幅 %", ascending=False),
            use_container_width=True,
            column_config={
                "涨幅 %": st.column_config.NumberColumn(format="%.2f%%"),
                "最新价": st.column_config.NumberColumn(format="%.2f USD")
            }
        )

        # 热门板块统计
        hot_sectors = Counter([s for s in sectors if s != "未知"]).most_common(5)
        st.subheader("热门板块（前5）")
        for sector, count in hot_sectors:
            st.write(f"• {sector}：{count} 只个股突出")

        # 简单消息区（可手动更新或未来加新闻API）
        st.subheader("今日市场要点（示例）")
        st.info("""
        - 美股三大指数隔夜反弹，道指+1.21%，纳指+1.18%。
        - 生物科技、半导体板块领涨。
        - 注意：数据实时性取决于 Polygon API，市场波动大，请自行验证。
        """)

    except Exception as e:
        st.error(f"数据获取失败：{str(e)}")
        st.info("""
        可能原因：
        1. API Key 无效或过期（请检查是否正确复制）
        2. 免费额度已用完（Polygon Basic 每天有限调用）
        3. 非交易日或市场数据未更新
        请稍后再试，或检查 key。
        """)

# 页脚
st.markdown("---")
st.caption("Powered by Streamlit + Polygon.io | Created by Jakob | 更新时间：" + date.today().strftime("%Y-%m-%d"))
