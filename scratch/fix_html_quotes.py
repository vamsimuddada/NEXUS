import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the broken HTML style attributes in the About page.
# Any instance of `style='font-family:\'Inter\'...` needs to become `style="font-family:'Inter'...`

# Because python string literals might be messy, let's just do a blanket regex replacement
# We are replacing `style='...'` with `style="..."` anywhere we see `font-family:` in the About page.

idx1 = text.find('PROJECT NEXUS MANIFESTO')
if idx1 == -1: idx1 = text.find('About NEXUS')
# Look backwards to the start of the line for idx1
idx1 = text.rfind('\n', 0, idx1)

idx2 = text.find('st.stop()', idx1)

about = text[idx1:idx2]

# Fix the specific headers
about = re.sub(
    r"<div style='font-family:\\?'Inter\\?', sans-serif; font-size:3rem; font-weight:800; color:#0B1121; margin-bottom:16px;'>PROJECT NEXUS MANIFESTO</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:3.5rem; font-weight:900; color:#0f172a; letter-spacing:-2px; margin-bottom:16px;\">PROJECT NEXUS MANIFESTO</div>",
    about
)

about = re.sub(
    r"<h3 style='font-family:\\?'Inter\\?', sans-serif; font-weight:800; color:#0B1121; margin-bottom:24px;'>System Architecture</h3>",
    r"<h3 style=\"font-family:'Inter', sans-serif; font-weight:800; color:#0f172a; letter-spacing:-1px; margin-bottom:24px;\">System Architecture</h3>",
    about
)

about = re.sub(
    r"<div style='font-family:\\?'Inter\\?', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121;'>Red Team \(Autonomous Attackers\)</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px;\">Red Team (Autonomous Attackers)</div>",
    about
)

about = re.sub(
    r"<div style='font-family:\\?'Inter\\?', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121;'>Blue Team \(SIEM & Defense\)</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px;\">Blue Team (SIEM & Defense)</div>",
    about
)

about = re.sub(
    r"<div style='font-family:\\?'Inter\\?', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121;'>The AI Brain & Technology Stack</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px;\">The AI Brain & Technology Stack</div>",
    about
)

about = re.sub(
    r"<h3 style='font-family:\\?'Inter\\?', sans-serif; font-weight:800; color:#0B1121; margin-top:32px; margin-bottom:24px;'>Simulation Lifecycle</h3>",
    r"<h3 style=\"font-family:'Inter', sans-serif; font-weight:800; color:#0f172a; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;\">Simulation Lifecycle</h3>",
    about
)

# And fix any leftover `font-family:\'Inter\'` in paragraphs or lists.
# Actually, the paragraphs were fine because they didn't have `font-family` originally, my previous script added them with double quotes.

text = text[:idx1] + about + text[idx2:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
