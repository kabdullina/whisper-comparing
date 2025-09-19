import whisper
import torch
import json
import os
import sys
import subprocess



# git clone https://github.com/nyrahealth/CrisperWhisper.git
# cd CrisperWhisper
# pip install -r CrisperWhisper/requirements.txt


audio_files_name = os.listdir('./vocal-audio-files')

directory = 'whisper_crisper_result'
os.makedirs(directory, exist_ok=True)

for file_name in audio_files_name:
    print(f'Started: {file_name}')
    cmd = [
        sys.executable,
        "CrisperWhisper/transcribe.py",
        "--f", f"./vocal-audio-files/{file_name}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    print("Вывод скрипта:\n", result.stdout)
    print("Ошибки:\n", result.stderr)
    print(f'Finished: {file_name}')