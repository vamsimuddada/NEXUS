with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Remove JS
js_start = code.find('# ------------------------------------------------------------------------------\\n#  JAVASCRIPT TABS SCROLL SYNC')
if js_start != -1:
    js_end = code.find('""", height=0, width=0)') + len('""", height=0, width=0)')
    code = code[:js_start] + code[js_end:]

# Clean CSS
css_start = code.find('/* -- Break Streamlit CSS Traps -- */')
if css_start != -1:
    css_end = code.find('/* -- Floating Tabs Navigation -- */')
    code = code[:css_start] + code[css_end:]

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Cleaned.")
