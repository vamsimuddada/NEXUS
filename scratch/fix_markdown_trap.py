import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# I will write a regex to completely strip all leading whitespace from every line of the card_html
import re

# Find the block where card_html is defined
idx_card = text.find('card_html = f"""')
if idx_card != -1:
    # Actually, it's easier to just find the entire card_html string definition and dedent it manually
    idx_end = text.find('"""\n                            st.markdown(card_html, unsafe_allow_html=True)', idx_card)
    if idx_end != -1:
        block = text[idx_card:idx_end]
        
        # We want to keep `card_html = f"""` but dedent everything inside the string
        lines = block.split('\n')
        new_lines = [lines[0]]
        for line in lines[1:]:
            new_lines.append(line.lstrip())
            
        dedented_block = '\n'.join(new_lines)
        
        text = text[:idx_card] + dedented_block + text[idx_end:]
        
with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
