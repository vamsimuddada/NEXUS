import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Define the exact bad string to remove
bad_css1 = """/* The background track of the bar */
[data-testid="stProgress"] > div > div {
    background-color: #e2e8f0 !important;
    border-radius: 2px !important;
    height: 8px !important;
}"""

bad_css2 = """/* The actual moving fill line */
[data-testid="stProgress"] [role="progressbar"] {
    background: linear-gradient(90deg, #0f172a, #3b82f6) !important;
    border-radius: 2px !important;
    height: 8px !important;
    box-shadow: 0 0 12px rgba(59, 130, 246, 0.6) !important;
}"""

bad_css3 = """*/
[data-testid="stProgress"] p {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 800 !important;
    color: #3b82f6 !important;
    letter-spacing: 0.5px !important;
    font-size: 1rem !important;
}"""

text = text.replace(bad_css1, "")
text = text.replace(bad_css2, "")
text = text.replace(bad_css3, "")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
