import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import plotly.graph_objects as go

# --- 1. 页面配置 ---
st.set_page_config(page_title="PRO 隔夜美股热力中心", page_icon="⚡", layout="wide")

# --- 2. 深度定制 CSS (彻底消除白边) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; } /* 核心：消除组件间隙 */
    
    .main .block-container { padding: 1rem 1.5rem; }
    
    /* 卡片上半部分 */
    .card-top {
        background: #161b26;
        border: 1px solid #2d3648;
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        padding: 12px 12px 5px 12px;
        margin-top: 10px;
    }
    
    /* 图表容器下半部分 */
    .card-bottom {
        background: #161b26;
        border: 1px solid #2d3648;
        border-top: none;
        border-radius: 0 0 6px 6px;
        padding: 0px;
        margin-bottom: 5px;
        overflow: hidden;
    }

    .ticker-name { font-size: 1rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.75rem; color: #9ca3af; }
    .price-main { font-size: 1.25rem; color: #ffffff; font-family: 'Monaco', monospace; margin: 4px 0; font-weight: bold; }
    .change-up { color: #08d38d; font-weight: bold; }
    .change-down { color: #f23645; font-weight: bold; }
    
    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc; padding: 6px 12px; border-left: 4px solid #2962ff;
        font-size: 0.9rem; margin: 20px 0 10px 0; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 实时数据与趋势抓取 ---
@st.cache_data(ttl=30)
def get_market_data_with_spark(tickers):
    data_map = {}
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            # 抓取 5 天内 1 小时级别数据，确保覆盖夜盘和最新价
            df = stock.history(period="5d", interval="1h")
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
                chg = ((current_price - prev_close) / prev_close) * 100
                history = df['Close'].tail(24).tolist() # 取最近 24 个数据点点做趋势图
                data_map[t] = {
                    'price': round(current_price, 2),
                    'change': round(chg, 2),
                    'history': history
                }
        except:
            continue
    return data_map

# --- 4. 迷你图渲染函数 (Plotly 极简版) ---
def render_sparkline(data, color):
    fig = go.Figure(data=go.Scatter(
        y=data, mode='lines', 
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f"rgba({13 if color=='#08d38d' else 242}, {211 if color=='#08d38d' else 54}, {141 if color=='#08d38d' else 69}, 0.1)"
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=40,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    return fig

# --- 5. 渲染页面逻辑 ---

# 基础信息映射
NAME_MAP = {
    '^DJI': '道琼斯', '^GSPC': '标普500', '^IXIC': '纳斯达克', 'NQ=F': '纳指期货', 'ES=F': '标普期货',
    'NVDA': '英伟达', 'TSM': '台积电', 'INTC': '英特尔', 'AMD': '超威半导体', 'AVGO': '博通', 'ARM': '安谋',
    'MU': '美光科技', 'WDC': '西部数据', 'STX': '希捷', 'LITE': 'Lumentum', 'CIEN': 'Ciena', 'AAOI': '应用光电'
}

st.title("⚡ 隔夜美股热力中心 (实时趋势版)")

# 指数板块
st.markdown("<div class='section-header'>MARKET INDICES (核心股指)</div>", unsafe_allow_html=True)
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
idx_data = get_market_data_with_spark(idx_list)

cols = st.columns(len(idx_list))
for i, t in enumerate(idx_list):
    with cols[i]:
        if t in idx_data:
            d = idx_data[t]
            cls = "change-up" if d['change'] > 0 else "change-down"
            color_hex = "#08d38d" if d['change'] > 0 else "#f23645"
            
            # 渲染卡片文字
            st.markdown(f"""
                <div class="card-top">
                    <div class="ticker-name">{t} <span class="chinese-name">{NAME_MAP.get(t, '')}</span></div>
                    <div class="price-main">${d['price']} <span class="{cls}">{d['change']:+.2f}%</span></div>
                </div>
            """, unsafe_allow_html=True)
            
            # 渲染无缝集成的 Sparkline
            st.markdown('<div class="card-bottom">', unsafe_allow_html=True)
            st.plotly_chart(render_sparkline(d['history'], color_hex), use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

# 个股板块 (以芯片为例展示集成效果)
PLATES = {
    '芯片/AI 核心': ['NVDA', 'TSM', 'INTC', 'AMD', 'AVGO', 'ARM'],
    '存储/光模块': ['MU', 'WDC', 'STX', 'LITE', 'CIEN', 'AAOI']
}

for plate, tickers in PLATES.items():
    st.markdown(f"<div class='section-header'>{plate}</div>", unsafe_allow_html=True)
    stock_data = get_market_data_with_spark(tickers)
    s_cols = st.columns(6)
    for i, t in enumerate(tickers):
        with s_cols[i]:
            if t in stock_data:
                sd = stock_data[t]
                s_cls = "change-up" if sd['change'] > 0 else "change-down"
                s_color = "#08d38d" if sd['change'] > 0 else "#f23645"
                
                st.markdown(f"""
                    <div class="card-top">
                        <div class="ticker-name">{t}</div>
                        <div class="chinese-name">{NAME_MAP.get(t, '')}</div>
                        <div class="price-main">${sd['price']} <span style="font-size:0.9rem" class="{s_cls}">{sd['change']:+.2f}%</span></div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="card-bottom">', unsafe_allow_html=True)
                st.plotly_chart(render_sparkline(sd['history'], s_color), use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据源: Yahoo Finance 实时电子盘")
