import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Change "About NEXUS" to something more tactical
text = text.replace(
    "<div style='font-family:\\'Inter\\', sans-serif; font-size:3.5rem; font-weight:900; color:#0B1121; letter-spacing:-2px; margin-bottom:16px;'>About NEXUS</div>",
    "<div style='font-family:\\'Inter\\', sans-serif; font-size:3.5rem; font-weight:900; color:#0B1121; letter-spacing:-2px; margin-bottom:16px;'>PROJECT NEXUS MANIFESTO</div>"
)

# Remove the duplicate Simulation Lifecycle block.
# We will match the first one and delete it.
pattern = re.compile(
    r"<h3 style='font-family: 'Google Sans', sans-serif; font-weight:800; color:#0f172a; margin-top:32px; margin-bottom:24px;'>Simulation Lifecycle</h3>.*?</div>\s*\"\"\", unsafe_allow_html=True\)",
    re.DOTALL
)
text = pattern.sub("", text)

# Then fix the font of the remaining one to Inter
text = text.replace(
    "<h3 style='font-family:\\'Space Grotesk\\', sans-serif; font-weight:800; color:#0f172a; margin-top:32px; margin-bottom:24px;'>Simulation Lifecycle</h3>",
    "<h3 style='font-family:\\'Inter\\', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;'>Simulation Lifecycle</h3>"
)

# Also fix the "Tech Stack" header to Inter while we are here
text = text.replace(
    "<h3 style='font-family: 'Google Sans', sans-serif; font-weight:800; color:#0f172a; margin-top:32px; margin-bottom:24px;'>Tech Stack</h3>",
    "<h3 style='font-family:\\'Inter\\', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;'>Tech Stack</h3>"
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
