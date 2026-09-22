import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# The existing LinkedIn HTML block inside the minified string
linkedin_block = """<div style="display:flex; align-items:center; gap:14px; color:#475569;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg><a href="https://www.linkedin.com/in/vamsimuddada/" target="_blank" style="font-size:1.0rem; font-family:'Space Grotesk', sans-serif; color:#3b82f6; text-decoration:none;">LinkedIn Profile</a></div>"""

# The new GitHub HTML block to insert right after it
github_block = """<div style="display:flex; align-items:center; gap:14px; color:#475569;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg><a href="https://github.com/vamsimuddada" target="_blank" style="font-size:1.0rem; font-family:'Space Grotesk', sans-serif; color:#3b82f6; text-decoration:none;">GitHub Profile</a></div>"""

# Replace the LinkedIn block with (LinkedIn Block + GitHub Block)
text = text.replace(linkedin_block, linkedin_block + github_block)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
