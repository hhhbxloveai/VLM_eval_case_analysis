import streamlit as st
import os
import sys
import time # 引入time模块用于模拟刷新或延时

# ... (前文获取路径的代码保持不变) ...
current_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_path)
project_root = os.path.dirname(current_dir)

# 1. 将项目根目录添加到 sys.path (保持不变)
if project_root not in sys.path:
    sys.path.append(project_root)

# ==========================================
# 2. 【关键修改】将 change_evalout 子目录也添加到 sys.path
# ==========================================
# 假设 change_evalout 文件夹在 project_root 下
change_evalout_dir = os.path.join(project_root, "change_evalout")

if os.path.exists(change_evalout_dir) and change_evalout_dir not in sys.path:
    sys.path.append(change_evalout_dir)

# 3. 现在导入模块，内部的 sibling import 就能正常工作了
from change_evalout import change_module 

# 1. 设置页面配置
st.set_page_config(layout="wide", page_title="VLM-Dataset Case Viewer")

# 2. 导入子模块
import tool3_show_AI2D
import tool3_show_ChartQA
import tool3_show_DocVQA
import tool3_show_LogicVista
import tool3_show_MathVerse
import tool3_show_MathVision
import tool3_show_MathVista
import tool3_show_MMMU
import tool3_show_MMStar
import tool3_show_OCRBench
import tool3_show_RealWorldQA
import tool3_show_WeMath

# 3. 定义数据集配置
DATASETS = {
    "AI2D":         {"module": tool3_show_AI2D,       "keyword": "AI2D"},
    "ChartQA":      {"module": tool3_show_ChartQA,    "keyword": "ChartQA"},
    "DocVQA":       {"module": tool3_show_DocVQA,     "keyword": "DocVQA"},
    "LogicVista":   {"module": tool3_show_LogicVista, "keyword": "LogicVista"},
    "MathVerse":    {"module": tool3_show_MathVerse,  "keyword": "MathVerse"},
    "MathVision":   {"module": tool3_show_MathVision, "keyword": "MathVision"},
    "MathVista":    {"module": tool3_show_MathVista,  "keyword": "MathVista"},
    "MMMU":         {"module": tool3_show_MMMU,       "keyword": "MMMU"},
    "MMStar":       {"module": tool3_show_MMStar,     "keyword": "MMStar"},
    "OCRBench":     {"module": tool3_show_OCRBench,   "keyword": "OCRBench"},
    "RealWorldQA":  {"module": tool3_show_RealWorldQA,"keyword": "RealWorldQA"},
    "WeMath":       {"module": tool3_show_WeMath,     "keyword": "WeMath"},
}

# ===========================
#      侧边栏配置
# ===========================
st.sidebar.title("🗂️ 数据集与路径")

# 1. 原始文件夹路径配置
default_raw_folder = "Your Eval Out Folder Path Here----taichu_vl_moe"
raw_input_path = st.sidebar.text_input("📂 原始数据文件夹 (Raw):", value=default_raw_folder)
folder_name = os.path.basename(raw_input_path.rstrip(os.sep))

# 计算预期的检查文件夹路径 (添加 _for_check 后缀)
clean_raw_path = raw_input_path.rstrip(os.sep)
processed_folder_path = "/mnt/lustre/houbingxi/1212_moe_eval_badcase/tmp_data" + f"{clean_raw_path}_for_check"
File_Config = change_module.create_file_config(folder_name)
# ===========================
#      处理逻辑控制 (核心修改)
# ===========================
# 检查目标文件夹是否存在
target_exists = os.path.exists(processed_folder_path) and os.path.isdir(processed_folder_path)

if target_exists:
    # --- 情况 A: 文件夹已存在 ---
    st.sidebar.success(f"✅ 检测到目标文件夹已存在，直接使用。")
    st.sidebar.caption(f"路径: `{os.path.basename(processed_folder_path)}`")
    
    # (可选) 如果用户想强制覆盖，可以提供一个折叠的按钮，防止误触
    with st.sidebar.expander("🛠️ 需要重新生成？"):
        if st.button("🔄 强制重新格式转换"):
            with st.spinner("正在重新处理文件..."):
                try:
                    change_module.process_xlsx_files(raw_input_path, processed_folder_path, '/mnt/lustre/houbingxi/1212_moe_eval_badcase/LMUData', File_Config)
                    st.success("重新处理完成！")
                    time.sleep(1)
                    st.rerun() # 刷新页面
                except Exception as e:
                    st.error(f"错误: {e}")

