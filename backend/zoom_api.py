import os
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

def get_zoom_access_token():
    client_id = os.getenv("ZOOM_CLIENT_ID")
    client_secret = os.getenv("ZOOM_CLIENT_SECRET")
    account_id = os.getenv("ZOOM_ACCOUNT_ID")

    auth = (client_id, client_secret)
    res = requests.post(
        f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}",
        auth=auth,
    )
    res.raise_for_status()
    token = res.json().get("access_token")
    if not token:
        raise Exception("[FAIL]\t\tFailed to retrieve Zoom access token...")
    return token

#   Convert m4a files to wav files
def convert_m4a_to_wav(m4a_path, wav_path):
    try:
        if m4a_path == wav_path:
            temp_wav_path = wav_path + ".tmp.wav"
        else:
            temp_wav_path = wav_path

        subprocess.run(
            ["ffmpeg", "-y", "-i", m4a_path, "-ac", "1", "-ar", "16000", temp_wav_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if temp_wav_path != wav_path:
            os.replace(temp_wav_path, wav_path)

        print(f"[SUCCESS]\tConverted {m4a_path} to {wav_path}")
        return wav_path

    except subprocess.CalledProcessError as e:
        print("[FAIL]\t\tFFmpeg conversion failed:", e)
        return None

#   Download latest recording from Zoom Cloud storage
def download_latest_cloud_recording():
    access_token = get_zoom_access_token()

    #   Step 1: Get user's recordings
    res = requests.get(
        "https://api.zoom.us/v2/users/me/recordings",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    res.raise_for_status()
    meetings = res.json().get("meetings", [])
    if not meetings:
        raise Exception("[FAIL]\t\tNo recordings found in Zoom cloud.")

    #   Step 2: Find latest meeting with an audio (M4A) file
    latest = meetings[0]
    m4a_url = None
    for f in latest.get("recording_files", []):
        if f.get("file_type") == "M4A":
            m4a_url = f.get("download_url")
            break

    if not m4a_url:
        raise Exception("[FAIL]\t\tNo m4a audio file found in the latest meeting...")

    #   Step 3: Download the m4a to recordings/cloud/
    os.makedirs("recordings/cloud", exist_ok=True)
    m4a_path = "recordings/cloud/latest_cloud_audio.m4a"
    if "?" not in m4a_url:
        m4a_url += f"?access_token={access_token}"

    res = requests.get(m4a_url, headers={"Authorization": f"Bearer {access_token}"})
    res.raise_for_status()
    with open(m4a_path, "wb") as f:
        f.write(res.content)
    print(f"[SUCCESS]\tSaved cloud recording to: {m4a_path}")

    #   Step 4: Convert to outputs/latest_audio.wav
    wav_path = "outputs/latest_audio.wav"
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", m4a_path, "-ac", "1", "-ar", "16000", wav_path], 
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"[SUCCESS]\tConverted to WAV: {wav_path}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("[FAIL]\t\tffmpeg conversion failed") from e

    return wav_path

#   Download latest recording from local storage
def get_latest_local_recording_wav():
    local_dir = "recordings/local/"
    os.makedirs(local_dir, exist_ok=True)

    #   Search recursively for all .m4a files
    m4a_files = []
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            if file.lower().endswith(".m4a"):
                full_path = os.path.join(root, file)
                m4a_files.append(full_path)

    if not m4a_files:
        raise Exception("[FAIL]\t\tNo local m4a recordings found...")

    #   Find most recently modified .m4a file
    latest_file = max(m4a_files, key=os.path.getmtime)
    print(f"[SUCCESS]\tFound latest local M4A: {latest_file}")

    #   Convert to outputs/latest_audio.wav
    wav_path = "outputs/latest_audio.wav"
    convert_m4a_to_wav(latest_file, wav_path)

    return wav_path