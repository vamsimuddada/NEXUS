import json
import codecs
import re

found = False
with open('C:/Users/VAMSI/.gemini/antigravity/brain/d469ce46-7d98-4589-b233-80ecdcf9fc8e/.system_generated/logs/transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        content = data.get('content', '')
        if "Here is the complete file content to write" in content:
            # Extract the code block
            match = re.search(r"```python\n(.*?)```", content, re.DOTALL)
            if match:
                original_code = match.group(1)
                with codecs.open('C:/Users/VAMSI/OneDrive/Desktop/NEXUS/scratch/perfect_backup.py', 'w', 'utf-8') as out:
                    out.write(original_code)
                print("Extracted perfect backup!")
                found = True
                break

if not found:
    print("Could not find the prompt!")
