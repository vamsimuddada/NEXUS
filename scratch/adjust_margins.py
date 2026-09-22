with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_style = "margin-bottom: 12px; margin-top: -40px;"
new_style = "margin-bottom: 32px; margin-top: -55px;"

code = code.replace(old_style, new_style)

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Margins adjusted.")
