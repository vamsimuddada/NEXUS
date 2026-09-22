import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the syntax error in About page
text = text.replace(
    'st.markdown("<div style="font-family:\'Inter\'',
    'st.markdown("<div style=\\"font-family:\'Inter\''
)
text = text.replace(
    'st.markdown("<h3 style="font-family:\'Inter\'',
    'st.markdown("<h3 style=\\"font-family:\'Inter\''
)

# Fix APT28 header syntax specifically
text = text.replace(
    'st.markdown(f"<h3 style="color:#ef4444; font-family:\'Inter\'',
    'st.markdown(f"<h3 style=\\"color:#ef4444; font-family:\'Inter\''
)

# Re-escape the closing quotes!
# Wait, this is getting ridiculous. I will just restore from dashboard_final_locked.py, re-run all safe scripts, and then use a PERFECT rebuild_threat_intel script that uses SINGLE QUOTES for outer st.markdown!
