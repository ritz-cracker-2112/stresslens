from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

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
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(content_length))

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += body.get("history", [])
        messages.append({"role": "user", "content": body["message"]})

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": messages
            }).encode(),
            headers={
                "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read())
            reply_text = data["choices"][0]["message"]["content"]

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply_text}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
# no external dependencies
