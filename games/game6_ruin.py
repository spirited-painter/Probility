import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd

def app():
    reveal_title = st.sidebar.checkbox("👀 揭晓本关真名", key="reveal_g6_as_3")
    if reveal_title:
        st.title("游戏 3：赌徒破产悖论 (Gambler's Ruin)")
    else:
        st.title("神秘挑战项目 3")
    
    st.markdown("""
<div style="font-size: 24px; line-height: 1.6; padding: 20px; border-radius: 10px; background: rgba(100, 100, 100, 0.1); margin-bottom: 25px;">
    <strong>背景故事：</strong><br>
    假如你带着一定数量的本金去赌场，想要赢到目标金额后就收手回家。<br>
    赌场由于存在“抽水”或者像轮盘赌里的“0”和“00”等设定，玩家的单局胜率往往略低于 50%（比如 49%）。<br><br>
    那么你的“下注金额”大小，会对你最终<strong>“赢钱走人”</strong>还是<strong>“赔光破产”</strong>的概率产生什么影响？
</div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ 游戏参数设置")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        initial_cash = st.number_input("初始本金 ($)", min_value=10, max_value=1000, value=50, step=10)
    with col_p2:
        target_cash = st.number_input("目标金额 ($)", min_value=int(initial_cash)+10, max_value=10000, value=100, step=10)
    with col_p3:
        win_prob = st.slider("单局胜率", min_value=0.01, max_value=0.99, value=0.49, step=0.01)
    
    st.markdown("---")
    
    bet_sizes = [1, 2, 5, 10, 25, 50, initial_cash]
    bet_sizes = sorted(list(set([b for b in bet_sizes if b <= initial_cash])))
    st.markdown(f"**👇 下面的左表对比了不同单次下注额的理论成功率，右图为您呈现了平行宇宙的真实走势：**")
    
    # 理论计算
    results = []
    p = win_prob
    q = 1 - p
    
    for bet in bet_sizes:
        # Convert to units of bet
        i = initial_cash / bet
        M = target_cash / bet
        
        if p == 0.5:
            p_win = i / M
        else:
            # P(win) = (1 - (q/p)^i) / (1 - (q/p)^M)
            ratio = q / p
            try:
                p_win = (1 - ratio**i) / (1 - ratio**M)
            except OverflowError:
                # If i or M is huge and ratio > 1, the numerator and denominator blow up
                # ratio > 1 means p < 0.5 (disadvantage)
                # For huge numbers with p < 0.5, p_win approaches 0
                p_win = 0.0
                
        p_ruin = 1.0 - p_win
        results.append({
            "单次下注额": f"${bet}",
            "赢钱概率 (%)": p_win * 100,
            "破产概率 (%)": p_ruin * 100
        })
        
    df_results = pd.DataFrame(results)
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.subheader("💡 理论推导结果")
        st.dataframe(df_results.style.format({"赢钱概率 (%)": "{:.4f}", "破产概率 (%)": "{:.4f}"}))
        st.info("提示：看看你的破产概率，随着下注额增加是怎样变化的。")
        
    with col2:
        st.subheader("🎲 尝试模拟 3 条平行宇宙的路径")
        sim_bet = st.selectbox("选择测试下注额", bet_sizes, index=0)
        
        if 'g6_seed' not in st.session_state:
            st.session_state.g6_seed = np.random.randint(0, 100000)

        if st.button("🎲 重新模拟平行宇宙走势"):
            st.session_state.g6_seed = np.random.randint(0, 100000)
            
        np.random.seed(st.session_state.g6_seed)
        paths = []
        max_steps = 10000  # Prevent infinite loops in rare paths
        
        for path_idx in range(3):
            cash = initial_cash
            history = [cash]
            for _ in range(max_steps):
                win = np.random.rand() < win_prob
                cash += sim_bet if win else -sim_bet
                history.append(cash)
                
                if cash <= 0:
                    break
                if cash >= target_cash:
                    break
            
            df_path = pd.DataFrame({
                "局数": range(len(history)),
                "资金": history,
                "路径": f"模拟 {path_idx + 1}"
            })
            paths.append(df_path)
            
        df_all = pd.concat(paths)
        
        fig = px.line(df_all, x="局数", y="资金", color="路径", title=f"下注额 ${sim_bet} 时的财富路径 (终局为 0 或 {target_cash})")
        
        # 添加上下界参考线
        fig.add_hline(y=target_cash, line_dash="dash", line_color="green", annotation_text="目标 (赢钱走人)")
        fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="破产 (被抬出赌场)")
        
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    ### 经典结论
    如果你处于**劣势（单局胜率 < 50%）**：
    - **玩的局数越多越容易破产**。如果你每次只下注一点点钱（比如 1 块钱），你需要漫长的拉锯战才可能赢到目标线。这相当于给时间流大开倒车，在这个负期望值的数学吸尘器下，你的本金早晚会被“大数定律”给洗干净。
    - **如果你非赌不可，唯一的策略就是“一把梭”**（每次下注尽可能大）。比如只有这 50 块，要么一把到 100，要么一把输光。这能最大化你带着钱离开的概率（避免陷入吃人的复投循环）。

    如果你处于**优势（单局胜率 > 50%）**：
    - 局势反转：**小下注慢玩**反而是保护你不被震荡扫地出门的最佳武器。（这就是为什么在真实金融市场、量化交易中，大家常谈“仓位管理”和通过凯利公式控制头寸）。
    - 只要你不下大注被一波偶然的连续背运带走，凭借“正期望值”你最后肯定能赢到那个目标。
    """)
