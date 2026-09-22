import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Add bufsize=1 to subprocess.Popen to enforce line buffering
old_popen = 'process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")'
new_popen = 'process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1)'

text = text.replace(old_popen, new_popen)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
