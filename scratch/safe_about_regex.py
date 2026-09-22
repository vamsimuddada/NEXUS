import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix header
text = re.sub(
    r"<div style=[^>]*?About NEXUS</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:3.5rem; font-weight:900; color:#0B1121; letter-spacing:-2px; margin-bottom:16px;\">PROJECT NEXUS MANIFESTO</div>",
    text
)

# Fix subheaders
text = re.sub(
    r"<h3 style=[^>]*?System Architecture</h3>",
    r"<h3 style=\"font-family:'Inter', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-bottom:24px;\">System Architecture</h3>",
    text
)
text = re.sub(
    r"<div style=[^>]*?Red Team \(Autonomous Attackers\)</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;\">Red Team (Autonomous Attackers)</div>",
    text
)
text = re.sub(
    r"<div style=[^>]*?Blue Team \(SIEM & Defense\)</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;\">Blue Team (SIEM & Defense)</div>",
    text
)
text = re.sub(
    r"<div style=[^>]*?The AI Brain & Technology Stack</div>",
    r"<div style=\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;\">The AI Brain & Technology Stack</div>",
    text
)

# Fix Simulation Lifecycle
text = re.sub(
    r"<h3 style=[^>]*?Simulation Lifecycle</h3>",
    r"<h3 style=\"font-family:'Inter', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;\">Simulation Lifecycle</h3>",
    text,
    count=1
)

# Fix Tech Stack
text = re.sub(
    r"<h3 style=[^>]*?Tech Stack</h3>",
    r"<h3 style=\"font-family:'Inter', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;\">Tech Stack</h3>",
    text
)

# Remove the duplicate simulation lifecycle
text = re.sub(
    r"(st\.markdown\(\"<h3 style=.*?Simulation Lifecycle</h3>\".*?)st\.markdown\(\"<h3 style=.*?Tech Stack</h3>",
    r"\g<1>st.markdown(\"<h3 style=\"font-family:'Inter', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;\">Tech Stack</h3>",
    text,
    flags=re.DOTALL
)

# Apply Inter to paragraphs and lists in the About section
idx1 = text.find('PROJECT NEXUS MANIFESTO')
idx2 = text.find('with tab2:')
if idx1 != -1 and idx2 != -1:
    about_text = text[idx1:idx2]
    about_text = re.sub(r"<p style='[^']*'", r"<p style=\"font-family:'Inter', sans-serif; color:#475569; font-size:1.05rem; line-height:1.7; margin-bottom:0;\"", about_text)
    about_text = re.sub(r"<ul style='[^']*'", r"<ul style=\"font-family:'Inter', sans-serif; color:#475569;\"", about_text)
    about_text = re.sub(r"<ol style='[^']*'", r"<ol style=\"font-family:'Inter', sans-serif; color:#475569;\"", about_text)
    
    text = text[:idx1] + about_text + text[idx2:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
