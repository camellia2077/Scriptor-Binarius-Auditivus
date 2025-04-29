import numpy as np
import scipy.io.wavfile as wavfile
import re # 用于清理输入字符串
import os # 用于检查文件是否存在
import sys # 保留 sys 以便未来可能使用 sys.exit() 等

# --- 文件与音频配置 ---
INPUT_FILENAME = "C:\Computer\Code666\python\Scriptor-Binarius-Auditivus\output.txt" # <<< 指定包含二进制字符串的输入文件名
OUTPUT_FILENAME = "binary_output_audio.wav" # 输出音频文件名

SAMPLE_RATE = 44100      # 采样率 (Hz) - CD 音质常用值
FREQ_0 = 440             # '0' 的频率 (Hz) - 例如 A4 (钢琴中央A)
FREQ_1 = 880             # '1' 的频率 (Hz) - 例如 A5 (高一个八度的A)
DURATION = 0.1           # 每个 Beep/Boop 的持续时间 (秒)
SILENCE_DURATION = 0.05  # 每个 Beep/Boop 之间的静音持续时间 (秒)
AMPLITUDE = 0.6          # 音量大小 (0.0 到 1.0 之间)


def generate_sine_wave(frequency, duration, sample_rate, amplitude):
    """
    生成指定频率、持续时间、采样率和振幅的正弦波 NumPy 数组。
    """
    # 计算需要生成的样本数量
    num_samples = int(sample_rate * duration)
    # 创建时间轴 (从 0 到 duration)
    t = np.linspace(0., duration, num_samples, endpoint=False)
    # 计算正弦波: A * sin(2 * pi * f * t)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave

def generate_silence(duration, sample_rate):
    """
    生成指定持续时间的静音 NumPy 数组 (全零)。
    """
    return np.zeros(int(sample_rate * duration))

def binary_string_to_audio(binary_string, output_filename):
    """
    将二进制字符串转换为 Beep/Boop 音频并保存为 WAV 文件。
    """
    print(f"接收到的原始输入 (前100字符): '{binary_string[:100]}{'...' if len(binary_string) > 100 else ''}'")

    # 1. 清理输入：移除空格和任何非 '0' 或 '1' 的字符
    cleaned_binary = re.sub(r'[^01]', '', binary_string)

    if not cleaned_binary:
        print("\n错误：输入数据清理后未找到有效的二进制数字 ('0' 或 '1')。无法生成音频。")
        return False

    print(f"清理后的二进制序列 ({len(cleaned_binary)} 位): '{cleaned_binary[:100]}{'...' if len(cleaned_binary) > 100 else ''}'")
    print(f"将根据以下参数生成音频:")
    print(f"  - '0' 频率 (低音): {FREQ_0} Hz")
    print(f"  - '1' 频率 (高音): {FREQ_1} Hz")
    print(f"  - 每个音持续时间: {DURATION} 秒")
    print(f"  - 音之间静音: {SILENCE_DURATION} 秒")
    print(f"  - 输出文件: {output_filename}")

    audio_segments = []
    # 预先生成静音段以提高效率
    silence_segment = generate_silence(SILENCE_DURATION, SAMPLE_RATE)

    # 2. 遍历清理后的二进制字符串中的每一位
    print("\n正在生成音频波形...")
    total_bits = len(cleaned_binary)
    for i, bit in enumerate(cleaned_binary):
        if bit == '0':
            frequency = FREQ_0
            tone_type = "Boop (低)"
        else: # bit == '1'
            frequency = FREQ_1
            tone_type = "Beep (高)"

        # 打印进度 (可选, 对于长字符串有用)
        # 每处理 50 位或最后一位时打印一次状态
        if (i + 1) % 50 == 0 or i == total_bits - 1:
             print(f"  处理中: {i + 1}/{total_bits} 位 ({tone_type})...", end='\r') # 使用 \r 回车符实现原地更新

        # 生成当前位的音调
        tone_segment = generate_sine_wave(frequency, DURATION, SAMPLE_RATE, AMPLITUDE)
        audio_segments.append(tone_segment)

        # 在每个音调后添加静音段 (除了最后一个)
        if SILENCE_DURATION > 0 and i < total_bits - 1:
            audio_segments.append(silence_segment)

    print("\n" + " " * 50 + "\r音频波形生成完毕。") # 清除进度行并打印完成信息

    if not audio_segments:
        print("\n错误：未能生成任何音频片段。")
        return False

    # 3. 将所有音频片段连接成一个完整的波形
    print("正在连接所有音频片段...")
    final_wave = np.concatenate(audio_segments)

    # 4. 将波形数据转换为 WAV 文件所需的格式 (16位整数)
    print("正在将波形数据转换为 16 位整数格式...")
    scaled_wave = np.int16(final_wave * 32767) # 简化缩放，假设 AMPLITUDE <= 1.0

    # 5. 写入 WAV 文件
    try:
        print(f"正在写入 WAV 文件: {output_filename}...")
        wavfile.write(output_filename, SAMPLE_RATE, scaled_wave)
        print("\n成功！音频文件已保存为 '{}'".format(output_filename))
        return True
    except Exception as e:
        print(f"\n错误：无法写入 WAV 文件 '{output_filename}': {e}")
        return False

# --- 程序主入口 ---
if __name__ == "__main__":
    print("=" * 40)
    print("  二进制文件转音频 (Beep/Boop)")
    print("=" * 40)

    input_file_path = INPUT_FILENAME
    print(f"准备从文件 '{input_file_path}' 读取二进制字符串...")

    # 检查输入文件是否存在
    if not os.path.exists(input_file_path):
        print(f"\n错误：输入文件 '{input_file_path}' 未找到。")
        print("请在脚本同目录下创建该文件，并填入二进制字符串 (例如: 01101... )。")
        # 可以在这里选择创建一个空的示例文件
        # try:
        #     with open(input_file_path, 'w') as f:
        #         f.write("01101000 01100101 01101100 01101100 01101111 # 示例: hello")
        #     print(f"已创建示例输入文件 '{input_file_path}'。请填充内容后重新运行。")
        # except IOError as e:
        #     print(f"尝试创建示例文件时出错: {e}")
    else:
        # 文件存在，尝试读取
        try:
            print(f"正在读取文件 '{input_file_path}'...")
            with open(input_file_path, 'r', encoding='utf-8') as infile: # 指定 utf-8 编码以防万一
                binary_input_from_file = infile.read()

            if binary_input_from_file.strip():
                 # 调用核心函数处理读取到的内容
                 binary_string_to_audio(binary_input_from_file, OUTPUT_FILENAME)
            else:
                print(f"\n警告：输入文件 '{input_file_path}' 为空或只包含空格。")

        except IOError as e:
            print(f"\n错误：读取文件 '{input_file_path}' 时发生 IO 错误: {e}")
        except Exception as e:
            print(f"\n处理文件 '{input_file_path}' 时发生未知错误: {e}")

    print("\n程序结束。")