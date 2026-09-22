import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Extract the @import URL line
import_match = re.search(r"(@import url\('[^']+'\);)", text)
if import_match:
    import_line = import_match.group(1)
    
    # Remove it from wherever it is
    text = text.replace(import_line, "")
    
    # Put it immediately after <style>
    text = text.replace("<style>", f"<style>\n{import_line}")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
