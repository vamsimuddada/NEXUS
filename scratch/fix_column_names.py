import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Clarify table headers
text = text.replace('["Rank", "Entity", "ELO", "Peak ELO", "Battles", "Win Rate", "Evasion Rate"]', '["Rank", "Entity", "ELO", "Peak ELO", "Total History", "Win Rate", "Evasion Rate"]')
text = text.replace('["Agent", "Battles", "Top Technique", "Avg Stealth"]', '["Agent", "Total History", "Top Technique", "Avg Stealth"]')

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
