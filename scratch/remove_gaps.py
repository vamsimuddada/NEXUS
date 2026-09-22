import re

with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Remove st.divider()
code = code.replace("st.divider()", "")

# 2. Add padding-top fix to CSS
css_fix = '''
/* -- Remove Massive Native Gaps -- */
[data-testid="stAppViewBlockContainer"] { padding-top: 1rem !important; }
[data-testid="stTabs"] { margin-top: -10px !important; }
'''
code = code.replace("</style>", css_fix + "</style>")

# 3. Pull up logo
code = code.replace("margin-top: -10px;'>", "margin-top: -40px;'>")

# 4. Pull up Security Command Center header
code = code.replace("margin-top:-10px; font-size: 2.8rem; letter-spacing: -1px;'>Security Command Center", "margin-top:-35px; font-size: 2.8rem; letter-spacing: -1px;'>Security Command Center")

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Gaps removed.")
