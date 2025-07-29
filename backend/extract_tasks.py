import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_tasks_from_text(transcript):
    
    #   Prompt to feed OpenAI to extract usefull tasks
    prompt = f"""
    You're an intelligent task extractor for a meeting assistant app.

    From the transcript below, extract a structured list of action items. For each task, return the following fields:
    - "description": a short sentence summarizing the task
    - "assignee": the person responsible, if mentioned (else null)
    - "status": one of ["To-Do", "Doing", "Done"]

    Guidelines for assigning status:
    - "To-Do": for brand new or upcoming tasks that are being mentioned for the first time. These are things we should start working on.
    - "Doing": if someone mentions they're starting or currently working on a task, or if the task is already in progress from a previous meeting.
    - "Done": if someone says the task is finished, completed, or already taken care of.

    When parsing action items:
    - If you extract a person's name (e.g., 'Dave, can you...'), assign it to the `assignee` field and DO NOT include the name in the `description`.
    - The `description` should describe the action only.
    - Detect task completions using phrases like 'just finished', 'wrapped up', 'that’s done', 'completed', 'shipped', 'all set', etc. Set `status` to 'Done' in these cases.
    - If someone says they’re about to begin a task like 'I'm starting...', 'I'll begin...', etc. use `status: Doing`.
    - Otherwise, default to `status: To-Do`.

    Important:
    - Output must be a valid JSON array (not markdown), like:
    [
    {{
        "description": "...",
        "assignee": "...",
        "status": "To-Do"
    }},
    ...
    ]

    Here’s the transcript:
    \"\"\"
    {transcript}
    \"\"\"
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("[WARNING]\tFailed to parse OpenAI response as JSON. Saving raw content.")
        return [{"raw_output": content}]