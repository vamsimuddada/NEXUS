import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix numbering
text = text.replace("## 4. Recent Agent Performance", "## 3. Recent Agent Performance")
text = text.replace("## 5. Global Threat Intelligence Leaderboard", "## 4. Global Threat Intelligence Leaderboard")
text = text.replace("## 6. MITRE ATT&CK Tactic Effectiveness", "## 5. MITRE ATT&CK Tactic Effectiveness")
text = text.replace("## D. THREAT EVOLUTION VISUALIZATION", "## 6. Threat Evolution Visualization")
text = text.replace("## 3. Threat Evolution Visualization", "## 6. Threat Evolution Visualization")

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
