import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace About NEXUS header
text = re.sub(
    r"<div style='font-family:[^>]+>About NEXUS</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:3.5rem; font-weight:900; color:#0B1121; letter-spacing:-2px; margin-bottom:16px;\">PROJECT NEXUS MANIFESTO</div>",
    text
)

# Replace System Architecture
text = re.sub(
    r"<h3 style='font-family:[^>]+>System Architecture</h3>",
    r"<h3 style=\"font-family:'Inter', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-bottom:24px;\">System Architecture</h3>",
    text
)

# Replace Red Team header
text = re.sub(
    r"<div style='font-family:[^>]+>Red Team \(Autonomous Attackers\)</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;\">Red Team (Autonomous Attackers)</div>",
    text
)

# Replace Blue Team header
text = re.sub(
    r"<div style='font-family:[^>]+>Blue Team \(SIEM & Defense\)</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;\">Blue Team (SIEM & Defense)</div>",
    text
)

# Replace AI Brain header
text = re.sub(
    r"<div style='font-family:[^>]+>The AI Brain & Technology Stack</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;\">The AI Brain & Technology Stack</div>",
    text
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
