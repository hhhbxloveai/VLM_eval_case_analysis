import pandas as pd
import os

def add_prefix_to_xlsx(input_file, output_file, prefix_path):
    try:
        # 读取 Excel 文件
        print(f"正在读取文件: {input_file}")
        df = pd.read_excel(input_file)

        # 将index字段拼接到image_path中
        df['image_path'] = prefix_path + df['id'].astype(str) + '.png'
        
        # 保存为新文件，不包含索引
        print(f"正在保存文件到: {output_file}")
        df.to_excel(output_file, index=False)
        print("处理完成！")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    input_xlsx = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/taichu_vl_moe_lora_251210_s2400/taichu_vl_moe/taichu_vl_moe_LogicVista_gpt4o-mini.xlsx'
    output_xlsx = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/taichu_vl_moe_lora_251210_s2400/taichu_vl_moe_for_check/taichu_vl_moe_LogicVista_gpt4o-mini.xlsx'
    prefix_path = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/LMUData/LogicVista/'
    add_prefix_to_xlsx(input_xlsx, output_xlsx, prefix_path)
