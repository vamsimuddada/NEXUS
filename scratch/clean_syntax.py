with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Nuke the broken syntax
code = code.replace('initial_sidebar_state="expanded")\\n\\n\\n\\n\\n</div>\\n', 'initial_sidebar_state="expanded")\\n')
code = code.replace('initial_sidebar_state="expanded")\\n\\n</div>\\n', 'initial_sidebar_state="expanded")\\n')

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Cleaned.")
