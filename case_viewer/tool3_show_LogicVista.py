import streamlit as st
import pandas as pd
import os
from PIL import Image
import streamlit.components.v1 as components

# ===========================
#      配置区域
# ===========================
REQUIRED_COLS = ["index", "question", "answer", "prediction", "res", "image_path", "hit"]

# 1. 加载数据函数
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        
        # 1. 检查必要列
        missing = [c for c in REQUIRED_COLS if c not in df.columns]
        if missing:
            return None, f"Excel文件中缺少列: {missing}"
        
        # 2. 数据预处理
        # 确保 index 列存在并转为字符串（用于搜索）
        if 'index' in df.columns:
            df['index'] = df['index'].astype(str).str.strip()
            
        return df, None
    except Exception as e:
        return None, str(e)

# ===========================
#      模块主入口函数
# ===========================
def run(server_file_path):
    
    # 唯一前缀
    prefix = "logicvista"

    # ===========================
    #   1. 在页面最顶部插入锚点
    # ===========================
    st.markdown(
        """
        <div id="top-anchor"></div>
        <style>
            html { scroll-behavior: auto !important; }
        </style>
        """, 
        unsafe_allow_html=True
    )

    # --- 文件检查 ---
    if not os.path.exists(server_file_path):
        st.error(f"⚠️ 文件未找到: {server_file_path}")
        return 

    df, error_msg = load_data(server_file_path)
    if error_msg:
        st.error(f"❌ 读取失败: {error_msg}")
        return

    # --- 侧边栏 ---
    st.sidebar.divider()
    
    # 处理 hit 列可能存在的不同类型（布尔值或数字）
    if 'hit' in df.columns:
        if df['hit'].dtype == bool:
            hit_options = [True, False]
        else:
            hit_options = sorted(df['hit'].unique().tolist())
            
        filter_hit = st.sidebar.multiselect(
            "Hit 状态过滤 (LogicVista)",
            options=hit_options,
            default=hit_options,
            key=f"{prefix}_filter_hit"
        )
    else:
        filter_hit = None

    # --- 标题与搜索区域 ---
    st.title("📊 LogicVista Viewer")

    col_search, _ = st.columns([1, 2])
    with col_search:
        search_query = st.text_input("🔍 按 Index 搜索", key=f"{prefix}_search_input", placeholder="输入 Index ID")

    # --- 数据过滤逻辑 ---
    is_search_mode = False
    
    # 1. 搜索优先
    if search_query:
        search_str = str(search_query).strip()
        df_display = df[df['index'] == search_str]
        is_search_mode = True
        if df_display.empty:
            st.warning(f"未找到 Index 为 '{search_str}' 的数据。")
    # 2. 侧边栏过滤
    elif filter_hit is not None:
        df_display = df[df['hit'].isin(filter_hit)]
    else:
        df_display = df

    st.sidebar.markdown(f"**展示:** {len(df_display)} / {len(df)} 条")

    # ===========================
    #      分页核心逻辑
    # ===========================
    items_per_page = 10
    
    page_key = f"{prefix}_page"
    key_top = f"{prefix}_jump_top"
    key_bottom = f"{prefix}_jump_bottom"

    if page_key not in st.session_state: st.session_state[page_key] = 0
    if key_top not in st.session_state: st.session_state[key_top] = 1
    if key_bottom not in st.session_state: st.session_state[key_bottom] = 1

    total_pages = max(1, (len(df_display) - 1) // items_per_page + 1)

    def sync_input_boxes(new_page_index):
        display_val = new_page_index + 1
        st.session_state[key_top] = display_val
        st.session_state[key_bottom] = display_val

    # 边界检查
    if is_search_mode: 
        st.session_state[page_key] = 0
        sync_input_boxes(0)
    elif st.session_state[page_key] >= total_pages:
        st.session_state[page_key] = 0
        sync_input_boxes(0)
        
    current_page = st.session_state[page_key]

    # 回调函数
    def prev_page_callback():
        if st.session_state[page_key] > 0:
            st.session_state[page_key] -= 1
            sync_input_boxes(st.session_state[page_key])

    def next_page_callback():
        if st.session_state[page_key] < total_pages - 1:
            st.session_state[page_key] += 1
            sync_input_boxes(st.session_state[page_key])

    def jump_page_callback(source_key):
        val = st.session_state[source_key] 
        new_page = val - 1
        if 0 <= new_page < total_pages: 
            st.session_state[page_key] = new_page
            sync_input_boxes(new_page)

    # 渲染翻页组件
    def render_pagination(location_suffix):
        if total_pages <= 1:
            if location_suffix == "bottom":
                st. markdown("""<div style="text-align: center; margin-top: 10px;"><a href="#top-anchor" style="text-decoration: none;"><button style="background:linear-gradient(135deg, #667eea, #764ba2); color:white; border:none; padding:8px 16px; border-radius: 6px; cursor:pointer;">⬆️ 回到顶部</button></a></div>""", unsafe_allow_html=True)
            return

        current_input_key = key_top if location_suffix == "top" else key_bottom
        
        # 修复1:  使用与第一份代码相同的动态列布局
        if location_suffix == "top": 
            c1, c2, c3, c4 = st. columns([1, 2, 1, 1])
        else:
            c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 1, 1])

        with c1:
            st.button("◀ 上一页", disabled=(current_page == 0), use_container_width=True, on_click=prev_page_callback, key=f"{prefix}_btn_prev_{location_suffix}")
        with c2:
            st.number_input("Page Jump", min_value=1, max_value=total_pages, key=current_input_key, on_change=jump_page_callback, args=(current_input_key,), label_visibility="collapsed")
        with c3:
            st.markdown(f"<div style='text-align: center; padding-top:  10px; font-weight:  bold;'>/ {total_pages} 页</div>", unsafe_allow_html=True)
        with c4:
            st.button("下一页 ▶", disabled=(current_page >= total_pages - 1), use_container_width=True, on_click=next_page_callback, key=f"{prefix}_btn_next_{location_suffix}")
        
        # 修复2: 只在底部渲染 Top 按钮，并修复点击区域
        if location_suffix == "bottom":
            with c5:
                st.markdown(
                    """
                    <a href="#top-anchor" style="text-decoration:none; display: block;" target="_self">
                        <div style="
                            display: flex; align-items: center; justify-content: center;
                            width: 100%; min-height: 38px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white; border-radius: 6px; font-weight: 500; font-size: 14px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.2); cursor: pointer;">
                            ⬆️ Top
                        </div>
                    </a>
                    """,
                    unsafe_allow_html=True
                )
    # --- 顶部翻页 ---
    render_pagination("top")

    # ===========================
    #      列表内容展示
    # ===========================
    start_idx = current_page * items_per_page
    end_idx = start_idx + items_per_page
    current_batch = df_display.iloc[start_idx:end_idx]

    if current_batch.empty and not is_search_mode:
        st.info("当前过滤条件下无数据。")

    for idx, row in current_batch.iterrows():
        # 外层容器
        with st.container(border=True):
            col_img, col_text = st.columns([1, 2])
            
            # --- 图片列 ---
            with col_img:
                img_path = str(row['image_path'])
                if os.path.exists(img_path):
                    try:
                        image = Image.open(img_path)
                        st.image(image, caption=f"File: {os.path.basename(img_path)}", use_container_width=True)
                    except Exception as e:
                        st.error(f"Image Error: {e}")
                else:
                    if img_path and img_path.lower() != 'nan':
                        st.warning(f"图片缺失: {img_path}")
                    else:
                        st.info("无关联图片")

            # --- 文本列 ---
            with col_text:
                # 1. 标题 (Index + Hit)
                is_hit = bool(row['hit'])
                header_color = "#198754" if is_hit else "#dc3545" # Green / Red
                hit_icon = "✅" if is_hit else "❌"
                
                st.markdown(f"<h3 style='color: {header_color}; margin-top:0;'>Index: {row['index']} ({hit_icon} Hit: {row['hit']})</h3>", unsafe_allow_html=True)
                
                # 2. 问题
                st.markdown(f"**Question:**")
                st.markdown(f"> {row['question']}")
                
                st.divider()

                # 3. 答案对比区域 (使用列布局并排展示)
                c_ans, c_res = st.columns(2)
                
                with c_ans:
                    st.info(f"**Standard Answer:**\n\n{row['answer']}")
                
                with c_res:
                    # 如果 Hit 为 True，用绿色，否则用红色
                    if is_hit:
                        st.success(f"**Model Res (Extracted):**\n\n{row['res']}")
                    else:
                        st.error(f"**Model Res (Extracted):**\n\n{row['res']}")

                # 4. 完整的预测过程 (通常比较长，放在折叠面板里)
                with st.expander("查看完整模型输出 (Prediction / Chain of Thought)"):
                    st.code(row['prediction'], language="text", wrap_lines=True)

    # --- 底部翻页 ---
    st.divider()
    render_pagination("bottom")

    # ===========================
    #      JS 注入
    # ===========================
    js_code = """
    <script>
    function instantScrollToTop() {
        var anchor = window.parent.document.getElementById('top-anchor');
        if (anchor) { anchor.scrollIntoView({ behavior: 'auto', block: 'start' }); }
    }
    function bindButtons() {
        var buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(function(btn) {
            if (btn.innerText.includes("上一页") || btn.innerText.includes("下一页")) {
                btn.removeEventListener('click', instantScrollToTop);
                btn.addEventListener('click', instantScrollToTop);
            }
        });
    }
    bindButtons();
    setTimeout(bindButtons, 500);
    </script>
    """
    components.html(js_code, height=0)