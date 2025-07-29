import os
import glob
import json
import subprocess
from backend.transcribe import transcribe_audio
from backend.extract_tasks import extract_tasks_from_text

RECORDINGS_DIR = "recordings"
OUTPUT_AUDIO = "outputs/latest_audio.wav"
OUTPUT_TRANSCRIPT = "outputs/transcript.txt"
OUTPUT_TASKS = "outputs/extracted_tasks.json"

#   Grab latest m4a recording
def get_latest_m4a():
    folders = [os.path.join(RECORDINGS_DIR, f) for f in os.listdir(RECORDINGS_DIR)]
    folders = [f for f in folders if os.path.isdir(f)]
    folders.sort(key=os.path.getmtime, reverse=True)
    latest_folder = folders[0]

    m4a_files = glob.glob(os.path.join(latest_folder, "*.m4a"))
    if not m4a_files:
        raise FileNotFoundError("No .m4a files found in latest folder.")
    return m4a_files[0]

#   Convert .m4a --> .wav
def convert_to_wav(m4a_path, wav_path):
    subprocess.run(
        ["ffmpeg", "-y", "-i", m4a_path, "-ac", "1", "-ar", "16000", wav_path],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

#   Run pipeline to transcribe audio and extract tasks
def run_pipeline(audio_path="outputs/latest_audio.wav"):
    transcript = transcribe_audio(OUTPUT_AUDIO)
    tasks = extract_tasks_from_text(transcript)

    with open(OUTPUT_TASKS, "w") as f:
        json.dump(tasks, f, indent=2)

    print(f"[SUCCESS]\tExtracted tasks saved to {OUTPUT_TASKS}")
    return transcript, tasks

#   Transcribe logic
def transcribe_audio(audio_path):
    from backend.transcribe import transcribe_audio as transcribe_fn
    return transcribe_fn(audio_path)

#   Extract tasks logic
def extract_tasks(audio_path):
    from backend.extract_tasks import extract_tasks_from_text
    transcript = transcribe_audio(audio_path)[0]
    return transcript, extract_tasks_from_text(transcript)

if __name__ == "__main__":
    run_pipeline()