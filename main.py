import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date

# 1. 页面配置
st.set_page_config(page_title="PRO 隔夜美股热力中心", page_icon="⚡", layout="wide")

# 2. UI 样式：增加迷你图容器样式
st.markdown("""
    <style>
    .stApp { background-color: #0b1018; }
    .main .block-container { padding: 1rem 1.5rem; }
    .card {
        background: linear-gradient(145deg, #1e2533, #131924);
        border: 1px solid #2d3648;
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 2px;
    }
    .ticker-name { font-size: 0.95rem; font-weight: 800; color: #ffffff; }
    .chinese-name { font-size: 0.75rem; color: #9ca3af; font-weight: normal; }
    .price-main { font-size: 1.1rem; color: #ffffff; font-family: 'Courier New', monospace; margin: 2px 0; }
    .change-up { color: #08d38d; font-weight: bold; }
    .change-down { color: #f23645; font-weight: bold; }
    .news-container {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid #3b82f6; border-radius: 8px;
        padding: 12px; margin-bottom: 15px;
    }
    .news-item { display: flex; align-items: flex-start; margin-bottom: 4px; font-size: 0.85rem; color: #e2e8f0; }
    .news-tag {
        background: #3b82f6; color: white; padding: 1px 6px; border-radius: 4px;
        font-size: 0.65rem; margin-right: 8px; font-weight: bold;
    }
    .section-header {
        background: linear-gradient(90deg, #1e222d, #0b1018);
        color: #d1d4dc; padding: 6px 12px; border-left: 4px solid #2962ff;
        font-size: 0.95rem; margin: 15px 0 8px 0; font-weight: bold;
    }
    /* 迷你图表容器微调 */
    .chart-container { margin-top: -10px; padding: 0 5px; }
    </style>
""", unsafe_allow_html=True)

# 3. 名称映射
NAME_MAP = {
    '^DJI': '道琼斯工业指数', '^GSPC': '标准普尔指数', '^IXIC': '纳斯达克指数',
    'NQ=F': '纳指期货', 'ES=F': '标普500期货',
    'NVDA': '英伟达', 'TSM': '台积电', 'INTC': '英特尔', 'AMD': '超威半导体', 'AVGO': '博通', 'ARM': '安谋',
    'MU': '美光科技', 'WDC': '西部数据', 'STX': '希捷', 'LITE': 'Lumentum', 'CIEN': 'Ciena', 'AAOI': '应用光电',
    'RKLB': '火箭实验室', 'LUNR': '直觉机器', 'ASTS': 'AST SpaceMobile', 'RCAT': 'Red Cat', 'AVAV': '环境', 'ONDS': 'Ondas',
    'MSTR': '微策投资', 'COIN': 'Coinbase', 'HOOD': '罗宾汉', 'IREN': 'Iris Energy', 'NBIS': 'Nebula', 'APLD': 'Applied Digital'
}

# 4. 增强版数据抓取：同时获取价格和走势历史
@st.cache_data(ttl=60)
def get_data_with_history(tickers):
    # 获取 1d 的 5 分钟线，足以绘制漂亮的走势图
    data = yf.download(tickers, period="1d", interval="5m", prepost=True, progress=False)
    if data.empty: return {}
    
    results = {}
    for t in tickers:
        try:
            subset = data.xs(t, axis=1, level=1) if len(tickers) > 1 else data
            subset = subset.dropna()
            if subset.empty: continue
            
            curr_p = subset['Close'].iloc[-1]
            prev_close = subset['Close'].iloc[0]
            chg = ((curr_p - prev_close) / prev_close) * 100
            
            results[t] = {
                'Price': curr_p,
                'Change': chg,
                'History': subset['Close'].tolist() # 用于画图的数据点
            }
        except: continue
    return results

# ---------------- 页面逻辑 ----------------
st.title("⚡ 隔夜美股热力中心 (实时曲线版)")

# 1. 指数板块 (包含走势图)
st.markdown("<div class='section-header'>MARKET INDICES (核心股指)</div>", unsafe_allow_html=True)
idx_list = ['^DJI', '^GSPC', '^IXIC', 'NQ=F', 'ES=F']
idx_data = get_data_with_history(idx_list)

