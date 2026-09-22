with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_logo = '''        <div style='font-family:'Google Sans', 'Plus Jakarta Sans', sans-serif; font-size:2.8rem; font-weight:800; color:#0f172a; line-height:1; letter-spacing:-2px;'>NEXUS</div>
        <div style='font-size:0.8rem; font-weight:800; color:#3b82f6; letter-spacing:4px;'>COMMAND CENTER</div>'''

new_logo = '''        <div style="font-family:'Google Sans', 'Plus Jakarta Sans', sans-serif; font-size:3.2rem; font-weight:800; color:#0f172a; line-height:1; letter-spacing:-2px;">NEXUS</div>'''

code = code.replace(old_logo, new_logo)

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Logo fixed.")
