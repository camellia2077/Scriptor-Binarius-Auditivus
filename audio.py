# 用于把二进制字符生成音频
import numpy as np
import scipy.io.wavfile as wavfile
import re 

SAMPLE_RATE = 44100      # 采样率 (Hz)
FREQ_0 = 440             # '0' 的频率 (Hz)
FREQ_1 = 880             # '1' 的频率 (Hz)
DURATION = 0.1           # 每个音的持续时间 (秒)
SILENCE_DURATION = 0.05  # 音之间的静音持续时间 (秒)
AMPLITUDE = 0.6          # 音量 (0.0 to 1.0)

def generate_sine_wave(frequency, duration, sample_rate, amplitude):
    """生成正弦波 NumPy 数组。"""
    num_samples = int(sample_rate * duration)
    t = np.linspace(0., duration, num_samples, endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave

def generate_silence(duration, sample_rate):
    """生成静音 NumPy 数组。"""
    return np.zeros(int(sample_rate * duration))

# --- Core Function ---
def binary_string_to_audio(binary_string, output_filename):
    """将二进制字符串转换为 Beep/Boop音频并保存为 WAV 文件。"""
    
    print(f"音频模块收到二进制输入 (前100字符): '{binary_string[:100]}{'...' if len(binary_string) > 100 else ''}'")

    # 1. 清理输入：移除所有非 '0' 或 '1' 的字符
    cleaned_binary = re.sub(r'[^01]', '', binary_string)

    if not cleaned_binary:
        print("\n错误 (Audio): 输入数据清理后未找到有效的二进制数字 ('0' 或 '1')。")
        return False

    print(f"清理后的二进制序列 ({len(cleaned_binary)} 位) 将用于生成音频。")
    # print(f"音频参数: FREQ_0={FREQ_0}, FREQ_1={FREQ_1}, DUR={DURATION}, SILENCE={SILENCE_DURATION}") # Optional detail

    audio_segments = []
    silence_segment = generate_silence(SILENCE_DURATION, SAMPLE_RATE)

    # 2. 生成音频波形
    print("开始生成音频波形...")
    total_bits = len(cleaned_binary)
    for i, bit in enumerate(cleaned_binary):
        frequency = FREQ_0 if bit == '0' else FREQ_1
        # tone_type = "Boop (低)" if bit == '0' else "Beep (高)" # For verbose logging

        # 打印进度
        if (i + 1) % 100 == 0 or i == total_bits - 1:
             print(f"  生成中: {i + 1}/{total_bits} 位...", end='\r')

        tone_segment = generate_sine_wave(frequency, DURATION, SAMPLE_RATE, AMPLITUDE)
        audio_segments.append(tone_segment)

        if SILENCE_DURATION > 0 and i < total_bits - 1:
            audio_segments.append(silence_segment)

    print("\n" + "-" * 50 + "\r音频波形生成完成。")

    if not audio_segments:
        print("错误 (Audio): 未能生成任何音频片段。")
        return False

    # 3. 连接片段
    print("连接音频片段...")
    final_wave = np.concatenate(audio_segments)

    # 4. 格式转换 (16-bit integer)
    print("转换为 16 位整数格式...")
    scaled_wave = np.int16(final_wave * 32767)

    # 5. 写入 WAV 文件
    try:
        print(f"写入 WAV 文件: {output_filename}...")
        wavfile.write(output_filename, SAMPLE_RATE, scaled_wave)
        print(f"成功！音频文件已保存到 '{output_filename}'")
        return True
    except Exception as e:
        print(f"错误 (Audio): 无法写入 WAV 文件 '{output_filename}': {e}")
        return False
if __name__ == "__main__":
    print("--- Running audio.py Standalone for Testing ---")

    # Example binary string for testing
    test_binary = "01101000 01100101 01101100 01101100 01101111" # "hello"
    test_output_wav = "output_audio_standalone_test.wav"

    print(f"使用测试二进制串: '{test_binary}'")
    success = binary_string_to_audio(test_binary, test_output_wav)

    if success:
        print("独立音频生成测试成功。")
    else:
        print("独立音频生成测试失败。")
    print("---程序结束--")
