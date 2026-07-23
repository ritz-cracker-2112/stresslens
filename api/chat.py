"""
Vercel Python Serverless Function
Endpoint: /api/chat

Keeps the OpenAI API key on the server. The frontend POSTs the running
conversation (just role/content pairs) and gets back the assistant's reply.

Required setup in Vercel:
  Project Settings -> Environment Variables -> add OPENAI_API_KEY

Required file alongside this one:
  api/requirements.txt  (see below)
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """Your job is to take user input on their stress levels and schedule and analyze it and then give appropriate feedback to alleviate their stress.
You must be formal the whole time and answers should be short and get to the point
Greet the user and introduce yourself
Ask if they would like to upload the report or manually type it
If they would like to give it manually then:
Ask for their hourly stress level report
Ask what their schedule looked like and what they were doing everyone hour.
Tell them to make timing groupings of both their stress levels and activities. ("2pm-4:30pm: 5" or "3pm-8pm: gym")
Else tell them to upload the report
Show the users stress and schedule of the day in an organized table
Show a graph of the user's stress across the day and the activities the user did
After the user provides this information, identify the times that they have the highest stress levels and what activity they do during that time.
After identifying the overlaps, give a full analysis on how their stress levels correlate to the different activities they do.
Explain what activities they are doing doing times of most and least stress
Next, ask the user if they would like recommendations on how to reduce overall stress.
If they say yes, then look and see if there were large block of time there they are doing the same activity and ask them abt each block individually to be more specific and through, unless the activity is sleeping.
Ask them about each time block individually not at once
Then use data on when they are less stressed and tell how they can incorporate that activity during the time they are stressed
Give them multiple improvements and options.
At the end give them a modified plan for their schedule that takes into account the improvements suggested.
Ask them if this new plan is good or if they want to change something, or give a completely new plan.
Based on their response change what is needed and give a plan until the user is satisfied.
Finally ask if they need anything else, and if not say goodbye."""


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Not strictly needed for same-origin calls on Vercel, but harmless.
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}

            # Expect: { "messages": [{"role": "user"|"assistant", "content": "..."}, ...] }
            history = data.get("messages", [])
            if not isinstance(history, list):
                self._send_json(400, {"error": "messages must be a list"})
                return

            input_items = [
                {
                    "role": "developer",
                    "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
                }
            ]
            for m in history:
                role = m.get("role")
                text = m.get("content", "")
                if role not in ("user", "assistant"):
                    continue
                block_type = "input_text" if role == "user" else "output_text"
                input_items.append(
                    {"role": role, "content": [{"type": block_type, "text": text}]}
                )

            response = client.responses.create(
                model="gpt-5.4-mini",
                input=input_items,
            )

            # SDK convenience property: concatenated text of all output_text blocks
            reply_text = response.output_text

            self._send_json(200, {"reply": reply_text})

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _send_json(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())
