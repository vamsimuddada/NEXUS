import codecs
with codecs.open('scratch/restore.py', 'r', encoding='cp1252') as f:
    text = f.read()

start = text.find("code = '''") + 10
end = text.rfind("'''")
if start != 9 and end != -1:
    dashboard_code = text[start:end]
    with codecs.open('scripts/dashboard.py', 'w', encoding='utf-8') as out:
        out.write(dashboard_code)
    print("Dashboard restored completely.")
else:
    print("Could not parse restore.py")
