with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "st.set_page_config" in line:
        new_lines.append(line)
        skip = True
    elif skip and "st.markdown(" in line and "<style>" in line:
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Hard fix applied.")
