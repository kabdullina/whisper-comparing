import os
import sys
import subprocess

#pip install whisperx==3.3.2
#pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu12

audio_files_name = os.listdir('./vocal-audio-files')

params = [['large-v2', None],
          ['large-v2', 15],
          ['large-v3-turbo', None],
          ['large-v3-turbo', 15],
          ]

directory = 'whisperx_result'
os.makedirs(directory, exist_ok=True)

for file_name in audio_files_name:
    for param_set in params:
        print(f'Started WhisperX: {file_name}, {str(param_set[0])}, {str(param_set[1])}')
        if param_set[1]:
            cmd = [
                "whisperx",
                f"./vocal-audio-files/{file_name}",
                "--output_dir", f"./{directory}/{file_name.replace('.wav', '')}_{str(param_set[0])}_{str(param_set[1])}",
                "--compute_type", "float32",
                "--model", f"{param_set[0]}",
                "--batch_size", "4",
                "--chunk_size", f"{param_set[1]}",
                "--vad_onset", "0.4",
                "--vad_offset", "0.3",
                "--output_format", "json",
                "--task", "transcribe"
            ]
        else:
            cmd = [
                "whisperx",
                f"./vocal-audio-files/{file_name}",
                "--output_dir", f"./{directory}/{file_name.replace('.wav', '')}_{str(param_set[0])}_{str(param_set[1])}",
                "--compute_type", "float32",
                "--model", f"{param_set[0]}",
                "--batch_size", "4",
                "--vad_onset", "0.4",
                "--vad_offset", "0.3",
                "--output_format", "json",
                "--task", "transcribe"
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        print("Вывод скрипта:\n", result.stdout)
        print("Ошибки:\n", result.stderr)
        print(f'Finished WhisperX: {file_name}, {str(param_set[0])}, {str(param_set[1])}')
