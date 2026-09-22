with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_html = '''    <div>
        <div style="font-family:'Google Sans', 'Plus Jakarta Sans', sans-serif; font-size:3.2rem; font-weight:800; color:#0f172a; line-height:1; letter-spacing:-2px;">NEXUS</div>
    </div>'''

new_html = '''    <div style="display: flex; align-items: baseline; gap: 16px;">
        <div style="font-family:'Google Sans', 'Plus Jakarta Sans', sans-serif; font-size:3.2rem; font-weight:800; color:#0f172a; line-height:1; letter-spacing:-2px;">NEXUS</div>
        <div style="font-family:'Google Sans', 'Plus Jakarta Sans', sans-serif; font-size:1.1rem; font-weight:600; color:#64748b; letter-spacing:0px;">Neural Exploitation & eXplainable Unified Security</div>
    </div>'''

code = code.replace(old_html, new_html)

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Acronym updated.")
