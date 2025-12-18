import streamlit as st
import pandas as pd
import os
from PIL import Image
import ast  # 保留：用于解析字符串列表 "['a.jpg', 'b.jpg']"
import streamlit.components.v1 as components

# ===========================
#      配置区域
# ===========================
# 核心必须存在的列 (选项列 A-I 在展示时动态判断)
REQUIRED_COLS = ["index", "question", "answer", "image_path", "prediction", "hit"]

# 1. 加载数据函数
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        
        # 1. 检查必要列
        missing = [c for c in REQUIRED_COLS if c not in df.columns]
        if missing:
            return None, f"Excel文件中缺少核心列: {missing}"
        
        # 2. 确保 index 列存在并转为字符串（用于搜索）
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
    prefix = "mmmu"

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
    
    # Hit 过滤器
    if 'hit' in df.columns:
        filter_hit = st.sidebar.multiselect(
            "Hit 状态过滤 (MMMU)",
            options=df['hit'].unique(),
            default=df['hit'].unique(),
            key=f"{prefix}_filter_hit"
        )
    else:
        filter_hit = None

    # --- 标题与搜索区域 ---
    st.title("📊 MMMU Viewer")

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

    # MMMU 特有的选项列定义
    OPTION_COLS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

    for idx, row in current_batch.iterrows():
        with st.container(border=True):
            col_img, col_text = st.columns([1, 2])
            
            # --- 图片列处理 (MMMU 特有：支持单图或列表) ---
            with col_img:
                raw_path = row.get('image_path', '')
                image_list = []
                
                # 1. 尝试解析列表字符串 "['a.jpg', 'b.jpg']"
                try:
                    # 如果本身就是list对象
                    if isinstance(raw_path, list):
                        image_list = raw_path
                    # 如果是字符串，尝试 eval 解析
                    elif isinstance(raw_path, str):
                        clean_str = raw_path.strip()
                        if clean_str.startswith("[") and clean_str.endswith("]"):
                            image_list = ast.literal_eval(clean_str)
                        else:
                            image_list = [clean_str]
                    else:
                        image_list = [] # 空或NaN
                except:
                    # 解析失败，当作普通字符串路径处理
                    image_list = [str(raw_path)]

                # 2. 循环展示图片
                if not image_list:
                    st.warning("无图片路径")
                else:
                    for i, img_p in enumerate(image_list):
                        img_p_str = str(img_p).strip()
                        if os.path.exists(img_p_str):
                            try:
                                image = Image.open(img_p_str)
                                # 如果有多张图，显示 Image 1, Image 2...
                                caption_prefix = f"[{i+1}/{len(image_list)}] " if len(image_list) > 1 else ""
                                st.image(image, caption=f"{caption_prefix}{os.path.basename(img_p_str)}", use_container_width=True)
                            except Exception as e:
                                st.error(f"Error loading {os.path.basename(img_p_str)}")
                        else:
                            # 避免空字符串报错
                            if img_p_str and img_p_str.lower() != 'nan':
                                st.warning(f"⚠️ 图片缺失: {img_p_str}")

            # --- 文本列处理 ---
            with col_text:
                header_color = "#198754" if row['hit'] else "#dc3545" 
                hit_icon = "✅" if row['hit'] else "❌"
                
                st.markdown(f"<h3 style='color: {header_color}; margin-top:0;'>Index: {row['index']} ({hit_icon} Hit: {row['hit']})</h3>", unsafe_allow_html=True)
                st.markdown(f"**Q:** {row['question']}")
                
                st.divider()
                
                # --- 动态渲染选项 (A - I) ---
                for opt in OPTION_COLS:
                    # 检查列是否存在且内容不为空
                    if opt in df.columns and pd.notna(row[opt]):
                        text = row[opt]
                        
                        # 答案/预测判定逻辑
                        is_answer = (str(opt) == str(row['answer']))
                        is_pred = (str(opt) == str(row['prediction']))
                        
                        # 样式逻辑
                        base_style = "padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; border: 1px solid;"
                        
                        if is_answer:
                            css = f"{base_style} background-color: #d1e7dd; color: #0f5132; border-color: #badbcc;"
                            prefix_icon = "✅"
                        elif is_pred and not is_answer:
                            css = f"{base_style} background-color: #f8d7da; color: #842029; border-color: #f5c6cb;"
                            prefix_icon = "❌ <b>(Pred)</b> "
                        elif is_pred and is_answer: 
                            css = f"{base_style} background-color: #d1e7dd; color: #0f5132; border-color: #badbcc;"
                            prefix_icon = "🎯 "
                        else:
                            css = f"{base_style} background-color: #f8f9fa; color: #333333; border-color: #dee2e6;"
                            prefix_icon = ""
                        
                        st.markdown(f"<div style='{css}'><b>{opt}:</b> {text} {prefix_icon}</div>", unsafe_allow_html=True)
                
                # --- 模型输出 (折叠) ---
                st.write("") # Spacer
                with st.expander(f"👁️ 查看完整模型输出 (Prediction)", expanded=False):
                    st.info(row['prediction'])

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