cols = st.columns(5)
for i, t in enumerate(idx_list):
    with cols[i]:
        if t in idx_data:
            d = idx_data[t]
            display_name = "S&P 500 Index" if t == '^GSPC' else "NASDAQ Index" if t == '^IXIC' else t
            cls = "change-up" if d['Change'] > 0 else "change-down"
            chart_color = "#08d38d" if d['Change'] > 0 else "#f23645"
            
            st.markdown(f"""
                <div class="card">
                    <div class="ticker-name">{display_name}</div>
                    <div class="chinese-name">{NAME_MAP.get(t, '')}</div>
                    <div class="price-main">${d['Price']:,.2f} <span class="{cls}">{d['Change']:+.2f}%</span></div>
                </div>
            """, unsafe_allow_html=True)
            # 绘制迷你曲线图
            st.line_chart(d['History'], height=50, use_container_width=True, color=chart_color)
        else:
            st.info(f"{t} 载入中...")

# 2. 重要新闻
st.markdown("""
<div class="news-container">
    <div class="news-item"><span class="news-tag" style="background:#ef4444;">NQ!</span><span><b>纳指期货</b> 突破 25700，实时涨幅达 <b>+0.91%</b>，曲线显示稳步上攻。</span></div>
    <div class="news-item"><span class="news-tag" style="background:#10b981;">Hot</span><span><b>英特尔 (INTC)</b> 隔夜放量，曲线呈 45 度拉升，夜盘目前小幅回调。</span></div>
</div>
""", unsafe_allow_html=True)

# 3. 核心板块个股 (带走势图)
PLATES = {
    '芯片/AI': ['NVDA', 'TSM', 'INTC', 'AMD', 'AVGO', 'ARM'],
    '存储/光模块': ['MU', 'WDC', 'STX', 'LITE', 'CIEN', 'AAOI'],
    '航天/无人机': ['RKLB', 'LUNR', 'ASTS', 'RCAT', 'AVAV', 'ONDS'],
    '加密/云': ['MSTR', 'COIN', 'HOOD', 'IREN', 'NBIS', 'APLD']
}

for plate, tickers in PLATES.items():
    st.markdown(f"<div class='section-header'>{plate}</div>", unsafe_allow_html=True)
    p_data = get_data_with_history(tickers)
    
    # 将获取到的数据按涨幅排序展示
    sorted_tickers = sorted(p_data.keys(), key=lambda x: p_data[x]['Change'], reverse=True)
    
    cols = st.columns(6)
    for i, t in enumerate(sorted_tickers):
        d = p_data[t]
        with cols[i % 6]:
            cls = "change-up" if d['Change'] > 0 else "change-down"
            chart_color = "#08d38d" if d['Change'] > 0 else "#f23645"
            st.markdown(f"""
                <div class="card">
                    <div class="ticker-name">{t} <span class="chinese-name">({NAME_MAP.get(t, '')})</span></div>
                    <div class="price-main">${d['Price']:,.2f} <span class="{cls}">{d['Change']:+.2f}%</span></div>
                </div>
            """, unsafe_allow_html=True)
            # 绘制个股迷你曲线
            st.line_chart(d['History'], height=40, use_container_width=True, color=chart_color)

# 4. 底部榜单
st.markdown("<div class='section-header'>TOP GAINERS (隔夜领涨)</div>", unsafe_allow_html=True)
g_cols = st.columns(4)
gainers = [("NAMM", 130.61), ("GITS", 97.97), ("PAVM", 94.67), ("LSTA", 86.57)]
for i, (t, c) in enumerate(gainers):
    with g_cols[i]:
        st.markdown(f"""<div class="card" style="border-left: 3px solid #10b981;"><span class="ticker-name">{t}</span><span class="change-up" style="float:right;">+{c}%</span></div>""", unsafe_allow_html=True)

st.caption(f"Last Update: {date.today()} | 走势图基于 5 分钟频率更新")
