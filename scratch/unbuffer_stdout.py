import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Add the -u flag to the python executable call to force unbuffered stdout
old_cmd = 'cmd = [sys.executable, "scripts/run_simulation.py", "--provider", prov, "--turns", str(turns), "--save"]'
new_cmd = 'cmd = [sys.executable, "-u", "scripts/run_simulation.py", "--provider", prov, "--turns", str(turns), "--save"]'

text = text.replace(old_cmd, new_cmd)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
