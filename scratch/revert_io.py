import codecs

with codecs.open('scripts/run_simulation.py', 'r', 'utf-8') as f:
    text = f.read()

# Revert write_through=True
old_io = 'sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", write_through=True)'
new_io = 'sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")'

text = text.replace(old_io, new_io)

with codecs.open('scripts/run_simulation.py', 'w', 'utf-8') as f:
    f.write(text)
