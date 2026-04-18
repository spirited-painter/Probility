import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def app():
    reveal_title = st.sidebar.checkbox("👀 揭晓本关真名", key="reveal_g1")
    if reveal_title:
        st.title("游戏 1：梭哈与凯利公式 (The All-In Illusion & Kelly Criterion)")
    else:
        st.title("神秘挑战项目 1")
    
    st.markdown("""
<div style="font-size: 24px; line-height: 1.6; padding: 20px; border-radius: 10px; background: rgba(100, 100, 100, 0.1); margin-bottom: 25px;">
    <strong>背景故事：</strong><br>
    你去买彩票，每次购买后只有两种结果：要么赔 50%，要么赚 50%。<br><br>
    你是一个高手，每次判断正确的概率是 <strong>60%</strong>。即是说，每次交易有 60% 的概率盈利 50%，40% 的概率损失 50%。<br><br>
    假如，你手里有100块资金，每次买彩票都 <strong>All-in（全仓梭哈）</strong>。<br>
    这是否意味着，只要交易次数足够多，就<strong>一定能够赚钱</strong>？
</div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ 游戏参数设置")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        initial_capital = st.number_input("初始资金", min_value=1.0, value=100.0, step=10.0)
        num_trades = st.slider("交易次数", min_value=10, max_value=1000, value=100, step=10)
    with col_p2:
        win_prob = st.slider("胜率 (判断正确概率)", min_value=0.01, max_value=0.99, value=0.60, step=0.01)
    with col_p3:
        win_ret = st.number_input("盈利比例", min_value=0.01, value=0.50, step=0.05)
        loss_ret = st.number_input("亏损比例", min_value=0.01, max_value=0.99, value=0.50, step=0.05)
    st.markdown("---")
    
    # Calculate Expected Values
    ev_single = win_prob * win_ret - (1 - win_prob) * loss_ret
    geom_ret_all_in = win_prob * np.log(1 + win_ret) + (1 - win_prob) * np.log(1 - loss_ret)
    
    st.info(f"👉 **单次预期收益 (算术期望):** {ev_single * 100:.2f}%")

    if 'g1_seed' not in st.session_state:
        st.session_state.g1_seed = np.random.randint(0, 100000)

    if st.button("🎲 重新掷骰子 (生成新随机走势)"):
        st.session_state.g1_seed = np.random.randint(0, 100000)

    # Simulate All-In
    np.random.seed(st.session_state.g1_seed)
    outcomes = np.random.rand(num_trades) < win_prob
    multipliers_all_in = np.where(outcomes, 1 + win_ret, 1 - loss_ret)
    wealth_all_in = initial_capital * np.cumprod(multipliers_all_in)
    
    # Kelly Criterion Formula
    # f* = p / loss_ret - (1 - p) / win_ret
    kelly_fraction = max(0, (win_prob / loss_ret) - ((1 - win_prob) / win_ret))
    
    # Simulate Kelly
    multipliers_kelly = np.where(outcomes, 1 + kelly_fraction * win_ret, 1 - kelly_fraction * loss_ret)
    wealth_kelly = initial_capital * np.cumprod(multipliers_kelly)
    
    # Dataframe for plotting
    x_axis = np.arange(1, num_trades + 1)
    df_plot = pd.DataFrame({
        "交易次数": x_axis,
        "全仓梭哈财富": wealth_all_in,
        f"凯利公式 (仓位 {kelly_fraction*100:.1f}%)财富": wealth_kelly
    })
    
    fig = px.line(df_plot, x="交易次数", y=["全仓梭哈财富", f"凯利公式 (仓位 {kelly_fraction*100:.1f}%)财富"],
                  title="财富随交易次数的变化",
                  labels={"value": "总资产", "variable": "策略"})
                  
    scale_type = st.radio("Y轴坐标系选择:", ["对数坐标 (Log, 推荐)", "线性坐标 (Linear)"], horizontal=True, key="g1_scale")
    fig.update_layout(yaxis_type="log" if "对数" in scale_type else "linear", yaxis_tickformat='.2e')
    st.plotly_chart(fig, use_container_width=True)

    st.metric(label="最终 全仓梭哈 财富", value=f"{wealth_all_in[-1]:.4f}")
    st.metric(label=f"最终 凯利策略 财富", value=f"{wealth_kelly[-1]:.4f}")

    with st.expander("🤔 查看残酷的数学解释及最终解 (凯利公式)"):
        st.warning(f"🚨 根据您当前设置的参数动态计算：**长期全仓增长率 (对数期望) = {geom_ret_all_in * 100:.2f}%**")
        part1 = "### 为什么单次期望为正，长期收益为负？\n\n"
        part2 = f"这涉及到**算术平均**和**几何平均**的区别：\n- 单次投掷的**算术期望**是：`{win_prob:.2f} * {win_ret} + {1-win_prob:.2f} * (-{loss_ret}) = {ev_single:.4f}`。这是你借钱雇了1万人帮你第一局同时下注，总钱数的期望。\n"
        part3 = "- 但是如果是**你一个人**连续交易，资金是**利滚利（乘法机制）**。\n\n"
        part4 = "举个具体的例子：100块全仓，赢一次变成150块，输一次变成75块。\n（1 + 0.5）*（1 - 0.5） = 1.5 * 0.5 = **0.75**。\n所以只要赢一次输一次，你就亏了 25%！要想通过赢一次补回输一次的亏损，你需要赢 100%。\n\n"
        part5 = r"长期的资金增长服从**对数收益期望**：" + "\n"
        part6 = r"$E = p * \ln(1 + \text{win}) + (1-p) * \ln(1 - \text{loss})$" + "\n"
        part7 = r"如果 $E < 0$，只要次数足够多，$W_n$ 必定趋近于 0。" + "\n\n"
        part8 = "### 临界点在哪里？\n你需要极高的胜率才能抵消掉重仓带来的波动摩擦，全仓模式下保持资产不缩水的胜率临界点 $p^*$ 是：\n"
        part9 = r"$p^* * \ln(1.5) + (1-p^*) * \ln(0.5) = 0$" + "\n"
        part10 = "计算得出 $p^* \\approx 0.6309$（即 63.1% 的胜率才能在全仓全下中保本）。这里胜率是 60%，因此长期必亏。\n\n"
        part11 = "### 终极解：凯利公式 (Kelly Criterion)\n为了实现几何增长率最大化，你不能全仓。你需要按照凯利公式计算下注比例 $f^*$：\n"
        part12 = r"$$f^* = \frac{p}{\text{loss_ret}} - \frac{1-p}{\text{win_ret}}$$" + "\n带入当前参数：\n"
        
        kf_val = (win_prob / loss_ret) - ((1 - win_prob) / win_ret)
        part13 = r"$f^* = \frac{" + str(win_prob) + r"}{" + str(loss_ret) + r"} - \frac{" + str(round(1-win_prob, 2)) + r"}{" + str(win_ret) + r"} = " + f"{kf_val:.4f}" + r"$" + "\n\n"
        part14 = f"也就是说，最佳单次投入资金应当是当前总资金的 **{max(0, kf_val) * 100:.1f}%**。\n在这个仓位下，虽然每次赚钱少了，但是规避了巨幅回撤产生的“乘法缩水”，长期的复利是最高的！\n"
        
        st.markdown(part1 + part2 + part3 + part4 + part5 + part6 + part7 + part8 + part9 + part10 + part11 + part12 + part13 + part14)
