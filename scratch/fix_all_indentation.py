import codecs
import textwrap

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

start_str = '    st.markdown(\'\'\''
end_str = "    ''', unsafe_allow_html=True)"

# Find the specific st.markdown block after "About the Developer"
title_idx = text.find('About the Developer')
start_idx = text.find(start_str, title_idx)
end_idx = text.find(end_str, start_idx)

if start_idx != -1 and end_idx != -1:
    end_idx += len(end_str)
    old_block = text[start_idx:end_idx]
    
    # We will rebuild the block by stripping ALL leading spaces from every line inside the string
    lines = old_block.split('\n')
    new_lines = []
    for i, line in enumerate(lines):
        if i == 0 or i == len(lines) - 1:
            # Keep the python code lines untouched
            new_lines.append(line)
        else:
            # Strip all leading spaces from the HTML lines
            new_lines.append(line.lstrip())
            
    new_block = '\n'.join(new_lines)
    
    text = text.replace(old_block, new_block)
    
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(text)
