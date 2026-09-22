import re

with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Fix the broken top
code = code.replace('initial_sidebar_state="expanded")\\n\\n</div>', 'initial_sidebar_state="expanded")')
code = code.replace('initial_sidebar_state="expanded")\\n\\n', 'initial_sidebar_state="expanded")')

# 2. Extract the block from the bottom
match = re.search(r'# ------------------------------------------------------------------------------\n#  ABOUT PROJECT PAGE \(ROUTING\).*?(?=st\.stop\(\))st\.stop\(\)', code, re.DOTALL)

if match:
    block = match.group(0)
    # Remove it from the bottom
    code = code.replace(block, "")
    
    # Inject it at the top
    target = 'initial_sidebar_state="expanded")'
    if target in code:
        code = code.replace(target, target + '\n\n' + block + '\n')
    
    with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Fixed.")
else:
    print("Block not found!")
