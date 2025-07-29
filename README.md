# TaskLens MVP

TaskLens is a lightweight AI assistant that transcribes Zoom meeting recordings (local or cloud), extracts tasks using GPT, and sends them directly to Trello for streamlined task management.

---

Video Demo: https://drive.google.com/file/d/10DnkgR0nSVfvLLCNsNCA9JpjH7mYhIrH/view?usp=sharing

---

## Setup Instructions

### 1. Clone and Enter Project
```bash
git clone https://github.com/yourusername/TaskLens_App.git
cd TaskLens_App
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- Flask
- flask-cors
- python-dotenv
- requests
- openai
- google-cloud-speech
- pydub

### 4. Configure `.env` File
Create a `.env` file in the root with:

```
OPENAI_API_KEY=your_openai_key
TRELLO_KEY=your_trello_key
TRELLO_TOKEN=your_trello_token
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
ZOOM_ACCOUNT_ID=your_zoom_account_id
```

*** Also make sure you added your `google_speech_key.json` into `/utils/` for Google Speech-to-Text.

### 5. Run the app

```bash
cd TaskLens_App
python server.py
```

Visit in your browser at:  
http://127.0.0.1:5000

---

## Features

- Select Zoom **Local** or **Cloud** recordings
- Extract tasks and task status (To-Do, Doing, Done) using GPT
- Edit tasks manually before sending to Trello
- Automatically uploads to the correct Trello list

---

## Sample Meeting Transcript Input (m4p Audio)


> Alright guys quick stand-up today, nothing too crazy.

> Some users are still getting error codes at the login screen on certain servers. Zane, can you take a look at the login flow on those please?

> And Dave, can you take a look at the bug in the task sync logic and patch it up if you can?

> I just wrapped up the UI cleanup work I was doing for the dashboard so that’s all set and that's done.

> I just started the backend endpoint for the export function now, hoping to get a draft done today.

> And reminder for everyone: it looks like the team testing merge request in GitLab is ready to move into quality, so please review and list any findings.

> And that’s all I got everyone, have a nice rest of your day.


---

## Sample Extracted Meeting Transcript Output

all right guys quick stand up today um nothing too crazy some users are still getting error codes at the login screen on certain servers
Zane can you take a look at the login flow on those please
and Dave
can you take a look at the bug and the task sync logic and Patch it up if you can
I just wrapped up the UI cleanup work I was doing for the dashboard so that's all set and that's done
I just started the back end endpoint for the export function now I'm hoping to get a draft done today
and final reminder for everyone it looks like the team testing merge requests and gitlab is ready to move in the quality so please review you and list any findings
and that's all I've got
everyone have a nice rest of your day


---

## Sample Extracted Task Output

Once the transcript is processed, the extracted tasks returned in this structured JSON format, to then be displayed in the UI:

```json
[
  {
    "description": "Check the login flow",
    "assignee": "Zane",
    "status": "To-Do"
  },
  {
    "description": "Fix the bug and patch the task sync logic",
    "assignee": "Dave",
    "status": "To-Do"
  },
  {
    "description": "UI cleanup work for the dashboard",
    "assignee": null,
    "status": "Done"
  },
  {
    "description": "Start backend endpoint for export function",
    "assignee": null,
    "status": "Doing"
  },
  {
    "description": "Review team testing merge requests in GitLab",
    "assignee": null,
    "status": "To-Do"
  }
]
```

---

## Web UI Preview (Mockup)

Below is a visual representation of how tasks appear on the TaskLens interface after processing a meeting transcript:


| Description                                             | Assignee | Status |
|---------------------------------------------------------|----------|--------|
| Check the login flow                                    | Zane     | To-Do  |
| Fix the bug and patch the task sync logic               | Dave     | To-Do  |
| UI cleanup work for the dashboard                       | –        | Done   |
| Start backend endpoint for export function              | –        | Doing  |
| Review team testing merge requests in GitLab            | –        | To-Do  |

#### Each task is editable via a card-style input form in the web app, with:
	•	a text input for description
	•	a text input for assignee
	•	a dropdown menu for status (To-Do, Doing, Done)
	•	a delete button in the top-right corner of each card
	•	an add button for additional tasks
	
---

## Sending to Trello

Once tasks are finalized in the UI, clicking **"Send to Trello"** sends each task to the appropriate Trello list based on its `Status`:

- **To-Do** → Sent to "To-Do" list on Trello
- **Doing** → Sent to "Doing" list
- **Done** → Sent to "Done" list

Tasks are then displayed in Trello like this:

### **To-Do**
──────────────

• Check the login flow

• Fix the bug and patch the task sync logic

• Review team testing merge requests in GitLab

### **Doing**
──────────────

• Start backend endpoint for export function

### **Done**
──────────────

• UI cleanup work for the dashboard 

---

## Submission Info
- Sean Terando  
- terando.2@wright.edu
- CEG 7370 – Distributed Computing   
- 07/29/2025 
