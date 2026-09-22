import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace the indented HTML block with a flush-left HTML block to prevent Markdown from interpreting it as a code block.
pattern = re.compile(r'st\.markdown\(f"""\s*<div style=\'background: #ffffff;', re.DOTALL)

# Let's just write a custom replace using a simple split
idx = text.find('st.markdown(f"""\n            <div style=\'background: #ffffff;')
if idx != -1:
    end_idx = text.find('""", unsafe_allow_html=True)', idx)
    old_block = text[idx:end_idx+len('""", unsafe_allow_html=True)')]
    
    # Strip leading spaces from each line in the block
    lines = old_block.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('            '):
            new_lines.append(line[12:])
        else:
            new_lines.append(line)
            
    new_block = '\n'.join(new_lines)
    text = text.replace(old_block, new_block)
    
with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
