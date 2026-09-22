import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

old_target = '"\\n" + self.results(campaign_record),'
new_target = '"\\n" + self.project_info(),\n            "\\n" + self.tactical_details(campaign_record),\n            "\\n" + self.results(campaign_record),'

text = text.replace(old_target, new_target)

# Fix numbering
text = text.replace("## 1. Executive Summary", "## Executive Summary")
text = text.replace("## 1. Project Overview & Architecture", "## 1. Project Overview & Architecture")
text = text.replace("## 2. Tactical Deployment Details", "## 2. Tactical Deployment Details")
text = text.replace("## A. RECENT AGENT PERFORMANCE", "## 3. Recent Agent Performance")
text = text.replace("## B. ELO THREAT INTELLIGENCE LEADERBOARD", "## 4. Global Threat Intelligence Leaderboard")
text = text.replace("## C. MITRE ATT&CK TACTIC EFFECTIVENESS", "## 5. MITRE ATT&CK Tactic Effectiveness")
text = text.replace("## D. THREAT EVOLUTION VISUALIZATION", "## 6. Threat Evolution Visualization")

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
