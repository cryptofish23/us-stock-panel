import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. 页面配置与 CSS 样式注入 (解决白边关键) ---
st.set_page_config(layout="wide", page_title="Financial Dashboard")

st.markdown("""
    <style>
    /* 移除 Streamlit 默认的 padding */
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    
    /* 消除组件之间的间距和白边 */
    [data-testid="stVerticalBlock"] > div {
        gap: 0rem !important;
    }
    
    /* 自定义指数卡片样式 */
    .index-card {
        background-color: #1a1e2c;
        border: 1px solid #2d313e;
        border-radius: 8px 8px 0 0;
        padding: 15px;
        color: white;
        margin-bottom: 0px;
    }
    
    /* 图表容器 - 紧贴卡片 */
    .chart-container {
        background-color: #1a1e2c;
        border: 1px solid #2d313e;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 0px;
        margin-top: -1px;
        overflow: hidden;
    }
    
    /* 隐藏图表的交互工具栏 */
    .stPlotlyChart { margin-bottom: -10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 数据获取函数 ---
@st.cache_data(ttl=60)
def get_stock_data(symbols):
    data_list = []
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            # 获取最近2天的数据计算涨跌
            hist = ticker.history(period="5d", interval="1h")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change = ((current_price - prev_close) / prev_close) * 100
                
                # 获取历史价格数组用于 Sparkline
                spark_data = hist['Close'].tolist()
                
                data_list.append({
                    "symbol": sym,
                    "price": f"{current_price:,.2f}",
                    "change": round(change, 2),
                    "history": spark_data
                })
        except Exception as e:
            print(f"Error fetching {sym}: {e}")
    return data_list

# --- 3. 渲染逻辑 ---
def render_dashboard():
    # 定义需要展示的符号
    indices_symbols = ["^DJI", "^GSPC", "^IXIC", "NQ=F"]
    stock_symbols = ["AAPL", "TSLA", "NVDA", "MSFT"]

    # 获取数据
    indices_data = get_stock_data(indices_symbols)
    
    st.subheader("Market Indices (核心股指)")
    
    # 渲染指数 (第一排)
    cols = st.columns(len(indices_data))
    for i, data in enumerate(indices_data):
        with cols[i]:
            color = "#10b981" if data['change'] >= 0 else "#f43f5e"
            # 顶部卡片
            st.markdown(f"""
                <div class="index-card">
                    <div style="font-size: 1.1em; font-weight: bold;">{data['symbol']}</div>
                    <div style="margin-top: 8px;">
                        <span style="font-size: 1.4em; font-weight: bold;">${data['price']}</span>
                        <span style="color: {color}; margin-left: 8px;">{'+' if data['change'] > 0 else ''}{data['change']}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # 紧贴下方的 Sparkline (使用 st.line_chart 简化实现)
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                # 构造极简 DataFrame 以移除坐标轴感官
                chart_df = pd.DataFrame(data['history'], columns=['price'])
                st.line_chart(chart_df, height=60, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    
    # 渲染个股 (第二排 - 同样的集成逻辑)
    st.subheader("Watchlist (自选个股)")
    stocks_data = get_stock_data(stock_symbols)
    s_cols = st.columns(len(stocks_data))
    for j, s_data in enumerate(stocks_data):
        with s_cols[j]:
            s_color = "#10b981" if s_data['change'] >= 0 else "#f43f5e"
            st.markdown(f"""
                <div class="index-card">
                    <div style="font-size: 1.1em; font-weight: bold;">{s_data['symbol']}</div>
                    <div style="margin-top: 8px;">
                        <span style="font-size: 1.4em; font-weight: bold;">${s_data['price']}</span>
                        <span style="color: {s_color}; margin-left: 8px;">{'+' if s_data['change'] > 0 else ''}{s_data['change']}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.line_chart(pd.DataFrame(s_data['history']), height=50, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    render_dashboard()
