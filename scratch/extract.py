import json

with open('C:/Users/VAMSI/.gemini/antigravity/brain/d469ce46-7d98-4589-b233-80ecdcf9fc8e/.system_generated/logs/transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        content = data.get('content', '')
        if 'NEXUS War Room Dashboard — Professional Edition' in content:
            with open('C:/Users/VAMSI/OneDrive/Desktop/NEXUS/scratch/original.txt', 'w', encoding='utf-8') as out:
                out.write(content)
            print("Extracted!")
            break
