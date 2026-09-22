import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

if "import codecs" not in text:
    text = text.replace("import sys, os, json, time, threading, queue, sqlite3", "import sys, os, json, time, threading, queue, sqlite3, codecs")
    
with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
