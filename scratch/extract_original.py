import json
import codecs

with codecs.open(r"C:\Users\VAMSI\.gemini\antigravity\brain\d469ce46-7d98-4589-b233-80ecdcf9fc8e\.system_generated\logs\transcript_full.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if '"name":"view_file"' in line and 'scripts/dashboard.py' in line:
            # Maybe the response is in a later line
            pass
