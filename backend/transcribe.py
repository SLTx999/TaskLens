import os
import wave
import math
import contextlib
import subprocess
from google.cloud import speech_v1p1beta1 as speech

CHUNK_DURATION = 55  # seconds

def transcribe_audio(audio_path: str) -> str:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "utils/google_speech_key.json"

    client = speech.SpeechClient()
    transcript = ""

    #   Get duration
    with contextlib.closing(wave.open(audio_path, 'rb')) as wf:
        framerate = wf.getframerate()
        nframes = wf.getnframes()
        duration = nframes / float(framerate)
        num_chunks = math.ceil(duration / CHUNK_DURATION)

    print(f"[INFO]\t\tSplitting into {num_chunks} chunk(s)...")

    #   Read speech-to-text data from chunks into transcript
    for i in range(num_chunks):
        start = i * CHUNK_DURATION
        output_chunk = f"outputs/chunk_{i}.wav"

        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path, "-ss", str(start), "-t", str(CHUNK_DURATION),
            "-ac", "1", "-ar", "16000", output_chunk],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        with open(output_chunk, "rb") as f:
            content = f.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US"
        )

        response = client.recognize(config=config, audio=audio)

        for result in response.results:
            transcript += result.alternatives[0].transcript + " "

        os.remove(output_chunk)

    formatted_transcript = transcript.replace("  ", "\n")

    with open("outputs/transcript.txt", "w") as f:
        f.write(formatted_transcript.strip())

    print("[SUCCESS]\tTranscript saved to outputs/transcript.txt")
    return formatted_transcript.strip()