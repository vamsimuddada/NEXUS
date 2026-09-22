import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

start_idx = text.find('THREAT INTELLIGENCE LEADERBOARD')
if start_idx != -1:
    # Walk backward to find the start of the comment line
    line_start = text.rfind('\n', 0, start_idx)
    if line_start != -1:
        start_idx = line_start

end_idx = text.find("elif st.session_state.current_page == 'analytics':", start_idx)

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + '\n\n' + text[end_idx:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
