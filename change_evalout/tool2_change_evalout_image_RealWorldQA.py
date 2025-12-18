import pandas as pd
import os

def add_prefix_to_xlsx(input_file, output_file,prefix_path):
    # 定义要添加的前缀路径

    try:
        # 读取 Excel 文件
        print(f"正在读取文件: {input_file}")
        df = pd.read_excel(input_file)
        df['image_path'] = prefix_path + df['index'].astype(str) + '.png'

        # 保存为新文件，不包含索引
        print(f"正在保存文件到: {output_file}")
        df.to_excel(output_file, index=False)
        print("处理完成！")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    input_xlsx = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/taichu_vl_moe_lora_251210_s2400/taichu_vl_moe/taichu_vl_moe_RealWorldQA_openai_result.xlsx'       # 你的输入文件名
    output_xlsx = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/taichu_vl_moe_lora_251210_s2400/taichu_vl_moe_for_check/taichu_vl_moe_RealWorldQA_openai_result.xlsx'    # 结果保存的文件名
    prefix_path = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/LMUData/RealWorldQA/'
    add_prefix_to_xlsx(input_xlsx, output_xlsx,prefix_path)