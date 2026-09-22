import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    current_text = f.read()

with codecs.open('scripts/dashboard_final_locked.py', 'r', 'utf-8') as f:
    backup_text = f.read()

start_idx = current_text.find('with tab2:')
backup_start_idx = backup_text.find('with tab2:')

if start_idx != -1 and backup_start_idx != -1:
    # Replace the current tab2 to the end with the backup's tab2 to the end
    restored_text = current_text[:start_idx] + backup_text[backup_start_idx:]
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(restored_text)
