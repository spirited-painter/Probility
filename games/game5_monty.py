import streamlit as st
import numpy as np
import random
import pandas as pd
import plotly.express as px

def app():
    reveal_title = st.sidebar.checkbox("👀 揭晓本关真名", key="reveal_g5")
    if reveal_title:
        st.title("游戏 5：三门问题 (Monty Hall Problem)")
    else:
        st.title("神秘挑战项目 5")

    st.markdown("""
<div style="font-size: 24px; line-height: 1.6; padding: 20px; border-radius: 10px; background: rgba(100, 100, 100, 0.1); margin-bottom: 25px;">
    <strong>背景故事：</strong><br>
    这是一个反直觉的经典概率游戏。<br>
    假设你正在参加一个电视节目。你面前有三大扇门。其中一扇门后面停着一辆豪华跑车（大奖），另外两扇门后面各是一只山羊。<br><br>
    <strong>规则如下：</strong><br>
    1. 你先选定一扇门。<br>
    2. 知道门后是什么的主持人（Monty），会从你<strong>没有选</strong>的两扇门中，打开一扇<strong>必定是山羊</strong>的门。<br>
    3. 主持人给你一个选择：“你现在要改选剩下那扇没开的门，还是坚持你一开始的选择？”<br><br>
    你该“换”还是“不换”？换了收益大，还是不换收益大，还是一样大？
</div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ 百门模式参数设置")
    num_doors = st.slider("总共增加到几扇门？(挑战你的直觉)", min_value=3, max_value=100, value=3, step=1)
    st.markdown("---")
    
    # Session State Initialization
    if 'monty_stage' not in st.session_state or st.session_state.get('num_doors') != num_doors:
        st.session_state.monty_stage = 'pick_1'
        st.session_state.num_doors = num_doors
        # 0 is goat, 1 is car
        doors = [0] * num_doors
        car_idx = random.randint(0, num_doors - 1)
        doors[car_idx] = 1
        st.session_state.doors = doors
        st.session_state.car_idx = car_idx
        st.session_state.user_choice = None
        st.session_state.opened_by_host = []
    
    def reset_game():
        st.session_state.monty_stage = 'pick_1'
        doors = [0] * num_doors
        car_idx = random.randint(0, num_doors - 1)
        doors[car_idx] = 1
        st.session_state.doors = doors
        st.session_state.car_idx = car_idx
        st.session_state.user_choice = None
        st.session_state.opened_by_host = []
        st.session_state.final_choice = None
        st.session_state.won = False
    
    if st.button("重新开始游戏"):
        reset_game()

    st.markdown("---")
    
    # 统一视觉展示区域：渲染所有门的状态
    st.markdown("### 🚪 命运行节：现场大门实时状态")
    cols = st.columns(min(num_doors, 10))
    
    # Stage 1: Initial Pick
    if st.session_state.monty_stage == 'pick_1':
        st.info("第一阶段：请凭直觉选择一扇门！")
        for i in range(num_doors):
            with cols[i % 10]:
                if st.button(f"🚪 门 {i+1}", key=f"door_{i}", use_container_width=True):
                    st.session_state.user_choice = i
                    
                    # Host opens N-2 goat doors
                    available_to_open = [d for d in range(num_doors) if d != i and st.session_state.doors[d] == 0]
                    num_to_open = num_doors - 2
                    st.session_state.opened_by_host = random.sample(available_to_open, num_to_open)
                    st.session_state.monty_stage = 'pick_2'
                    st.rerun()

    # Stage 2: Host Opened Doors, Ask for Switch
    elif st.session_state.monty_stage == 'pick_2':
        closed_doors = [d for d in range(num_doors) if d not in st.session_state.opened_by_host]
        other_door = [d for d in closed_doors if d != st.session_state.user_choice][0]
        st.warning(f"由于主持人帮你排除了 {num_doors-2} 个错误答案，现在场上只有你的选择和另外一扇门紧闭。")
        for i in range(num_doors):
            with cols[i % 10]:
                if i == st.session_state.user_choice:
                    st.button(f"✅ 你的初选", key=f"door_{i}", type="primary", use_container_width=True)
                elif i in st.session_state.opened_by_host:
                    st.button(f"🐐 淘汰(羊)", key=f"door_{i}", disabled=True, use_container_width=True)
                else:
                    st.button(f"✨ 门 {i+1} (可换)", key=f"door_{i}", type="primary", use_container_width=True)
                    
        st.info(f"主持人偷偷对你坏笑：“我是知道底牌的，我现在帮你排除了所有必然是山羊的门。你要换去唯一没开的 **门 {other_door + 1}** 吗？”")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(f"🔒 坚守初心 (保持初选 门 {st.session_state.user_choice + 1})", use_container_width=True):
                st.session_state.final_choice = st.session_state.user_choice
                st.session_state.monty_stage = 'reveal'
                st.rerun()
        with col_btn2:
            if st.button(f"🔄 我要换！ (改选剩下的 门 {other_door + 1})", type="primary", use_container_width=True):
                st.session_state.final_choice = other_door
                st.session_state.monty_stage = 'reveal'
                st.rerun()

    # Stage 3: Reveal
    elif st.session_state.monty_stage == 'reveal':
        car_door = st.session_state.car_idx + 1
        chosen_door = st.session_state.final_choice + 1
        
        for i in range(num_doors):
            with cols[i % 10]:
                if i == st.session_state.car_idx:
                    if i == st.session_state.final_choice:
                        st.button(f"🚘 🎉你的跑车", key=f"door_{i}", disabled=True, use_container_width=True)
                    else:
                        st.button(f"🚘 跑车", key=f"door_{i}", disabled=True, use_container_width=True)
                else:
                    if i == st.session_state.final_choice:
                        st.button(f"🐐 ❌你的山羊", key=f"door_{i}", disabled=True, use_container_width=True)
                    else:
                        st.button(f"🐐 山羊", key=f"door_{i}", disabled=True, use_container_width=True)

        if st.session_state.final_choice == st.session_state.car_idx:
            st.success(f"🎊 极致幸运！你最后锁定的门 {chosen_door} 后面竟然真的是一辆豪华跑车！！！")
            st.balloons()
        else:
            st.error(f"💀 令人心碎！你最后锁定的门 {chosen_door} 后面是一只无辜的山羊 🐐。")
            st.info(f"真正的大奖其实一直藏在 **门 {car_door}** 后面。")
            
        st.markdown("""
        ### 原理解释
        为什么不管几扇门，“换”赢率永远压倒性更高？
        1. 你第一次选的门，中奖概率永远极微弱 `1 / N` (100门就是可怜的 1%)。
        2. **跑车在剩下所有门中的总概率是 `(N-1) / N`** (100门就是碾压的 99%)。
        3. 主持人是个自带视角的“作弊器”，他在暗中帮忙排除了所有的雷区。
        4. 所以“换门”，等于你直接打包**带走了剩下那 99% 的资产概率总和**！
        """)

    st.markdown("---")
    st.subheader("🤖 还是不信？让电脑跑 1000 次模拟！")
    
    if st.button(f"模拟 1000 次 {num_doors}个门的情况"):
        keep_wins = 0
        switch_wins = 0
        trials = 1000
        
        for _ in range(trials):
            car = random.randint(0, num_doors - 1)
            pick = random.randint(0, num_doors - 1)
            
            # Keep strategy
            if pick == car:
                keep_wins += 1
            # Switch strategy
            else:
                switch_wins += 1
                
        df_sim = pd.DataFrame({
            "策略": ["坚守初心 (不换)", "见异思迁 (换门)"],
            "胜率": [keep_wins / trials, switch_wins / trials]
        })
        
        fig = px.bar(df_sim, x="策略", y="胜率", color="策略", title=f"1000次随机模拟结果 (总{num_doors}门)", range_y=[0, 1])
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(f"模拟结果揭晓：不换的胜率 {keep_wins/trials*100:.1f}%，换的胜率 {switch_wins/trials*100:.1f}%")
