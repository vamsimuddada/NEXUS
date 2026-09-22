import re

with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace any garbage after expanded") up to </div>
c = re.sub(r'initial_sidebar_state="expanded"\).*?</div>\n?', 'initial_sidebar_state="expanded")\n', c, flags=re.DOTALL)

# Let's also check if literal backslash-n was inserted
c = c.replace(r'\n', '\n') # convert literal backslash-n to actual newlines

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(c)
print("Cleaned.")
