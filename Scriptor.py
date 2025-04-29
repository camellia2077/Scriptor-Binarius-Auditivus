# -*- coding: utf-8 -*-

import sys
import os

def text_to_binary_string(text, encoding='utf-8'):
    """
    将文本字符串转换为其二进制表示形式（每个字节用8位二进制数表示，用空格分隔）。

    Args:
        text (str): 输入的文本字符串。
        encoding (str): 用于将文本编码为字节的编码方式，默认为 'utf-8'。

    Returns:
        str: 表示文本的二进制字符串，每个字节之间用空格分隔。
              如果输入为空，则返回空字符串。
    """
    if not text:
        return ""
    try:
        # 1. 将文本字符串根据指定编码转换为字节序列 (bytes object)
        byte_array = text.encode(encoding)

        # 2. 将每个字节转换为8位的二进制字符串
        #    - bin(byte) 返回 "0bxxxxxx" 格式的字符串
        #    - [2:] 去掉前缀 "0b"
        #    - zfill(8) 确保每个字节都表示为8位，不足的前面补0
        binary_strings = [bin(byte)[2:].zfill(8) for byte in byte_array]

        # 3. 用空格连接所有字节的二进制字符串
        return ' '.join(binary_strings)
    except Exception as e:
        print(f"转换过程中发生错误: {e}")
        return None

def process_file(input_filepath='input.txt', output_filepath='output.txt', encoding='utf-8'):
    """
    读取输入文件，将其内容转换为二进制字符串，并写入输出文件。

    Args:
        input_filepath (str): 输入文本文件的路径。
        output_filepath (str): 输出二进制字符串文件的路径。
        encoding (str): 读取和处理文件时使用的编码。
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_filepath):
            print(f"错误：输入文件 '{input_filepath}' 不存在。")
            # 创建一个空的 input.txt 文件作为示例
            with open(input_filepath, 'w', encoding=encoding) as f:
                f.write("请在这里输入你想转换的文字，比如：Hello 世界！")
            print(f"已创建示例输入文件 '{input_filepath}'。请填充内容后重新运行。")
            return

        # 读取输入文件内容
        print(f"正在读取文件 '{input_filepath}' (使用 {encoding} 编码)...")
        with open(input_filepath, 'r', encoding=encoding) as infile:
            original_text = infile.read()

        if not original_text:
            print(f"警告：输入文件 '{input_filepath}' 为空。")
            binary_output = ""
        else:
             # 将读取的文本转换为二进制字符串
            print("正在将文本转换为二进制...")
            binary_output = text_to_binary_string(original_text, encoding)

        if binary_output is not None:
            # 将二进制字符串写入输出文件
            print(f"正在将二进制结果写入文件 '{output_filepath}'...")
            with open(output_filepath, 'w', encoding='ascii') as outfile: # 二进制字符串本身只包含0, 1和空格，用ascii写入即可
                outfile.write(binary_output)
            print(f"成功！二进制字符串已保存到 '{output_filepath}'。")
            print(f"\n原始文本 ({len(original_text)} 字符):\n{original_text[:100]}{'...' if len(original_text) > 100 else ''}") # 显示部分原始文本
            print(f"\n二进制表示 (前 100 个字符):\n{binary_output[:100]}{'...' if len(binary_output) > 100 else ''}") # 显示部分二进制结果

    except FileNotFoundError:
        # 这个理论上在上面的 os.path.exists 检查后不会触发，但保留以防万一
        print(f"错误：输入文件 '{input_filepath}' 未找到。")
    except UnicodeDecodeError:
        print(f"错误：无法使用 '{encoding}' 编码解码文件 '{input_filepath}'。")
        print(f"请确保文件的实际编码与指定的 '{encoding}' 编码一致。")
        print("常见的编码有 'utf-8', 'gbk' (简体中文), 'big5' (繁体中文) 等。")
    except IOError as e:
        print(f"读写文件时发生错误: {e}")
    except Exception as e:
        print(f"处理过程中发生未知错误: {e}")

# --- 程序主入口 ---
if __name__ == "__main__":
    # --- 配置 ---
    input_file = "C:\\Computer\\Code666\\python\\Scriptor-Binarius-Auditivus\\1.txt"   # 输入文件名
    output_file = "output.txt" # 输出文件名
    file_encoding = "utf-8"    # 文件编码，utf-8 支持绝大多数语言

    # --- 执行处理 ---
    process_file(input_file, output_file, file_encoding)