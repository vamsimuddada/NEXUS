import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the Markdown whitespace trap in the metric grid
idx = text.find('grid_html = f\'\'\'')
idx_end = text.find('\'\'\'', idx + 20)

if idx != -1 and idx_end != -1:
    block = text[idx:idx_end]
    lines = block.split('\n')
    new_lines = [lines[0]]
    for line in lines[1:]:
        new_lines.append(line.lstrip())
    
    dedented = '\n'.join(new_lines)
    text = text[:idx] + dedented + text[idx_end:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
