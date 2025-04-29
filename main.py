# main_controller.py
# -*- coding: utf-8 -*-

import os
import sys
from scriptor import text_to_binary_string  # Import from Scriptor.py
from audio import binary_string_to_audio   # Import from audio.py

# --- Master Configuration ---
# Use raw strings (r"...") or double backslashes ("\\") for Windows paths
SOURCE_TEXT_FILE = r"C:\Computer\Code666\python\Scriptor-Binarius-Auditivus\input.txt" # Input High Gothic text file
FINAL_AUDIO_FILE = r"C:\Computer\Code666\python\Scriptor-Binarius-Auditivus\Omnissiah_Vox_Output.wav" # Final audio output file
TEXT_ENCODING = "utf-8" # Encoding for reading the source text file

# --- NEW: Binary Output Configuration ---
SAVE_BINARY_FILE = True # Set to True to save the binary string, False to skip
# Define the output path for the binary file (optional)
# If None, it will be saved next to the audio file with a .bin.txt extension
BINARY_OUTPUT_FILE_PATH = None # Example: r"C:\path\to\binary_output.txt" or None

# --- Main Workflow ---
def run_conversion_pipeline(text_filepath, audio_filepath, encoding, save_binary_flag, binary_output_path_override=None):
    """
    Orchestrates the text -> binary -> (optional binary file) -> audio conversion process.

    Args:
        text_filepath (str): Path to the source text file.
        audio_filepath (str): Path to the target audio file.
        encoding (str): Text encoding to use.
        save_binary_flag (bool): Whether to save the intermediate binary string to a file.
        binary_output_path_override (str | None): Specific path to save the binary file,
                                                 or None to derive it automatically.
    """
    print("-" * 50)
    print(" Initiating Scriptor-Binarius-Auditivus Protocol")
    print("-" * 50)
    print(f"输入文本文件: {text_filepath}")
    print(f"目标音频文件: {audio_filepath}")
    print(f"文本编码: {encoding}")
    print(f"是否保存二进制文本文件: {'是' if save_binary_flag else '否'}") # Indicate if binary file will be saved
    print("-" * 50)

    # 1. Read Source Text File
    print("[Phase 1: Reading Source Text]")
    if not os.path.exists(text_filepath):
        print(f"错误: 输入文本文件未找到: {text_filepath}")
        return False

    original_text = ""
    try:
        with open(text_filepath, 'r', encoding=encoding) as infile:
            original_text = infile.read()
        print(f"成功读取文件。文本长度: {len(original_text)} 字符。")
        if not original_text.strip():
             print(f"警告: 输入文件 '{text_filepath}' 为空或只包含空白字符。")
             # Decide if processing should continue for empty input
             # return False # Or proceed to generate empty audio if desired

    except IOError as e:
        print(f"错误: 读取文件时发生 IO 错误: {e}")
        return False
    except UnicodeDecodeError:
        print(f"错误: 无法使用 '{encoding}' 编码解码文件。请检查文件编码。")
        return False
    except Exception as e:
        print(f"错误: 读取文件时发生未知错误: {e}")
        return False

    print("-" * 50)

    # 2. Convert Text to Binary String (using Scriptor module)
    print("[Phase 2: Text to Binary Conversion (Scriptor Module)]")
    binary_string_data = text_to_binary_string(original_text, encoding)

    if binary_string_data is None:
        print("错误: 文本到二进制转换失败。请检查 Scriptor 模块的错误输出。")
        return False
    elif not binary_string_data:
         print("信息: 源文本为空或无法编码，生成空的二进制数据。")
         # Handle empty binary data - maybe stop or generate silent audio?
         # For now, we'll proceed, audio module should handle empty binary string.

    print("文本到二进制转换完成。")
    # print(f"  Binary Sample (first 100 chars): {binary_string_data[:100]}{'...' if len(binary_string_data)>100 else ''}") # Optional
    print("-" * 50)


    # --- NEW: Phase 2.5: Optionally Save Binary String to File ---
    if save_binary_flag:
        print("[Phase 2.5: Saving Binary Data to Text File]")
        if binary_string_data is not None: # Only save if conversion was successful
            # Determine the output path for the binary file
            if binary_output_path_override:
                binary_file_save_path = binary_output_path_override
            else:
                # Derive path from audio file path: replace extension with .bin.txt
                base_path, _ = os.path.splitext(audio_filepath)
                binary_file_save_path = base_path + ".bin.txt"

            print(f"尝试将二进制字符串保存到: {binary_file_save_path}")
            try:
                # Ensure the directory exists (might be redundant if already created for audio, but safe)
                binary_output_dir = os.path.dirname(binary_file_save_path)
                if binary_output_dir and not os.path.exists(binary_output_dir):
                     os.makedirs(binary_output_dir, exist_ok=True)
                     print(f"已创建二进制文件输出目录: {binary_output_dir}")

                # Write the binary string to the file (using ascii is fine)
                with open(binary_file_save_path, 'w', encoding='ascii') as bin_outfile:
                    bin_outfile.write(binary_string_data)
                print(f"二进制字符串已成功保存到: {binary_file_save_path}")

            except IOError as e:
                print(f"警告: 无法将二进制字符串写入文件 '{binary_file_save_path}': {e}")
                # Continue processing even if saving fails? Or return False? Decide based on requirements.
                # For now, we just print a warning and continue.
            except Exception as e:
                print(f"警告: 保存二进制文件时发生未知错误: {e}")
                # Continue processing
        else:
            print("警告: 二进制数据为空或转换失败，跳过保存二进制文件。")
        print("-" * 50)
    # --- End Phase 2.5 ---


    # 3. Convert Binary String to Audio (using audio module)
    print("[Phase 3: Binary to Audio Conversion (Audio Module)]")
    audio_success = binary_string_to_audio(binary_string_data if binary_string_data is not None else "", audio_filepath) # Pass empty string if None

    if not audio_success:
        print("错误: 二进制到音频转换失败。请检查 Audio 模块的错误输出。")
        return False

    print("-" * 50)
    print("转换流程成功完成!")
    print(f"最终音频文件已生成: {audio_filepath}")
    if save_binary_flag and binary_string_data is not None:
         # Re-calculate path in case it was generated automatically, to show the user
         binary_file_path_final = binary_output_path_override or (os.path.splitext(audio_filepath)[0] + ".bin.txt")
         if os.path.exists(binary_file_path_final): # Check if it was actually saved successfully before printing
              print(f"二进制文本文件已生成: {binary_file_path_final}")
    print("+" * 50)
    return True

# --- Execute the Main Workflow ---
if __name__ == "__main__":
    # Ensure the output directory for the *audio* file exists
    # The binary saving logic will handle its own directory if needed
    output_dir = os.path.dirname(FINAL_AUDIO_FILE)
    if output_dir and not os.path.exists(output_dir):
        print(f"创建输出目录: {output_dir}")
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            print(f"错误: 无法创建输出目录 '{output_dir}': {e}")
            sys.exit(1) # Exit if cannot create output directory

    # Run the main process, passing the configuration flags
    run_conversion_pipeline(
        text_filepath=SOURCE_TEXT_FILE,
        audio_filepath=FINAL_AUDIO_FILE,
        encoding=TEXT_ENCODING,
        save_binary_flag=SAVE_BINARY_FILE, # Pass the flag
        binary_output_path_override=BINARY_OUTPUT_FILE_PATH # Pass the specific path or None
    )