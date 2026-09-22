# -*- coding: utf-8 -*-
with open('scratch/restore.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract the string between code = ''' and the last '''
start = text.find("code = '''") + 10
end = text.rfind("'''")
if start != -1 and end != -1:
    dashboard_code = text[start:end]
    with open('scripts/dashboard.py', 'w', encoding='utf-8') as out:
        out.write(dashboard_code)
    print("Dashboard restored completely.")
else:
    print("Could not parse restore.py")
