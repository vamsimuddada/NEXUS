import codecs

with codecs.open('scripts/run_simulation.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the buffering on TextIOWrapper so stdout streams cleanly
old_io = 'sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")'
new_io = 'sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", write_through=True)'

text = text.replace(old_io, new_io)

with codecs.open('scripts/run_simulation.py', 'w', 'utf-8') as f:
    f.write(text)
