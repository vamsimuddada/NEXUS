import json
import codecs

with codecs.open(r"C:\Users\VAMSI\.gemini\antigravity\brain\d469ce46-7d98-4589-b233-80ecdcf9fc8e\.system_generated\logs\transcript_full.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("type") == "PLANNER_RESPONSE" and "tool_calls" in data:
                for tc in data["tool_calls"]:
                    if tc["name"] == "view_file" and "dashboard.py" in tc["args"].get("AbsolutePath", ""):
                        args = tc["args"]
                        print(f"Step {data.get('step_index')}: view_file dashboard.py, Start: {args.get('StartLine')}, End: {args.get('EndLine')}")
        except: pass
