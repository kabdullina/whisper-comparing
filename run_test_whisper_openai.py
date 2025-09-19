import whisper
import torch
import json
import os
import subprocess
import sys

#pip install openai-whisper


device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

audio_files_name = os.listdir('./vocal-audio-files')
params = [['large-v2'],
          ['large-v3']
          ]

directory = 'whisper_openai_result'
os.makedirs(directory, exist_ok=True)

for file_name in audio_files_name:
    for param_set in params:
        print(f'Started: {file_name}')
        model = whisper.load_model(param_set[0]).to(device)

        result = model.transcribe(f"./vocal-audio-files/{file_name}", verbose=True)

        with open(f"./{directory}/{file_name.replace('.wav', '')}_{param_set[0]}.json", "w") as f:
            json.dump(result, f)

        print(f'Finished: {file_name}')

