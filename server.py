from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from backend.process_latest_recording import run_pipeline
from backend.process_latest_recording import transcribe_audio, extract_tasks
from backend.send_to_trello import send_tasks_to_trello

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

#   Frontend
@app.route("/")
def serve_frontend():
    return app.send_static_file("index.html")

#   API: Transcribe + Extract Tasks
@app.route("/api/transcribe_extract", methods=["POST"])
def transcribe_and_extract():
    data = request.get_json()
    use_cloud = data.get("use_cloud", False)

    if use_cloud:
        from backend.zoom_api import download_latest_cloud_recording
        print("[INFO]\t\tUsing Zoom cloud recording...")
        audio_path = download_latest_cloud_recording()
    else:
        from backend.zoom_api import get_latest_local_recording_wav
        print("[INFO]\t\tUsing local recording...")
        audio_path = get_latest_local_recording_wav()

    transcript, tasks = run_pipeline(audio_path)
    return jsonify({ "transcript": transcript, "tasks": tasks })

#   API: Send Extracted Tasks to Trello
@app.route("/api/send_to_trello", methods=["POST"])
def api_send_to_trello():
    try:
        results = send_tasks_to_trello()
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)