import streamlit as st
import importlib

st.set_page_config(
    page_title="Probability & Finance Games",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("🎲 概率与金融游戏")
st.sidebar.markdown("探索概率论反直觉的奇妙世界。")

# Navigation
PAGES = {
    "神秘游戏 1：？？？": "games.game1_kelly",
    "神秘游戏 2：？？？": "games.game2_peters",
    "神秘游戏 3：？？？": "games.game6_ruin",
    "神秘游戏 4：？？？": "games.game4_axes",
    "神秘游戏 5：？？？": "games.game5_monty",
    "神秘游戏 6：？？？": "games.game3_lognormal",
    "神秘游戏 7：？？？": "games.game7_lottery",
}

selection = st.sidebar.radio("选择你要体验的游戏", list(PAGES.keys()))

st.sidebar.markdown("---")
st.sidebar.info("这是一组关于概率论、金融数学和分布反直觉特性的互动游戏演示。")

# Load the selected page
page_module_name = PAGES[selection]
try:
    module = importlib.import_module(page_module_name)
    module = importlib.reload(module)
    module.app()
except ModuleNotFoundError as e:
    st.error(f"无法加载模块: {page_module_name}. 尚在开发中...")
    st.exception(e)
except AttributeError:
    st.error(f"模块 {page_module_name} 缺少 `app()` 函数。")
