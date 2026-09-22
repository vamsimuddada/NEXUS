import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Add --save to the subprocess command
old_cmd = 'cmd = [sys.executable, "scripts/run_simulation.py", "--provider", prov, "--turns", str(turns)]'
new_cmd = 'cmd = [sys.executable, "scripts/run_simulation.py", "--provider", prov, "--turns", str(turns), "--save"]'

text = text.replace(old_cmd, new_cmd)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
