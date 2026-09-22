import json
import codecs

with codecs.open(r"C:\Users\VAMSI\.gemini\antigravity\brain\d469ce46-7d98-4589-b233-80ecdcf9fc8e\.system_generated\logs\transcript_full.jsonl", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    try:
        data = json.loads(line)
        if data.get("step_index") == 98 and data.get("source") == "SYSTEM":
            # This is the system response for view_file
            content = data.get("content", "")
            # The content is prefixed with some metadata like "Created At: ...\nCompleted At: ...\n\n"
            # We want the actual file content.
            # Usually tool output for view_file starts directly with the lines, prefixed by line numbers.
            # Let's write the raw content to a file first so we can parse it.
            with codecs.open("scratch/raw_step98.txt", "w", encoding="utf-8") as out:
                out.write(content)
            print("Extracted Step 98 successfully.")
            break
    except: pass
