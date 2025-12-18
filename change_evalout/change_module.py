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

def create_file_config(model_prefix="taichu_vl_moe"):
    """
    创建文件配置字典
    
    Args:
        model_prefix (str): 模型名称前缀，默认为 "taichu_vl_moe"
    
    Returns:
        dict: 文件配置字典
    """
    return {
        f"{model_prefix}_AI2D_TEST_openai_result.xlsx": {
            "module": tool2_change_evalout_image_AI2D, 
            "folder": None  # 使用None表示不需要folder
        },
        f"{model_prefix}_ChartQA_TEST_result.xlsx": {
            "module": tool2_change_evalout_image_ChartQA, 
            "folder": "ChartQA"
        },
        f"{model_prefix}_DocVQA_VAL_result.xlsx": {
            "module": tool2_change_evalout_image_DocVQA, 
            "folder": "DocVQA"
        },
        f"{model_prefix}_LogicVista_gpt4o-mini.xlsx": {
            "module": tool2_change_evalout_image_LogicVista, 
            "folder": "LogicVista"
        },
        f"{model_prefix}_MathVerse_MINI_Vision_Only_gpt-4o-mini_score.xlsx": {
            "module": tool2_change_evalout_image_MathVerse, 
            "folder": "MathVerse_MINI_Vision_Only"
        },
        f"{model_prefix}_MathVision_gpt-4o-mini.xlsx": {
            "module": tool2_change_evalout_image_MathVision, 
            "folder": "MathVision"
        },
        f"{model_prefix}_MathVista_MINI_gpt-4o-mini.xlsx": {
            "module": tool2_change_evalout_image_MathVista, 
            "folder": "MathVista_MINI"
        },
        f"{model_prefix}_MMMU_DEV_VAL_openai_result.xlsx": {
            "module": tool2_change_evalout_image_MMMU, 
            "folder": "MMMU_DEV_VAL"
        },
        f"{model_prefix}_MMStar_openai_result.xlsx": {
            "module": tool2_change_evalout_image_MMStar, 
            "folder": "MMStar"
        },
        f"{model_prefix}_OCRBench_result.xlsx": {
            "module": tool2_change_evalout_image_OCRBench, 
            "folder": "OCRBench"
        },
        f"{model_prefix}_RealWorldQA_openai_result.xlsx": {
            "module": tool2_change_evalout_image_RealWorldQA, 
            "folder": "RealWorldQA"
        },
        f"{model_prefix}_WeMath_gpt4o-mini.xlsx": {
            "module": tool2_change_evalout_image_WeMath, 
            "folder": "WeMath"
        }
    }

# 创建默认配置
DEFAULT_FILE_CONFIG = create_file_config()

def ensure_dir(directory):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建输出目录: {directory}")

def process_xlsx_files(input_root_dir, output_root_dir, base_data_path, file_config=None):
    """
    处理Excel文件，为图片路径添加前缀
    
    Args:
        input_root_dir (str): 输入文件夹路径 (存放原始 xlsx 的目录)
        output_root_dir (str): 输出文件夹路径
        base_data_path (str): 基础数据路径 (图片文件夹的父目录)
        file_config (dict, optional): 文件配置字典，如果为None则使用默认配置
    
    Returns:
        None
    """
    # 如果没有提供配置，则使用默认配置
    if file_config is None:
        file_config = DEFAULT_FILE_CONFIG

    ensure_dir(output_root_dir)
    
    print(f"开始处理，共 {len(file_config)} 个任务...\n")

    for filename, config in file_config.items():
        # 1. 构建完整路径
        input_path = os.path.join(input_root_dir, filename)
        output_path = os.path.join(output_root_dir, filename)
        
        # 2. 构建该数据集特有的 prefix 路径
        if config['folder'] is None:
            # 对于不需要folder的数据集(如AI2D)，直接使用BASE_DATA_PATH
            specific_prefix_path = base_data_path
        else:
            # 对于需要folder的数据集，拼接路径，并确保以/结尾
            specific_prefix_path = os.path.join(base_data_path, config['folder']) + '/'

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

    print("所有任务处理完毕！")

# 导出接口
__all__ = [
    'process_xlsx_files',
    'create_file_config',  # 导出创建配置的函数
    'DEFAULT_FILE_CONFIG',
    'ensure_dir'
]
