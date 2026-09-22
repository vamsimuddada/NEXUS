import json
import codecs

found_tool_call = False
with codecs.open(r"C:\Users\VAMSI\.gemini\antigravity\brain\d469ce46-7d98-4589-b233-80ecdcf9fc8e\.system_generated\logs\transcript_full.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("step_index") == 97:
                found_tool_call = True
            elif found_tool_call and data.get("source") == "SYSTEM" and data.get("type") == "GENERIC":
                # This should be the tool response
                with codecs.open("scratch/raw_step98.txt", "w", encoding="utf-8") as out:
                    out.write(data.get("content", ""))
                print(f"Extracted from step {data.get('step_index')}")
                break
        except: pass
