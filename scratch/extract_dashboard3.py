import json
import codecs

lines_list = []
with codecs.open(r"C:\Users\VAMSI\.gemini\antigravity\brain\d469ce46-7d98-4589-b233-80ecdcf9fc8e\.system_generated\logs\transcript_full.jsonl", "r", encoding="utf-8") as f:
    lines_list = f.readlines()

for i, line in enumerate(lines_list):
    try:
        data = json.loads(line)
        if data.get("type") == "PLANNER_RESPONSE":
            for tc in data.get("tool_calls", []):
                if tc["name"] == "view_file" and "dashboard.py" in str(tc["args"]):
                    if "None" in str(tc["args"]) or ("StartLine" not in tc["args"]):
                        # The next system response should be the output
                        for j in range(i+1, min(i+5, len(lines_list))):
                            next_data = json.loads(lines_list[j])
                            if next_data.get("source") == "SYSTEM" and next_data.get("type") == "GENERIC":
                                content = next_data.get("content", "")
                                if len(content) > 1000:
                                    with codecs.open("scratch/raw_dashboard_full.txt", "w", encoding="utf-8") as out:
                                        out.write(content)
                                    print("Found and extracted!")
                                    exit(0)
    except Exception as e: pass
