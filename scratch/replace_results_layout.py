import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# I will use a precise split to replace the entire `try:` block inside `if not report_files: else:`
start_marker = "          latest_report = report_files[0]\n          try:"
end_marker = "      except Exception as e:\n          st.error(f\"Failed to load Threat Intel: {e}\")"

# We must find the EXACT end of the try block for the results page.
# Wait, the try block ends at `st.error(f"Error parsing report: {e}")`!
# Let's use regex or split to be perfectly precise.
