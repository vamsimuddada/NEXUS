import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the JSON key path
text = text.replace('val = bdata.get("evolution_summary", {}).get("total_sigma_rules", 10)', 'val = bdata.get("total_sigma_rules", 10)')

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
