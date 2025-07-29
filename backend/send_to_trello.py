import os
import json
import requests
from dotenv import load_dotenv
from flask import request

load_dotenv()

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")

LIST_ID_TODO = "688842e0503100e09231b489"
LIST_ID_DOING = "688842e0503100e09231b48a"
LIST_ID_DONE = "688842e0503100e09231b48b"

def send_tasks_to_trello():
    data = request.get_json()
    tasks = data.get("tasks", [])
    results = []

    for task in tasks:
        desc = task.get("description", "No description").strip()
        assignee = task.get("assignee", "Unassigned").strip()
        status = task.get("status", "To-Do").strip()

        list_id = {
            "To-Do": LIST_ID_TODO,
            "Doing": LIST_ID_DOING,
            "Done": LIST_ID_DONE
        }.get(status, LIST_ID_TODO)

        params = {
            "key": TRELLO_KEY,
            "token": TRELLO_TOKEN,
            "idList": list_id,
            "name": desc,
            "desc": f"Assigned to: {assignee}"
        }

        res = requests.post("https://api.trello.com/1/cards", params=params)

        if res.ok:
            results.append({
                "status": "success",
                "description": desc,
                "assignee": assignee,
                "trello_id": res.json().get("id", "N/A")
            })
            print(f"[SUCCESS]\t{desc} --> {status} (Assignee: {assignee})")
        else:
            results.append({
                "status": "fail",
                "description": desc,
                "assignee": assignee,
                "error": f"{res.status_code}: {res.text}"
            })
            print(f"[FAIL]\t\t{desc} --> {status} — {res.status_code}: {res.text}")

    return {"results": results}