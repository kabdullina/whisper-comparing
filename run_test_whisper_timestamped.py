import os
import sys
import subprocess

#pip install whisper-timestamped

audio_files_name = os.listdir('./vocal-audio-files')

params = [['large-v2'],
          ['large-v3']
          ]

directory = 'whisper_timestamped_result'
os.makedirs(directory, exist_ok=True)

for file_name in audio_files_name:
    for param_set in params:
        print(f'Started: {file_name}, {str(param_set[0])}')
        cmd = [
            "whisper_timestamped",
            f"./vocal-audio-files/{file_name}",
            "--output_dir", f"./{directory}/{file_name.replace('.wav', '')}_{str(param_set[0])}",
            "--vad", 'True'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        print("Вывод скрипта:\n", result.stdout)
        print("Ошибки:\n", result.stderr)
        print(f'Finished: {file_name}, {str(param_set[0])}')
