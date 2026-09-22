import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix header
text = text.replace(
    "<div style='font-family:\\'Space Grotesk\\', sans-serif; font-size:3rem; font-weight:800; color:#0f172a; margin-bottom:16px;'>About NEXUS</div>",
    "<div style=\"font-family:'Inter', sans-serif; font-size:3.5rem; font-weight:900; color:#0B1121; letter-spacing:-2px; margin-bottom:16px;\">PROJECT NEXUS MANIFESTO</div>"
)

# Fix subheaders
text = text.replace(
    "<h3 style='font-family:\\'Space Grotesk\\', sans-serif; font-weight:800; color:#0f172a; margin-bottom:24px;'>System Architecture</h3>",
    "<h3 style=\"font-family:'Inter', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-bottom:24px;\">System Architecture</h3>"
)
text = text.replace(
    "<div style='font-family:\\'Space Grotesk\\', sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a;'>Red Team (Autonomous Attackers)</div>",
    "<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;\">Red Team (Autonomous Attackers)</div>"
)
text = text.replace(
    "<div style='font-family:\\'Space Grotesk\\', sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a;'>Blue Team (SIEM & Defense)</div>",
    "<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;\">Blue Team (SIEM & Defense)</div>"
)
text = text.replace(
    "<div style='font-family:\\'Space Grotesk\\', sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a;'>The AI Brain & Technology Stack</div>",
    "<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;\">The AI Brain & Technology Stack</div>"
)
text = text.replace(
    "<h3 style='font-family:\\'Space Grotesk\\', sans-serif; font-weight:800; color:#0f172a; margin-top:32px; margin-bottom:24px;'>Simulation Lifecycle</h3>",
    "<h3 style=\"font-family:'Inter', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;\">Simulation Lifecycle</h3>"
)
text = text.replace(
    "<h3 style='font-family: 'Google Sans', sans-serif; font-weight:800; color:#0f172a; margin-top:32px; margin-bottom:24px;'>Tech Stack</h3>",
    "<h3 style=\"font-family:'Inter', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;\">Tech Stack</h3>"
)
text = text.replace(
    "<h3 style='font-family: 'Google Sans', sans-serif; font-weight:800; color:#0f172a; margin-top:32px; margin-bottom:24px;'>Simulation Lifecycle</h3>",
    "<!-- duplicate header removed -->"
)

text = text.replace("<p style='font-size:1.15rem;", "<p style=\"font-family:'Inter', sans-serif; font-size:1.15rem;")
text = text.replace("<p style='font-size:1.05rem;", "<p style=\"font-family:'Inter', sans-serif; font-size:1.05rem;")
text = text.replace("<p style='color:#475569;", "<p style=\"font-family:'Inter', sans-serif; color:#475569;")
text = text.replace("<ul style='color:#475569;", "<ul style=\"font-family:'Inter', sans-serif; color:#475569;")
text = text.replace("<ol style='color:#475569;", "<ol style=\"font-family:'Inter', sans-serif; color:#475569;")

# And remove the duplicate lifecycle body
# Actually, the duplicate lifecycle body is identical to the first one, let me just find it and wipe it.
idx_dupe = text.find("<!-- duplicate header removed -->")
if idx_dupe != -1:
    idx_end = text.find('st.markdown("<h3 style="font-family:\'Inter\', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;">Tech Stack</h3>', idx_dupe)
    if idx_end != -1:
        text = text[:idx_dupe] + text[idx_end:]


with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
