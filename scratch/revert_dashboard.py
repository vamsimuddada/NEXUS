import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Remove the Global Evolution Analytics section from the dashboard
start_marker = "    # --- ADVANCED ANALYTICS ---"
end_marker = "    except Exception as e:\n        st.error(f\"Failed to render advanced analytics: {e}\")"

start_idx = text.find(start_marker)
end_idx = text.find(end_marker) + len(end_marker)

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + text[end_idx:]
    
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(text)
