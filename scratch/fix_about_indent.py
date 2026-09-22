import codecs
import autopep8

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Let's fix the specific lines by forcing everything in the if block to have exactly 4 spaces of indentation
lines = text.split('\n')
in_about = False
for i, line in enumerate(lines):
    if 'if st.query_params.get("page") == "about":' in line:
        in_about = True
        continue
    elif 'with tab2:' in line:
        in_about = False
        continue
    
    if in_about:
        if line.strip() == '': continue
        if line.lstrip().startswith('st.markdown'):
            lines[i] = '    ' + line.lstrip()
        elif line.lstrip().startswith('st.button'):
            lines[i] = '    ' + line.lstrip()
            
with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write('\n'.join(lines))
