import streamlit as st
import pandas as pd
import yfinance as yf
import akshare as ak
import plotly.express as px
import datetime

import os

DATA_DIR = "/Users/kiwi/Documents/Antigravity/Probility/data"

@st.cache_data(ttl=3600*24)
def load_data(asset):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    file_path = os.path.join(DATA_DIR, f"{asset}.csv")
    
    # 优先从本地读取，避免反复拉取 API
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
        
    # 如果本地没有，则通过 API 拉取（拉取月线以减小数据量，方便快速演示）
    start_date = "1990-01-01"
    
    try:
        if asset == "bitcoin":
            df = yf.download("BTC-USD", start="2014-01-01", interval="1mo", progress=False)
            df = df.reset_index()
            result = pd.DataFrame({'Date': df['Date'], 'Price': df['Close'].squeeze()})
        elif asset == "nasdaq":
            df = yf.download("^IXIC", start=start_date, interval="1mo", progress=False)
            df = df.reset_index()
            result = pd.DataFrame({'Date': df['Date'], 'Price': df['Close'].squeeze()})
        elif asset == "dow":
            df = yf.download("^DJI", start=start_date, interval="1mo", progress=False)
            df = df.reset_index()
            result = pd.DataFrame({'Date': df['Date'], 'Price': df['Close'].squeeze()})
        elif asset == "sp500":
            df = yf.download("^GSPC", start=start_date, interval="1mo", progress=False)
            df = df.reset_index()
            result = pd.DataFrame({'Date': df['Date'], 'Price': df['Close'].squeeze()})
        elif asset == "moutai":
            df = ak.stock_zh_a_hist(symbol="600519", period="monthly", start_date="20010827", adjust="qfq")
            df['Date'] = pd.to_datetime(df['日期'])
            result = pd.DataFrame({'Date': df['Date'], 'Price': df['收盘']})
        else:
            return pd.DataFrame()
            
        # 保存到本地避免未来重复下载
        if not result.empty:
            result.to_csv(file_path, index=False)
        return result
        
    except Exception as e:
        st.error(f"无法获取 {asset} 数据: {e}")
        return pd.DataFrame({'Date': [], 'Price': []})

def app():
    reveal_title = st.sidebar.checkbox("👀 揭晓本关真名", key="reveal_g4")
    if reveal_title:
        st.title("游戏 4：线性与对数坐标轴 (真实世界的财富增长)")
    else:
        st.title("神秘挑战项目 4")
    
    st.markdown("""
<div style="font-size: 24px; line-height: 1.6; padding: 20px; border-radius: 10px; background: rgba(100, 100, 100, 0.1); margin-bottom: 25px;">
    <strong>背景故事：</strong><br>
    金融史上最伟大的错觉之一，就在你看股票走势图的坐标轴里。<br><br>
    在普通图表（线性）里，过去二三十年的上涨总是像一片“死水平地”，最后几年突然发疯一样“直线上天”。<br>
    这是因为<strong>绝对数值变大了</strong>。从1涨到2（赚一倍）和从100涨到101（赚1%），在图上的高度是一样的。<br><br>
    而使用<strong>对数坐标（Log Scale）</strong>，同样高度代表的是“同样的涨幅（百分比）”。这才是资产增长的真实内涵。
</div>
    """, unsafe_allow_html=True)
    
    asset_map = {
        "神秘资产 1": "bitcoin",
        "神秘资产 2": "nasdaq",
        "神秘资产 3": "moutai",
        "神秘资产 4": "sp500",
        "神秘资产 5": "dow"
    }
    
    reveal_map = {
        "bitcoin": "比特币 (BTC)",
        "nasdaq": "纳斯达克综合指数 (IXIC)",
        "moutai": "贵州茅台 (600519.SH, 前复权)",
        "sp500": "标普 500 指数",
        "dow": "道琼斯工业平均指数"
    }
    
    selected_name = st.sidebar.selectbox("选择要观察的资产走势", list(asset_map.keys()))
    asset_code = asset_map[selected_name]
    
    with st.spinner("正在努力从远端拉取历史行情数据..."):
        df = load_data(asset_code)
    
    if df.empty:
        st.warning("数据拉取失败，请检查网络连接或 API 接口限制。")
        return

    st.subheader(f"你正在观察 {selected_name}")
    
    show_answer = st.checkbox("🤔 我猜不出来，这是什么资产？")
    if show_answer:
        st.success(f"🎊 这是： **{reveal_map[asset_code]}**")
    
    col1, col2 = st.columns([0.8, 1.2])  # 让左边的纯线性图更窄一些，放大斜率视觉
    with col1:
        st.markdown("### 线性坐标轴 (常规视角)")
        st.caption("视觉错觉：前期如同死水，后期直线飞天涨疯了。")
        fig_linear = px.line(df, x="Date", y="Price")
        fig_linear.update_layout(width=300, height=500, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_linear, use_container_width=False)
        
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.info("💡 线性图往往由于后期的绝对数值飙升，把早年的涨幅压成了平地。")
        if st.checkbox("🔥 点击揭晓本质：切换至对数坐标轴 (真实几何复利)"):
            st.markdown("### 对数坐标轴 (客观视角)")
            st.caption("真实内涵：斜率代表【涨跌幅百分比】，揭示了长期的发展规律。")
            fig_log = px.line(df, x="Date", y="Price", log_y=True)
            fig_log.update_layout(height=500, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_log, use_container_width=True)
            
            st.markdown("""
            ### 经验总结
            1. 你之所以会在投资顶峰冲进去接盘，很多时候是因为**线性坐标轴**给人一种“势不可挡，直冲云霄”的视觉冲击力。
            2. 而一旦你切到**对数坐标轴**，你会发现，那其实只是一段和二三十年前一样的正常波动（甚至是更慢的上涨）。
            3. 专业人士看跨度较长的宏大周期图，**必定切到 Log (对数) 坐标系**，否则你会被视觉严重欺骗！
            """)
