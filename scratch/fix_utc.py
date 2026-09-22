import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the duplicate UTC bug
text = text.replace('f"**Generated:** {timestamp} UTC\\n",', 'f"**Generated:** {timestamp}\\n",')

# Fix the slight grammar error in the SIGMA log
text = text.replace('new behavioral heuristics over the course', 'new behavioral heuristic(s) over the course')

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