else:
    # --- 情况 B: 文件夹不存在 ---
    st.sidebar.warning(f"⚠️ 目标文件夹尚未生成")
    st.sidebar.caption(f"预期路径: `{os.path.basename(processed_folder_path)}`")
    
    if st.sidebar.button("🚀 执行格式转换生成"):
        if os.path.exists(raw_input_path):
            with st.spinner("正在调用 change_module 处理文件..."):
                try:
                    change_module.process_xlsx_files(raw_input_path,processed_folder_path,'/mnt/lustre/houbingxi/1212_moe_eval_badcase/LMUData', File_Config)
                    st.sidebar.success("处理成功！正在加载...")
                    time.sleep(1)
                    st.rerun() # 刷新页面以进入“情况A”
                except Exception as e:
                    st.sidebar.error(f"处理失败: {e}")
                    st.exception(e)
        else:
            st.sidebar.error("❌ 原始路径不存在，无法转换。")

# 无论哪种情况，后续逻辑都使用 processed_folder_path
folder_path = processed_folder_path

st.sidebar.markdown("---")

# 初始化 session state
if "last_folder_path" not in st.session_state:
    st.session_state.last_folder_path = None

# 4. 选择数据集
selected_dataset_name = st.sidebar.selectbox(
    "请选择要查看的数据集:",
    options=list(DATASETS.keys())
)

current_config = DATASETS[selected_dataset_name]
target_keyword = current_config["keyword"]

# ===========================
#      自动匹配逻辑
# ===========================
auto_suggested_path = ""
match_status_msg = ""

# 在 folder_path (即 _for_check 目录) 中查找文件
if os.path.exists(folder_path) and os.path.isdir(folder_path):
    all_files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx") and not f.startswith("~$")]
    matched_files = [f for f in all_files if target_keyword.lower() in f.lower()]
    
    if len(matched_files) >= 1:
        auto_suggested_path = os.path.join(folder_path, matched_files[0])
        match_status_msg = f"✅ 自动匹配: {matched_files[0]}"
        if len(matched_files) > 1:
            match_status_msg = f"⚠️ 发现 {len(matched_files)} 个相关文件，默认加载第一个。"
    else:
        match_status_msg = f"❌ 文件夹中未找到包含 '{target_keyword}' 的文件"
else:
    # 如果代码走到这里，说明 target_exists 为 False 且用户还没点生成
    match_status_msg = "⚠️ 等待生成数据文件夹..."

if match_status_msg:
    st.sidebar.caption(match_status_msg)

# ===========================
#      状态同步
# ===========================
# 生成组件的唯一 Key
input_key = f"path_input_{selected_dataset_name}"

# 初始化 session state 中的文件路径
if input_key not in st.session_state:
    st.session_state[input_key] = auto_suggested_path

# 如果文件夹路径发生变化，更新文件路径
if folder_path != st.session_state.last_folder_path:
    st.session_state[input_key] = auto_suggested_path
    st.session_state.last_folder_path = folder_path

# ===========================
#      文件路径输入框
# ===========================
final_file_path = st.sidebar.text_input(
    "📄 Excel 文件路径 (可手动修改):",
    key=input_key
)

# ===========================
#      路由分发
# ===========================
if final_file_path and os.path.exists(final_file_path):
    try:
        current_config["module"].run(final_file_path)
    except Exception as e:
        st.title(f"📊 {selected_dataset_name} Viewer")
        st.error("运行模块时发生错误:")
        st.exception(e)
else:
    st.title(f"📊 {selected_dataset_name} Viewer")
    if not final_file_path:
        if not target_exists:
            st.info("👈 请在左侧点击【执行格式转换生成】以准备数据。")
        else:
            st.info(f"等待加载文件... 请检查 {selected_dataset_name} 是否存在于文件夹中。")
    else:
        st.warning(f"⚠️ 文件不存在: {final_file_path}")