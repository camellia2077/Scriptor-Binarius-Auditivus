# 文本字符串转换为其二进制表示形式
# -*- coding: utf-8 -*-

# Note: Removed 'sys' and 'os' imports as they are not needed
# for the core function when used as a module.

def text_to_binary_string(text, encoding='utf-8'):
    """
    将文本字符串转换为其二进制表示形式（每个字节用8位二进制数表示，用空格分隔）。

    Args:
        text (str): 输入的文本字符串。
        encoding (str): 用于将文本编码为字节的编码方式，默认为 'utf-8'。

    Returns:
        str: 表示文本的二进制字符串，每个字节之间用空格分隔。
             如果输入为空或发生错误，则返回 None。
    """
    if not text:
        print("警告 (Scriptor): 输入文本为空。")
        return "" # Return empty string for empty input
    try:
        # 1. 将文本字符串根据指定编码转换为字节序列 (bytes object)
        byte_array = text.encode(encoding)

        # 2. 将每个字节转换为8位的二进制字符串
        binary_strings = [bin(byte)[2:].zfill(8) for byte in byte_array]

        # 3. 用空格连接所有字节的二进制字符串
        return ' '.join(binary_strings)
    except UnicodeEncodeError:
        print(f"错误 (Scriptor): 无法使用 '{encoding}' 对提供的文本进行编码。")
        return None
    except Exception as e:
        print(f"错误 (Scriptor): 文本到二进制转换过程中发生错误: {e}")
        return None

# --- Standalone Execution Block (Optional: for testing Scriptor.py independently) ---
# The main controller will NOT use this part.
if __name__ == "__main__":
    import os # Import os here if testing standalone file processing

    print("--- Running Scriptor.py Standalone for Testing ---")

    # Configuration for standalone test
    input_file_test = "1.txt"  # Test input file in the same directory
    output_file_test = "output_standalone_test.txt" # Test output file
    file_encoding_test = "utf-8"

    # Simplified file processing for testing
    if not os.path.exists(input_file_test):
        print(f"测试错误：找不到测试输入文件 '{input_file_test}'。")
        # Create a sample file for testing
        try:
            with open(input_file_test, 'w', encoding=file_encoding_test) as f:
                f.write("Omnissiah be praised! 01")
            print(f"已创建示例测试文件 '{input_file_test}'。")
        except IOError as e:
            print(f"创建示例测试文件时出错: {e}")
    else:
        try:
            print(f"读取测试文件: {input_file_test}")
            with open(input_file_test, 'r', encoding=file_encoding_test) as infile:
                test_text = infile.read()

            print("执行文本到二进制转换...")
            binary_result = text_to_binary_string(test_text, file_encoding_test)

            if binary_result is not None:
                print(f"写入测试二进制输出到: {output_file_test}")
                with open(output_file_test, 'w', encoding='ascii') as outfile:
                    outfile.write(binary_result)
                print("独立测试完成。")
            else:
                print("独立测试期间转换失败。")

        except Exception as e:
            print(f"独立测试期间发生错误: {e}")
    print("--- End Standalone Test ---")
