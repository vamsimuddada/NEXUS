import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the heatmap status string assignment
old_status_logic = """                        status = "Compromised" if outcome == "success" else "Blocked"
                        if detected and outcome != "success": status = "Blocked"
                        elif detected and outcome == "success": status = "Attempted" # Detected but successful"""

new_status_logic = """                        status = "Blocked" if outcome == "success" else "Compromised"
                        if detected and outcome != "failure": status = "Blocked"
                        elif detected and outcome == "failure": status = "Attempted" # Detected but successful"""

text = text.replace(old_status_logic, new_status_logic)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
