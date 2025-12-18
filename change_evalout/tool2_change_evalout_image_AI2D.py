import pandas as pd
import os

def add_prefix_to_xlsx(input_file, output_file,prefix_path):
    # 定义要添加的前缀路径

    try:
        # 读取 Excel 文件
        print(f"正在读取文件: {input_file}")
        df = pd.read_excel(input_file)

        # 检查是否存在 image_path 列
        if 'image_path' not in df.columns:
            print("错误: 文件中没找到 'image_path' 这一列。")
            return

        # 处理路径拼接
        # 使用 os.path.join 可以自动处理路径分隔符，但为了强制使用 Linux 风格的 '/'，
        # 这里使用字符串拼接更为稳妥（防止在 Windows 运行代码时生成反斜杠）
        
        # 逻辑：前缀 + '/' + 原有路径 (同时将内容转为字符串防止报错)
        # 如果你原有的路径里已经包含了文件名，直接拼接即可
        df['image_path'] = df['image_path'].apply(
            lambda x: f"{prefix_path}/{str(x).lstrip('/')}" if pd.notna(x) else x
        )

        # 保存为新文件，不包含索引
        print(f"正在保存文件到: {output_file}")
        df.to_excel(output_file, index=False)
        print("处理完成！")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    input_xlsx = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/taichu_vl_moe_lora_251210_s2400/taichu_vl_moe/taichu_vl_moe_AI2D_TEST_openai_result.xlsx'       # 你的输入文件名
    output_xlsx = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/taichu_vl_moe_lora_251210_s2400/taichu_vl_moe_for_check/taichu_vl_moe_AI2D_TEST_openai_result.xlsx'    # 结果保存的文件名
    prefix_path = '/mnt/lustre/houbingxi/1212_moe_eval_badcase/LMUData'
    add_prefix_to_xlsx(input_xlsx, output_xlsx,prefix_path)