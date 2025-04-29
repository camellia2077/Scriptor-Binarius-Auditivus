# 把音频转化为字符
# -*- coding: utf-8 -*-

import numpy as np
import scipy.io.wavfile as wavfile
import scipy.fft
import os


# --- Configuration - MUST MATCH audio.py ---
EXPECTED_SAMPLE_RATE = 44100 # Expected sample rate
FREQ_0 = 440                 # Frequency for '0' (Hz)
FREQ_1 = 880                 # Frequency for '1' (Hz)
TONE_DURATION = 0.1          # Duration of each tone (seconds)
SILENCE_DURATION = 0.05      # Duration of silence between tones (seconds)
# --- Decoding Parameters ---
AMPLITUDE_THRESHOLD = 0.1 # Adjust based on generated amplitude and noise
FREQUENCY_THRESHOLD = (FREQ_0 + FREQ_1) / 2 # Midpoint frequency

def analyze_tone_segment(segment, sample_rate):
    """
    Analyzes an audio segment using FFT to find the dominant frequency.
    """
    if np.max(np.abs(segment)) < AMPLITUDE_THRESHOLD:
        return 0.0 # Considered silence

    n = len(segment)
    if n < 2: # Need at least 2 samples for FFT
        return -1.0

    try:
        fft_result = scipy.fft.fft(segment)
        frequencies = scipy.fft.fftfreq(n, 1.0 / sample_rate)
        magnitudes = np.abs(fft_result)
        # Find the peak frequency (ignoring DC component at index 0 and negative freqs)
        dominant_freq_index = np.argmax(magnitudes[1:n//2]) + 1
        dominant_freq = frequencies[dominant_freq_index]
        return abs(dominant_freq)
    except IndexError:
        # print("Warning: Could not find dominant frequency peak.") # Reduced verbosity
        return -1.0
    except Exception as e:
        print(f"Warning: Error during FFT analysis: {e}")
        return -1.0


# **** MODIFIED FUNCTION ****
def decode_audio_to_binary(audio_data, sample_rate):
    """
    Decodes the audio data into a binary string based on detected frequencies.
    (Revised loop logic to potentially capture the last bit)

    Args:
        audio_data (np.array): The audio waveform data (normalized float).
        sample_rate (int): The sample rate of the audio.

    Returns:
        str: The decoded binary string, or None if decoding fails.
    """
    if sample_rate != EXPECTED_SAMPLE_RATE:
        print(f"错误: 音频采样率 ({sample_rate} Hz) 与预期 ({EXPECTED_SAMPLE_RATE} Hz) 不符。")
        return None

    # Calculate expected number of samples per part
    tone_samples = int(TONE_DURATION * sample_rate)
    silence_samples = int(SILENCE_DURATION * sample_rate)
    # Samples per presumed bit cycle (tone + potential silence)
    cycle_samples = tone_samples + silence_samples

    # Basic validation
    if cycle_samples <= 0 or tone_samples <= 0:
        print("错误: 计算出的周期或音调样本数为0或负数，请检查音频参数。")
        return None

    print(f"音频总长度: {len(audio_data)/sample_rate:.2f} 秒")
    print(f"预期样本数: 音调={tone_samples}, 静音={silence_samples}, 每比特周期(估算)={cycle_samples}")

    decoded_bits = []
    uncertain_bits = 0
    current_pos = 0
    analyzed_segment_count = 0 # Keep track of processed segments

    # --- Revised Loop ---
    # Loop as long as there is enough data remaining for at least a tone segment
    while current_pos + tone_samples <= len(audio_data):
        start_index = current_pos
        end_index = start_index + tone_samples
        segment = audio_data[start_index:end_index]

        # Analyze the segment
        dominant_freq = analyze_tone_segment(segment, sample_rate)

        bit_decoded = False
        # Check if frequency is clearly identifiable and closer to one of the targets
        if dominant_freq > 0: # Check if it's not silence or FFT error (-1.0)
            dist_to_0 = abs(dominant_freq - FREQ_0)
            dist_to_1 = abs(dominant_freq - FREQ_1)
            # Simple comparison: is it closer to 0 or 1?
            if dist_to_0 < dist_to_1 and dominant_freq < FREQUENCY_THRESHOLD: # Closer to FREQ_0
                decoded_bits.append('0')
                bit_decoded = True
            elif dist_to_1 < dist_to_0 and dominant_freq > FREQUENCY_THRESHOLD: # Closer to FREQ_1
                decoded_bits.append('1')
                bit_decoded = True
            #else: # Frequency might be ambiguous, right in the middle, or far from both
                # print(f"Warning: Ambiguous frequency {dominant_freq:.1f} Hz at segment {analyzed_segment_count}")

        if not bit_decoded:
            # Could be actual silence, or an ambiguous frequency, or FFT error
            uncertain_bits += 1
            # Optional: Log details about uncertain segments if needed for debugging
            # print(f"Segment {analyzed_segment_count}: Uncertain (Freq: {dominant_freq:.1f} Hz). Skipping.")

        # Move to the start of the next potential cycle
        current_pos += cycle_samples
        analyzed_segment_count += 1

        # Optional: Add progress indicator
        if analyzed_segment_count % 50 == 0:
             print(f"  解码进度: 已分析 {analyzed_segment_count} 个潜在周期...", end='\r')
    # --- End Revised Loop ---

    print("\n" + " " * 50 + f"\r解码分析完成。共分析 {analyzed_segment_count} 个潜在周期。跳过 {uncertain_bits} 个不确定/静音周期。")

    # Check if any bits were decoded, especially if many were uncertain
    if not decoded_bits and uncertain_bits == analyzed_segment_count and analyzed_segment_count > 0:
        print("警告：分析了周期但未能解码任何确定的比特。请检查音频质量或解码参数（特别是 AMPLITUDE_THRESHOLD）。")
        # You might return None or empty string depending on desired behavior
        # return None

    return "".join(decoded_bits)
# **** END OF MODIFIED FUNCTION ****


def binary_string_to_text(binary_string, encoding='utf-8'):
    """
    Converts a string of binary digits ('0' and '1') into text.
    """
    if not binary_string:
        print("错误: 二进制字符串为空，无法转换为文本。")
        return None

    # Ensure length is a multiple of 8
    remainder = len(binary_string) % 8
    if remainder != 0:
        print(f"警告: 解码后的二进制字符串长度 ({len(binary_string)}) 不是8的倍数。")
        # Decision: Discard trailing bits or try padding? Discarding is safer.
        print(f"将丢弃末尾的 {remainder} 个比特。")
        binary_string = binary_string[:-remainder]

    if not binary_string:
        print("错误: 丢弃末尾比特后，二进制字符串为空。")
        return None

    try:
        byte_list = []
        for i in range(0, len(binary_string), 8):
            byte_chunk = binary_string[i:i+8]
            byte_value = int(byte_chunk, 2)
            byte_list.append(byte_value)

        recovered_bytes = bytes(byte_list)
        # Use 'replace' to handle potential errors if some bytes don't form valid UTF-8
        recovered_text = recovered_bytes.decode(encoding, errors='replace')
        return recovered_text
    except ValueError as e:
         print(f"错误: 将二进制块 '{byte_chunk}' 转换为整数时出错: {e}") # Added chunk info
         return None
    except UnicodeDecodeError as e:
        print(f"错误: 使用 '{encoding}' 解码字节序列时出错: {e}")
        print("可能原因：二进制数据损坏、编码不匹配或解码参数错误。")
        return None
    except Exception as e:
        print(f"错误: 二进制到文本转换过程中发生未知错误: {e}")
        return None


# --- Main Function ---
def decode_audio_file(input_wav_path, output_txt_path=None):
    """
    Reads a WAV file, decodes it to text, and prints/saves the result.
    """
    print("+"*50)
    print(" Initiating Auditivus-Binarius-Scriptor Protocol (Decoder)")
    print("+"*50)
    print(f"输入音频文件: {input_wav_path}")

    if not os.path.exists(input_wav_path):
        print(f"错误: 输入文件未找到: {input_wav_path}")
        return

    # 1. Read WAV file
    try:
        print("正在读取 WAV 文件...")
        sample_rate, audio_data = wavfile.read(input_wav_path)
        print(f"文件读取成功。采样率: {sample_rate} Hz, 数据点数: {len(audio_data)}")

        if audio_data.ndim > 1:
            print("检测到立体声，将使用第一个声道。")
            audio_data = audio_data[:, 0]

        # --- Normalization ---
        print("正在标准化音频数据...")
        dtype_info = np.iinfo(audio_data.dtype) if np.issubdtype(audio_data.dtype, np.integer) else None
        if dtype_info:
             # Integer type: scale based on max value for its type
             max_val = dtype_info.max
             min_val = dtype_info.min
             # Avoid division by zero if max_val equals min_val (e.g., constant signal)
             if max_val == min_val:
                 audio_data_float = np.zeros_like(audio_data, dtype=float)
             else:
                # Scale signed integers to [-1, 1], unsigned to [0, 1] then shift?
                # Simpler approach: just scale based on max possible deviation from zero
                scale_factor = max(abs(max_val), abs(min_val))
                audio_data_float = audio_data.astype(float) / scale_factor
        elif np.issubdtype(audio_data.dtype, np.floating):
             # Floating point type: assume it's already in [-1, 1] or similar range
             print(f"检测到浮点类型 ({audio_data.dtype})，假设已标准化。")
             audio_data_float = audio_data
             # Optional: Check range and normalize if needed
             # max_abs_val = np.max(np.abs(audio_data_float))
             # if max_abs_val > 1.0: # Or some tolerance
             #     print(f"警告: 浮点数据范围超过 [-1, 1] (最大绝对值: {max_abs_val:.2f})，将进行标准化。")
             #     audio_data_float = audio_data_float / max_abs_val
        else:
             print(f"错误: 不支持的音频数据类型 '{audio_data.dtype}' 用于标准化。")
             return
        print("音频标准化完成。")
        # --- End Normalization ---

    except FileNotFoundError: # More specific error
        print(f"错误: 输入文件未找到: {input_wav_path}")
        return
    except Exception as e:
        print(f"错误: 读取或处理 WAV 文件时出错: {e}")
        return

    # 2. Decode audio to binary string
    print("-" * 50)
    print("开始解码音频到二进制...")
    binary_result = decode_audio_to_binary(audio_data_float, sample_rate)

    if binary_result is None:
        print("解码音频到二进制失败。")
        return
    elif not binary_result:
         print("解码完成，但未检测到有效比特或所有周期都不确定。")
         # Decide how to handle this - maybe create empty text?
         recovered_text = ""
    else:
        print(f"解码得到的二进制串 (前100位): {binary_result[:100]}{'...' if len(binary_result) > 100 else ''}")
        print(f"总比特数: {len(binary_result)}")
        print("-" * 50)

        # 3. Convert binary string to text
        print("开始转换二进制到文本 (UTF-8)...")
        recovered_text = binary_string_to_text(binary_result, encoding='utf-8')

    # Check result of binary_string_to_text before proceeding
    if recovered_text is None:
        print("二进制到文本转换失败。")
    else:
        # Only print and save if text recovery was successful
        print("-" * 50)
        print("解码得到的文本:")
        print("="*20 + " START " + "="*20)
        print(recovered_text)
        print("="*21 + " END " + "="*21)

        # 4. Save to file if path provided
        if output_txt_path:
            print("-" * 50)
            print(f"正在将解码文本保存到: {output_txt_path}")
            try:
                # Ensure output directory exists
                output_dir = os.path.dirname(output_txt_path)
                if output_dir and not os.path.exists(output_dir):
                    print(f"创建输出目录: {output_dir}")
                    os.makedirs(output_dir, exist_ok=True)

                with open(output_txt_path, 'w', encoding='utf-8') as outfile:
                    outfile.write(recovered_text)
                print("文件保存成功。")
            except IOError as e:
                print(f"错误: 无法写入输出文件 '{output_txt_path}': {e}")
            except Exception as e:
                print(f"错误: 保存文件时发生未知错误: {e}")

    print("\n解码流程结束。")


# --- Main Execution ---
if __name__ == "__main__":
    # Configure input and output paths here
    # Use raw strings (r"...") or double backslashes for Windows paths
    INPUT_WAV_FILE = r"C:\Computer\Code666\python\Scriptor-Binarius-Auditivus\Omnissiah_Vox_Output.wav" # Path to the audio file generated previously
    OUTPUT_TEXT_FILE = r"C:\Computer\Code666\python\Scriptor-Binarius-Auditivus\decoded_text.txt" # Path to save the decoded text (optional)

    # Run the decoder
    decode_audio_file(INPUT_WAV_FILE, OUTPUT_TEXT_FILE)