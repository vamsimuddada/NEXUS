import re
import codecs

# Read the pristine dashboard backup (from the transcript)
with codecs.open('scratch/found_dashboard_finally.py', 'r', 'utf-8') as f:
    original_code = f.read()

# 1. Update the import glob
if "import glob" not in original_code:
    original_code = original_code.replace(
        "import sys, os, json, time, threading, queue, sqlite3", 
        "import sys, os, json, time, threading, queue, sqlite3, glob, codecs"
    )

# 2. Fix the start campaign toggle logic
toggle_old = """        if st.button("▶  START CAMPAIGN", type="primary", use_container_width=True):
            st.session_state.running = True
            st.session_state.start_time = time.time()"""

toggle_new = """        if st.button("▶  START CAMPAIGN", type="primary", use_container_width=True):
            st.session_state.running = True
            st.session_state.start_time = time.time()
            st.session_state.test_completed = False"""
            
original_code = original_code.replace(toggle_old, toggle_new)

# 3. Replace the entire Results block with the updated vectors and Stacked Layout!
# The Results block in the original_code looks something like this:
# html += f"""\n<div style="float: left... except Exception as e:\n    st.error(f"Error parsing report: {e}")

# We will use regex to find the `c1, c2 = st.columns([1, 1.5])` or whatever was originally there.
# Let's check what the original results block looked like.
# Wait, found_dashboard_finally.py was from "Professional dashboard rewrite" which had a custom HTML string for the Results page!
# It started with `html += f"""...` and ended with `st.html(html)`.
