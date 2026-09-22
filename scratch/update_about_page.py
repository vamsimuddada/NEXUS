import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace fonts in About page
text = text.replace(
    "<div style='font-family:\\'Space Grotesk\\', sans-serif; font-size:3rem; font-weight:800; color:#0f172a; margin-bottom:16px;'>About NEXUS</div>",
    "<div style='font-family:\\'Inter\\', sans-serif; font-size:3.5rem; font-weight:900; color:#0B1121; letter-spacing:-2px; margin-bottom:16px;'>About NEXUS</div>"
)

text = text.replace(
    "<h3 style='font-family:\\'Space Grotesk\\', sans-serif; font-weight:800; color:#0f172a; margin-bottom:24px;'>System Architecture</h3>",
    "<h3 style='font-family:\\'Inter\\', sans-serif; font-weight:800; color:#0B1121; letter-spacing:-1px; margin-bottom:24px;'>System Architecture</h3>"
)

text = text.replace(
    "<div style='font-family:\\'Space Grotesk\\', sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a;'>Red Team (Autonomous Attackers)</div>",
    "<div style='font-family:\\'Inter\\', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;'>Red Team (Autonomous Attackers)</div>"
)

text = text.replace(
    "<div style='font-family:\\'Space Grotesk\\', sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a;'>Blue Team (SIEM & Defense)</div>",
    "<div style='font-family:\\'Inter\\', sans-serif; font-size:1.3rem; font-weight:800; color:#0B1121; letter-spacing:-0.5px;'>Blue Team (SIEM & Defense)</div>"
)

# And remove the arrow emoji from the back button to match the emoji-less military aesthetic
text = text.replace('st.button("⬅ Back to Command Center")', 'st.button("BACK TO COMMAND CENTER")')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
