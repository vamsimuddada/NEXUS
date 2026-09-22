import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Safe duplicate removal
idx1 = text.find('Simulation Lifecycle')
if idx1 != -1:
    idx2 = text.find('Simulation Lifecycle', idx1 + 20)
    if idx2 != -1:
        # Find the start of the st.markdown line containing the duplicate
        start_dup = text.rfind('st.markdown', 0, idx2)
        # Find the NEXT header which is Tech Stack
        idx_tech = text.find('Tech Stack', idx2)
        if idx_tech != -1:
            start_tech = text.rfind('st.markdown', 0, idx_tech)
            text = text[:start_dup] + text[start_tech:]

# Font replacement
idx_end = text.find('st.stop()')
if idx_end == -1: idx_end = len(text)
about = text[:idx_end]
about = about.replace('Space Grotesk', 'Inter')
about = about.replace('Google Sans', 'Inter')
about = about.replace('color:#0f172a', 'color:#0B1121')
about = about.replace('About NEXUS', 'PROJECT NEXUS MANIFESTO')
text = about + text[idx_end:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
