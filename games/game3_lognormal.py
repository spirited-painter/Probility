import streamlit as st
import numpy as np
import plotly.express as px
import scipy.stats as stats
import pandas as pd

def app():
    reveal_title = st.sidebar.checkbox("👀 揭晓本关真名", key="reveal_g3_as_6")
    if reveal_title:
        st.title("游戏 6：从“全仓梭哈”到“对数正态分布”")
    else:
        st.title("神秘挑战项目 6")
    
    st.markdown("""
<div style="font-size: 24px; line-height: 1.6; padding: 20px; border-radius: 10px; background: rgba(100, 100, 100, 0.1); margin-bottom: 25px;">
    <strong>生活故事：</strong><br>
    你有 100 元，每次全仓交易要么赚 50%，要么亏 50%。<br>
    如果有 <strong>10万人</strong> 和你一起去赌场，每个人都独立玩了 100 次（比如抛掷均匀硬币定输赢）。<br><br>
    100次之后，你们这 10 万人的最终资金分布是钟形（正态分布）吗？<br>
    不，它是一条向右拖着极长极长尾巴的<strong>偏态曲线</strong>。
</div>
    """, unsafe_allow_html=True)
    
    if st.button("生成 10 万人的 100 次交易结果"):
        num_people = 100000
        num_trades = 100
        initial_wealth = 100.0
        
        # We don't need to simulate all paths step-by-step. 
        # We just need the number of wins for each person.
        # It's a binomial distribution: B(100, 0.5)
        wins = np.random.binomial(n=num_trades, p=0.5, size=num_people)
        losses = num_trades - wins
        
        # Calculate final wealth
        final_wealth = initial_wealth * (1.5 ** wins) * (0.5 ** losses)
        
        # For plot, due to extreme right skew, we might need a custom layout
        # Plot 1: Histogram of Wealth
        st.subheader("1. 真实的财富分布 (对数正态分布极度偏斜)")
        df1 = pd.DataFrame({"最终财富财富值": final_wealth})
        # Plotting top 99% to avoid the chart being distorted by 1 out of 100,000 who won 90 times
        cap_val = np.percentile(final_wealth, 99.9)
        fig1 = px.histogram(df1[df1['最终财富财富值'] < cap_val], x="最终财富财富值", nbins=100,
                            title="剔除极个别首富后的普通人财富分布图 (向右长尾)")
        st.plotly_chart(fig1, use_container_width=True)
        
        st.markdown(f"**提示：** 实际上有极个别人财富超过了 {cap_val:.0f}，只是为了你能看清集中区域，没有画进去。")
        
        # Plot 2: Histogram of Log Wealth
        st.subheader("2. 为什么取对数后，它又是完美的钟形？")
        log_wealth = np.log(final_wealth)
        df2 = pd.DataFrame({"最终对数财富 ln(财富)": log_wealth})
        fig2 = px.histogram(df2, x="最终对数财富 ln(财富)", nbins=100,
                            title="对数世界里，完美的正态分布 (钟形曲线)")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    ### 统计原理：对数正态分布 (Log-normal)
    
    1. **为什么不是钟形？** 当事物的增长是**乘法机制**（比如利滚利、涨跌幅、复利）时，它就不再对称了。增加 50% 和减少 50% 并不对称。
    2. **为什么叫“对数正态”？** 因为把乘法公式取对数 ($\ln$) 后，数学上 `A * B` 就变成了加法 `ln(A) + ln(B)`。
    3. 根据**中心极限定理 (CLT)**，无数次独立的随机加减效应累积，必然走向正态分布。
    因此，资金的**对数值**服从加减累积正态分布，而资金的绝对金额由于是针对正态的指数逆推，自然形成了偏度极高的**对数正态分布**。
    
    ---
    
    ### 药学实战：【DMPK 参数 (AUC, Cmax, CL, F)】
    
    这也是制药行业临床药代动力学（DMPK）必须要掌握的原则。
    
    **问题：为什么患者个体的清除率 (CL) 和生物利用度 (F) 数据分布不是正态分布？**
    1. **现实约束：** 它们不可能为负数，而普通的正态分布在理论上是可以趋向负无穷的。
    2. **乘法效应：** 酶活性、血流量、肝肾功能受损等效应，往往是对基础指标进行“成倍差异”的影响，而不是简单的加减。例如，某种变异酶可能让代谢变慢一半（乘法机制）。
    
    **计算公式：**
    体系中的血药浓度暴露量 AUC 的公式：
    $$AUC = \\frac{\\text{Dose} \\times F}{CL}$$
    
    这同样是一个充满乘除法的公式。
    如果我们对等式左右两边取自然对数，神奇的事情就发生了：
    $$\\ln(AUC) = \\ln(\\text{Dose}) + \\ln(F) - \\ln(CL)$$
    
    全是完美符合中心极限定理的正态分布**加减**！
    结论：PK 参数（除去 $T_{max}$ 等少数）几乎全部服从**对数正态分布**。这也是为什么当你作为申办方去做仿制药的 BE（生物等效性）试验时，指导原则强制要求：所有受试者的 AUC 和 Cmax 数据**必须先取自然对数，然后再求平均和做统计学假设检验**！
    """)
