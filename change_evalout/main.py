import os
import pandas as pd

# 1. 导入所有工具模块
import tool2_change_evalout_image_AI2D
import tool2_change_evalout_image_ChartQA
import tool2_change_evalout_image_DocVQA
import tool2_change_evalout_image_LogicVista
import tool2_change_evalout_image_MathVerse
import tool2_change_evalout_image_MathVision
import tool2_change_evalout_image_MathVista
import tool2_change_evalout_image_MMMU
import tool2_change_evalout_image_MMStar
import tool2_change_evalout_image_OCRBench
import tool2_change_evalout_image_RealWorldQA
import tool2_change_evalout_image_WeMath


# ================= 核心映射配置 =================
FILE_CONFIG = {
    "taichu_vl_moe_AI2D_TEST_openai_result.xlsx": {
        "module": tool2_change_evalout_image_AI2D, 
        "folder": None  # 使用None表示不需要folder
    },
    "taichu_vl_moe_ChartQA_TEST.xlsx": {
        "module": tool2_change_evalout_image_ChartQA, 
        "folder": "ChartQA"
    },
    "taichu_vl_moe_DocVQA_VAL.xlsx": {
        "module": tool2_change_evalout_image_DocVQA, 
        "folder": "DocVQA"
    },
    "taichu_vl_moe_LogicVista_gpt4o-mini.xlsx": {
        "module": tool2_change_evalout_image_LogicVista, 
        "folder": "LogicVista"
    },
    "taichu_vl_moe_MathVerse_MINI_Vision_Only_gpt-4o-mini_score.xlsx": {
        "module": tool2_change_evalout_image_MathVerse, 
        "folder": "MathVerse_MINI_Vision_Only"
    },
    "taichu_vl_moe_MathVision_gpt-4o-mini.xlsx": {
        "module": tool2_change_evalout_image_MathVision, 
        "folder": "MathVision"
    },
    "taichu_vl_moe_MathVista_MINI_gpt-4o-mini.xlsx": {
        "module": tool2_change_evalout_image_MathVista, 
        "folder": "MathVista_MINI"
    },
    "taichu_vl_moe_MMMU_DEV_VAL_openai_result.xlsx": {
        "module": tool2_change_evalout_image_MMMU, 
        "folder": "MMMU_DEV_VAL"
    },
    "taichu_vl_moe_MMStar_openai_result.xlsx": {
        "module": tool2_change_evalout_image_MMStar, 
        "folder": "MMStar"
    },
    "taichu_vl_moe_OCRBench.xlsx": {
        "module": tool2_change_evalout_image_OCRBench, 
        "folder": "OCRBench"
    },
    "taichu_vl_moe_RealWorldQA_openai_result.xlsx": {
        "module": tool2_change_evalout_image_RealWorldQA, 
        "folder": "RealWorldQA"
    },
    "taichu_vl_moe_WeMath_gpt4o-mini.xlsx": {
        "module": tool2_change_evalout_image_WeMath, 
        "folder": "WeMath"
    }
}

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建输出目录: {directory}")

def run_processing(INPUT_ROOT_DIR, OUTPUT_ROOT_DIR, BASE_DATA_PATH):
    ensure_dir(OUTPUT_ROOT_DIR)
    
    print(f"开始处理，共 {len(FILE_CONFIG)} 个任务...\n")

    for filename, config in FILE_CONFIG.items():
        # 1. 构建完整路径
        input_path = os.path.join(INPUT_ROOT_DIR, filename)
        output_path = os.path.join(OUTPUT_ROOT_DIR, filename)
        
        # 2. 构建该数据集特有的 prefix 路径
        if config['folder'] is None:
            # 对于不需要folder的数据集(如AI2D)，直接使用BASE_DATA_PATH
            specific_prefix_path = BASE_DATA_PATH
        else:
            # 对于需要folder的数据集，拼接路径，并确保以/结尾
            specific_prefix_path = os.path.join(BASE_DATA_PATH, config['folder']) + '/'

        # 3. 检查输入文件是否存在
        if not os.path.exists(input_path):
            print(f"[跳过] 找不到文件: {filename}")
            continue

        # 4. 调用对应的模块进行处理
        module = config['module']
        
        print(f"正在处理: {filename}")
        print(f"  - 对应模块: {module.__name__}")
        print(f"  - 图片前缀: {specific_prefix_path}")

        try:
            # 调用模块中的 add_prefix_to_xlsx 函数
            module.add_prefix_to_xlsx(input_path, output_path, specific_prefix_path)
            print(f"  - [成功] 已保存至: {output_path}\n")
        except Exception as e:
            print(f"  - [失败] 处理出错: {e}\n")

if __name__ == "__main__":
    # ================= 配置区域 =================

    # 输入文件夹路径 (存放原始 xlsx 的目录)
    INPUT_ROOT_DIR = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/taichu_vl_moe_lora_251210_s2400/taichu_vl_moe'

    # 输出文件夹路径
    OUTPUT_ROOT_DIR = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/taichu_vl_moe_lora_251210_s2400/taichu_vl_moe_for_check'

    # 基础数据路径 (图片文件夹的父目录)
    BASE_DATA_PATH = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/LMUData'

    run_processing(INPUT_ROOT_DIR, OUTPUT_ROOT_DIR, BASE_DATA_PATH)
    print("所有任务处理完毕！")
