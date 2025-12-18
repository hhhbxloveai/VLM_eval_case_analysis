import pandas as pd
import os
import ast  # 用于安全地评估字符串形式的列表

def add_prefix_to_xlsx(input_file, output_file, prefix_path):
    try:
        # 读取 Excel 文件，指定dtype为object以保持原始数据类型
        print(f"正在读取文件: {input_file}")
        df = pd.read_excel(input_file, dtype={'image_path': object})

        # 检查是否存在 image_path 列
        if 'image_path' not in df.columns:
            print("错误: 文件中没找到 'image_path' 这一列。")
            return

        # 处理路径拼接
        def process_path(x):
            if pd.isna(x):
                return x
            
            # 如果是字符串形式的列表，先转换为列表
            if isinstance(x, str):
                try:
                    x = ast.literal_eval(x)
                except:
                    # 如果转换失败，说明是普通字符串
                    return f"{prefix_path}/{str(x).lstrip('/')}"
            
            # 如果是列表类型
            if isinstance(x, list):
                return [f"{prefix_path}/{str(item).lstrip('/')}" for item in x]
            
            # 如果是单个路径
            return f"{prefix_path}/{str(x).lstrip('/')}"

        df['image_path'] = df['image_path'].apply(process_path)

        # 保存为新文件，不包含索引
        print(f"正在保存文件到: {output_file}")
        df.to_excel(output_file, index=False)
        print("处理完成！")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    input_xlsx = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/taichu_vl_moe_lora_251210_s2400/taichu_vl_moe/taichu_vl_moe_MMMU_DEV_VAL_openai_result.xlsx'
    output_xlsx = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/taichu_vl_moe_lora_251210_s2400/taichu_vl_moe_for_check/taichu_vl_moe_MMMU_DEV_VAL_openai_result.xlsx'
    prefix_path = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/LMUData/MMMU_DEV_VAL/'
    add_prefix_to_xlsx(input_xlsx, output_xlsx, prefix_path)
