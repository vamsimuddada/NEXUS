import json
import codecs
import re
import os

found = False
transcript_path = 'C:/Users/VAMSI/.gemini/antigravity/brain/d469ce46-7d98-4589-b233-80ecdcf9fc8e/.system_generated/logs/transcript_full.jsonl'

if not os.path.exists(transcript_path):
    print(f"File not found: {transcript_path}")
else:
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            for tc in data.get('tool_calls', []):
                if tc.get('function', {}).get('name') == 'default_api:invoke_subagent':
                    args = tc.get('function', {}).get('arguments', {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except:
                            continue
                    
                    subagents = args.get('Subagents', [])
                    for agent in subagents:
                        prompt = agent.get('Prompt', '')
                        if "Here is the complete file content to write" in prompt:
                            match = re.search(r"```python\n(.*?)```", prompt, re.DOTALL)
                            if match:
                                original_code = match.group(1)
                                with codecs.open('C:/Users/VAMSI/OneDrive/Desktop/NEXUS/scratch/perfect_backup.py', 'w', 'utf-8') as out:
                                    out.write(original_code)
                                print("Extracted perfect backup from transcript_full.jsonl!")
                                found = True
                                break
                if found: break
            if found: break

    if not found:
        print("Could not find the prompt in transcript_full.jsonl!")
