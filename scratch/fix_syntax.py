import codecs

with codecs.open('core/simulation.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the syntax error
text = text.replace('turn_attack_logs.append(log)}"\n                )', 'turn_attack_logs.append(log)')

with codecs.open('core/simulation.py', 'w', 'utf-8') as f:
    f.write(text)
