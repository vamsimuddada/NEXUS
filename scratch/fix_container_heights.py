import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Force a fixed height on the description paragraphs in Tab 3 so the containers don't dynamically resize and break symmetry.
text = text.replace(
    '<p style="font-family:\'Inter\', sans-serif; color:#64748b; font-size:0.95rem; line-height:1.6; margin-bottom:20px;">Generate',
    '<p style="font-family:\'Inter\', sans-serif; color:#64748b; font-size:0.95rem; line-height:1.6; margin-bottom:20px; min-height: 75px;">Generate'
)

text = text.replace(
    '<p style="font-family:\'Inter\', sans-serif; color:#64748b; font-size:0.95rem; line-height:1.6; margin-bottom:20px;">Download',
    '<p style="font-family:\'Inter\', sans-serif; color:#64748b; font-size:0.95rem; line-height:1.6; margin-bottom:20px; min-height: 75px;">Download'
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
