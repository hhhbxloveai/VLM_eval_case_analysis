import streamlit as st
import pandas as pd
import os
from PIL import Image
import streamlit.components.v1 as components

# 1. 加载数据函数 (保持不变)
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        required_cols = ["index", "question", "A", "B", "C", "D", "answer", "image_path", "prediction", "hit"]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return None, f"Excel文件中缺少列: {missing}"
        df['index'] = df['index'].astype(str)
        return df, None
    except Exception as e:
        return None, str(e)

# ===========================
#      模块主入口函数
# ===========================
def run(server_file_path):
    
    prefix = "ai2d"

    # ===========================
    #   1. 在页面最顶部插入锚点
    # ===========================
    # 定义锚点 ID，并强制 CSS 为瞬间滚动（去掉 smooth 动画以追求最快速度）
    st.markdown(
        """
        <div id="top-anchor"></div>
        <style>
            html {
                scroll-behavior: auto !important;
            }
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
    filter_hit = st.sidebar.multiselect(
        "Hit 状态过滤 (AI2D)",
        options=df['hit'].unique(),
        default=df['hit'].unique(),
        key=f"{prefix}_filter_hit"
    )

    # --- 标题与搜索 ---
    st.title("📊 AI2D Viewer")

    col_search, _ = st.columns([1, 2])
    with col_search:
        search_query = st.text_input("🔍 按 Index 搜索", key=f"{prefix}_search_input", placeholder="输入 Index ID")

    # --- 数据过滤 ---
    is_search_mode = False
    if search_query:
        search_str = str(search_query).strip()
        df_display = df[df['index'] == search_str]
        is_search_mode = True
        if df_display.empty:
            st.warning(f"未找到 Index 为 '{search_str}' 的数据。")
    else:
        if filter_hit:
            df_display = df[df['hit'].isin(filter_hit)]
        else:
            df_display = df

    st.sidebar.markdown(f"**展示:** {len(df_display)} / {len(df)} 条")

    # ===========================
    #      分页核心逻辑
    # ===========================
    items_per_page = 10
    
    # 定义 Key
    page_key = f"{prefix}_page"
    key_top = f"{prefix}_jump_top"
    key_bottom = f"{prefix}_jump_bottom"
    # 注意：删除了 key_click_trigger，不再需要后端控制滚动

    # 1. 初始化 Session State
    if page_key not in st.session_state: st.session_state[page_key] = 0
    if key_top not in st.session_state: st.session_state[key_top] = 1
    if key_bottom not in st.session_state: st.session_state[key_bottom] = 1

    # 2. 计算总页数
    total_pages = max(1, (len(df_display) - 1) // items_per_page + 1)

    # 3. 同步状态函数
    def sync_input_boxes(new_page_index):
        """强制更新输入框在 session_state 中的值"""
        display_val = new_page_index + 1
        st.session_state[key_top] = display_val
        st.session_state[key_bottom] = display_val

    # 4. 边界检查
    if is_search_mode: 
        st.session_state[page_key] = 0
        sync_input_boxes(0)
    elif st.session_state[page_key] >= total_pages:
        st.session_state[page_key] = 0
        sync_input_boxes(0)
        
    current_page = st.session_state[page_key]

    # ===========================
    #      回调函数
    # ===========================
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

    # ===========================
    #      分页组件 UI
    # ===========================
    def render_pagination(location_suffix):
        if total_pages <= 1:
            # 单页时的回到顶部按钮
            if location_suffix == "bottom":
                st.markdown(
                    """
                    <div style="text-align: center; margin-top: 10px;">
                        <a href="#top-anchor" style="text-decoration: none;">
                            <button style="background:linear-gradient(135deg, #667eea, #764ba2); color:white; border:none; padding:8px 16px; border-radius:6px; cursor:pointer;">
                            ⬆️ 回到顶部
                            </button>
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            return

        current_input_key = key_top if location_suffix == "top" else key_bottom

        if location_suffix == "top": 
            c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
        else:
            c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 1, 1])

        with c1:
            st.button(
                "◀ 上一页", 
                disabled=(current_page == 0), 
                use_container_width=True,
                on_click=prev_page_callback,
                key=f"{prefix}_btn_prev_{location_suffix}" 
            )

        with c2:
            st.number_input(
                "Page Jump",
                min_value=1, 
                max_value=total_pages,
                key=current_input_key, 
                on_change=jump_page_callback,
                args=(current_input_key,),
                label_visibility="collapsed"
            )

        with c3:
            st.markdown(
                f"<div style='text-align:  center; padding-top: 10px; font-weight: bold;'>/ {total_pages} 页</div>", 
                unsafe_allow_html=True
            )

        with c4:
            st.button(
                "下一页 ▶", 
                disabled=(current_page >= total_pages - 1), 
                use_container_width=True,
                on_click=next_page_callback,
                key=f"{prefix}_btn_next_{location_suffix}"
            )

        if location_suffix == "bottom":
            with c5:
                # 这里的 href 直接指向锚点，速度最快
                st.markdown(
                    """
                    <a href="#top-anchor" style="text-decoration:none;" target="_self">
                        <div style="
                            display: flex; align-items: center; justify-content: center;
                            width: 100%; height: 100%; min-height: 38px;
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
        with st.container(border=True):
            col_img, col_text = st.columns([1, 2])
            
            with col_img:
                img_path = str(row['image_path']) 
                if os.path.exists(img_path):
                    try:
                        image = Image.open(img_path)
                        st.image(image, caption=f"File: {os.path.basename(img_path)}", use_container_width=True)
                    except Exception as e:
                        st.error(f"Image Error: {e}")
                else:  
                    st.warning(f"图片缺失: {img_path}")

            with col_text:
                header_color = "#198754" if row['hit'] else "#dc3545"
                hit_icon = "✅" if row['hit'] else "❌"
                
                st.markdown(f"<h3 style='color: {header_color}; margin-top: 0;'>Index: {row['index']} ({hit_icon} Hit:  {row['hit']})</h3>", unsafe_allow_html=True)
                st.markdown(f"**Q:** {row['question']}")
                
                options = {"A": row['A'], "B": row['B'], "C": row['C'], "D": row['D']}
                
                for opt, text in options.items():
                    is_answer = (str(opt) == str(row['answer']))
                    is_pred = (str(opt) == str(row['prediction']))
                    
                    base_style = "padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; border: 1px solid;"
                    
                    if is_answer: 
                        css = f"{base_style} background-color:  #d1e7dd; color: #0f5132; border-color: #badbcc;"
                        prefix_icon = "✅"
                    elif is_pred and not is_answer:  
                        css = f"{base_style} background-color:  #f8d7da; color: #842029; border-color: #f5c6cb;"
                        prefix_icon = "❌ <b>(Pred)</b> "
                    elif is_pred and is_answer:  
                        css = f"{base_style} background-color:  #d1e7dd; color: #0f5132; border-color: #badbcc;"
                        prefix_icon = "🎯 "
                    else:  
                        css = f"{base_style} background-color:  #f8f9fa; color: #333333; border-color: #dee2e6;"
                        prefix_icon = ""
                    
                    st.markdown(f"<div style='{css}'><b>{opt}:</b> {text}{prefix_icon}</div>", unsafe_allow_html=True)
                
                st.divider()
                st.markdown(
                    f"""<div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 14px; white-space: pre-wrap; word-break: break-word; color: #31333F;'><b>Prediction:</b> {row['prediction']}</div>""", 
                    unsafe_allow_html=True
                )

    # --- 底部翻页 ---
    st.divider()
    render_pagination("bottom")

    # =========================================================
    #  关键优化：在页面底部注入纯前端 JS
    #  这会找到所有翻页按钮，并强制绑定点击事件，实现瞬间滚动
    # =========================================================
    js_code = """
    <script>
    // 定义核心滚动逻辑：直接找 ID 进行跳转
    function instantScrollToTop() {
        var anchor = window.parent.document.getElementById('top-anchor');
        if (anchor) {
            // behavior: 'auto' 是瞬间跳转，'smooth' 是平滑滚动
            anchor.scrollIntoView({ behavior: 'auto', block: 'start' });
        }
    }

    // 绑定事件到 Streamlit 按钮上
    function bindButtons() {
        // 找到父级文档中的所有 button
        var buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(function(btn) {
            // 通过按钮文字判断是否为翻页按钮
            if (btn.innerText.includes("上一页") || btn.innerText.includes("下一页")) {
                // 移除旧的监听器防止重复
                btn.removeEventListener('click', instantScrollToTop);
                // 添加新的监听器，点击时立刻执行
                btn.addEventListener('click', instantScrollToTop);
            }
        });
    }

    // 1. 立即执行一次
    bindButtons();

    // 2. 由于 Streamlit 是动态渲染，可能按钮还没出来，稍微延迟再执行一次
    setTimeout(bindButtons, 500);

    // 3. (可选) 如果页面结构变化频繁，也可以使用 MutationObserver，
    // 但简单的 setTimeout 通常足够应对翻页场景
    </script>
    """
    
    # 将 JS 注入，高度设为0使其不可见
    components.html(js_code, height=0)