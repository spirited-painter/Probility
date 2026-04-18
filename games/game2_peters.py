import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

def app():
    reveal_title = st.sidebar.checkbox("👀 揭晓本关真名", key="reveal_g2")
    if reveal_title:
        st.title("游戏 2：彼得斯抛硬币 (The Peters Coin Toss 与 遍历性)")
    else:
        st.title("神秘挑战项目 2")
    
    st.markdown("""
<div style="font-size: 24px; line-height: 1.6; padding: 20px; border-radius: 10px; background: rgba(100, 100, 100, 0.1); margin-bottom: 25px;">
    <strong>背景故事：</strong><br>
    这也是一个由于“乘法动态”和“加法动态”造成认知错觉的故事，由物理学家和经济学家 Ole Peters 提出。<br><br>
    游戏规则非常简单：你投掷一枚均匀硬币。<br>
    - 如果是正面：你的财富增加 <strong>50%</strong>。<br>
    - 如果是反面：你的财富减少 <strong>40%</strong>。<br><br>
    单从单次下注来看，你的<strong>单次算术期望值为正</strong>： <code>0.5 * 50% + 0.5 * (-40%) = 5%</code>。<br><br>
    但是，如果<strong>是你自己一个人连续玩下去</strong>呢？我们来看看社会总财富和你个人的真实体感。
</div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ 游戏参数设置")
    st.info("💡 提示：由于是纯粹的蒙特卡洛模拟，您可以直接调节总人数。人数越少，整体社会的存续时间可能越短。")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        population = st.number_input("模拟的测试人数 (社会规模 N)", min_value=1, max_value=100000, value=1000, step=100)
    with col_p2:
        tosses = st.slider("抛硬币次数 (时间长度 T)", min_value=5, max_value=1000, value=100, step=10)

    if 'g2_seed' not in st.session_state:
        st.session_state.g2_seed = np.random.randint(0, 100000)

    if st.button("🎲 重新抛硬币 (生成新模拟社会)"):
        st.session_state.g2_seed = np.random.randint(0, 100000)

    st.markdown("---")
    
    np.random.seed(st.session_state.g2_seed)
    initial_wealth = 100.0
    
    # Simulate Paths
    outcomes = np.random.choice([1.5, 0.6], size=(population, tosses))
    wealth_paths = initial_wealth * np.cumprod(outcomes, axis=1)
    
    # Add initial state
    initial_state = np.full((population, 1), initial_wealth)
    wealth_paths = np.hstack([initial_state, wealth_paths])
    
    # Times
    times = np.arange(tosses + 1)
    
    # Mathematical theoretical Expected Value
    expected_total = population * initial_wealth * (1.05 ** times)
    
    # Calculate simulated statistics
    sim_total_wealth = np.sum(wealth_paths, axis=0)
    sim_avg_wealth = np.mean(wealth_paths, axis=0)
    
    # Select randomly one individual
    random_individual = wealth_paths[0, :]
    
    # Plotting Total Wealth
    df1 = pd.DataFrame({
        "次数": times,
        "理论社会总财富 (无限人口期望)": expected_total,
        "实际模拟社会总财富 (真实有限人口)": sim_total_wealth,
    })
    
    st.subheader("1. 为什么它是好生意：系统集合视角")
    scale_type1 = st.radio("系统视图 - 坐标系:", ["对数坐标 (Log)", "线性坐标 (Linear)"], horizontal=True, key="g2_scale1")
    fig1 = px.line(df1, x="次数", y=["理论社会总财富 (无限人口期望)", "实际模拟社会总财富 (真实有限人口)"], 
                   title=f"【社会总财富】理论上无限膨胀，但有限人口下最终往往崩溃")
    fig1.update_layout(yaxis_type="log" if "对数" in scale_type1 else "linear", yaxis_tickformat='.2e')
    st.plotly_chart(fig1, use_container_width=True)
    st.write(f"在无尽的时间长河里，**实际的社会总财富也会因为普遍破产而出现下跌甚至趋于零**。这是因为在有限人口群体中，数学理论上的无限扩张最终会被物理现实（非遍历性导致的全员归零）所击败。")
    
    # Plotting Individual vs Average
    df2 = pd.DataFrame({
        "次数": times,
        "社会平均财富 (人均)": sim_avg_wealth,
        "随机抽样的 1 个真实个体财富": random_individual,
    })

    st.subheader("2. 为什么它是坏生意：个体时间流视角")
    scale_type2 = st.radio("个体视图 - 坐标系:", ["对数坐标 (Log)", "线性坐标 (Linear)"], horizontal=True, key="g2_scale2")
    fig2 = px.line(df2, x="次数", y=["社会平均财富 (人均)", "随机抽样的 1 个真实个体财富"], 
                   title=f"“均值”被假象或极少数超级幸运儿拉高，而随机个体的感官是一路向南")
    fig2.update_layout(yaxis_type="log" if "对数" in scale_type2 else "linear", yaxis_tickformat='.2e')
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("""
    ### 本质解释 (非遍历性系统 Non-Ergodicity)
    
    **遍历性系统**中，空间上的平均（一万个人玩一次）应该等于时间上的平均（一个人玩一万次）。
    但金融和利滚利的财富并非如此！它是一个**非遍历性系统**。
    
    1. **空间期望 (算术均值)**：由于单次 `+50%` 和 `-40%`，算术平均是正的 (`1.05`)，因此理论上无数个人同时玩一步，社会总财富在变多。
    2. **时间期望 (几何均值)**：对于个人而言，盈亏的概率都是 50%。经过两次随机交易（一盈一亏），`1.5 * 0.6 = 0.9`，资金缩水了 10%！长期的复合增长因子是 `sqrt(1.5 * 0.6) = 0.9486 < 1`。因此个人的时间流长期期望必定趋一无所有（破产）。
    
    **结论：** 有限系统中的“表面人均富裕”其实是一个数学幻梦。它要么是由一个还没破产的超级寡头暂时支撑起来的，要么在拉长的时间线上，由于乘法系统下不可避免的必然衰退，所有人都会被拉回深渊。
    """)
