import streamlit as st
import numpy as np

def app():
    reveal_title = st.sidebar.checkbox("👀 揭晓本关真名", key="reveal_g7")
    if reveal_title:
        st.title("游戏 7：年会抽奖与几何分布")
    else:
        st.title("神秘挑战项目 7")
        
    st.markdown("""
<div style="font-size: 24px; line-height: 1.6; padding: 20px; border-radius: 10px; background: rgba(100, 100, 100, 0.1); margin-bottom: 25px;">
    <strong>背景故事：</strong><br>
    你们公司每年都会举办一次极其丰厚的年会抽奖。大奖只有少数人能拿，全公司的综合中奖率固定。
    <br><br>
    这就引出了一个非常诱人的职场错觉：<br>
    “如果今年的中奖率是 10%，那是不是意味着，只要我在这家公司干满 10 年，就绝对、一定、肯定能中一次大奖呢？”<br><br>
    让我们用你自己的职业生涯来检验一下这个直觉。
</div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ 抽奖概率设置")
    win_prob = st.slider("公司年会设定的中奖率 (%)", min_value=1.0, max_value=99.0, value=10.0, step=1.0) / 100.0
    st.markdown("---")
    
    # State tracking
    if 'g7_year' not in st.session_state or st.session_state.get('g7_win_prob') != win_prob:
        st.session_state.g7_year = 1
        st.session_state.g7_history = []
        st.session_state.g7_win_prob = win_prob
        st.session_state.g7_won_at_least_once = False
        
    def reset_lottery():
        st.session_state.g7_year = 1
        st.session_state.g7_history = []
        st.session_state.g7_won_at_least_once = False
        
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(f"🎉 参加第 {st.session_state.g7_year} 年的年会抽奖！", type="primary", use_container_width=True):
            # Draw lottery
            win = np.random.rand() < win_prob
            st.session_state.g7_history.append({"year": st.session_state.g7_year, "win": win})
            if win:
                st.session_state.g7_won_at_least_once = True
            st.session_state.g7_year += 1
            
    with col2:
        if st.button("🔄 离职重开 (清空资历重新来过)", use_container_width=True):
            reset_lottery()
            st.rerun()

    st.markdown("---")
    
    if len(st.session_state.g7_history) > 0:
        st.subheader(f"📅 你的职场抽奖履历 (共 {len(st.session_state.g7_history)} 年)")
        
        # Calculate real-time cumulative math
        n_years = len(st.session_state.g7_history)
        prob_never_win = (1 - win_prob) ** n_years
        prob_win_at_least_once = 1 - prob_never_win
        expected_wins = n_years * win_prob
        
        # Display history
        history_md = ""
        for record in reversed(st.session_state.g7_history):  # newest first
            if record["win"]:
                history_md += f"- **第 {record['year']} 年：** 🎊 **中了！！！大奖带回家！**\n"
            else:
                history_md += f"- 第 {record['year']} 年： 陪跑，只拿到了阳光普照奖 (纸巾一包)。\n"
        
        col_hist, col_math = st.columns([1, 1.2])
        with col_hist:
            st.markdown(history_md)
            
        with col_math:
            if st.session_state.g7_won_at_least_once:
                st.success("🎉 你终于打破了魔咒，在这个公司拿到过至少一次大奖了！")
            else:
                st.warning("🥲 革命尚未成功，你还在苦苦陪跑中...")
                
            st.markdown(f"""
            #### 📊 残酷的数学显微镜
            虽然单次中奖率是 **{win_prob*100:.1f}%**，但你已经抽了 **{n_years}** 年。
            
            1. **你在这 {n_years} 年里【一次都没中】的概率：**
            > `{1 - win_prob:.2f} × {1 - win_prob:.2f} × ... ({n_years}次) = {prob_never_win * 100:.2f}%`
            
            2. **你这 {n_years} 年里【至少中一次】的真实累积概率：**
            > `1 - {prob_never_win * 100:.2f}% = ` **`{prob_win_at_least_once * 100:.2f}%`**
            
            3. **直觉幻觉 (算术期望法则)：**
            > 理论上 {n_years} 年你的总体期望中奖次数是 `{expected_wins:.2f}` 次。**加法法则**很容易让人以为 $10\% \\times 10 = 100\%$。但**几何乘法法则**无情地告诉你：即便抽 10 年，依然有高达 {((1-win_prob)**10)*100:.1f}% 的人，十年连抽一次都中不了！
            """)
