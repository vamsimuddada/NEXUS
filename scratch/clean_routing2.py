with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix the broken top
code = code.replace('initial_sidebar_state="expanded")\\n\\n</div>', 'initial_sidebar_state="expanded")')

start_str = '# ------------------------------------------------------------------------------\\n#  ABOUT PROJECT PAGE (ROUTING)'
start_idx = code.find(start_str)

if start_idx != -1:
    end_str = 'st.stop()\\n'
    end_idx = code.find(end_str, start_idx) + len(end_str)
    
    block = code[start_idx:end_idx]
    code = code[:start_idx] + code[end_idx:]
    
    target = 'initial_sidebar_state="expanded")'
    code = code.replace(target, target + '\\n\\n' + block + '\\n')
    
    with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Fixed via string find.")
else:
    print("Not found.")
