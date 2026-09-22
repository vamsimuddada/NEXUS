import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

old_css = """/*  Progress Bar Integration  */
[data-testid="stProgress"] {
    margin-top: 8px;
}
[data-testid="stProgress"] > div > div > div > div > div {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 800 !important;
    color: #3b82f6 !important;
    letter-spacing: 0.5px;
    font-size: 0.85rem !important;
}
[data-testid="stProgressBar"] {
    background-color: #f1f5f9 !important;
    border-radius: 2px !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    height: 10px !important;
}
[data-testid="stProgressBar"] > div {
    background: linear-gradient(90deg, #3b82f6, #0f172a) !important;
    border-radius: 2px !important;
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
    height: 10px !important;
}"""

new_css = """/*  Progress Bar Integration  */
[data-testid="stProgress"] {
    margin-top: 8px;
}
/* The text label above the progress bar */
[data-testid="stProgress"] p {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 800 !important;
    color: #3b82f6 !important;
    letter-spacing: 0.5px !important;
    font-size: 1rem !important;
}
/* The background track of the bar */
[data-testid="stProgress"] > div > div {
    background-color: #e2e8f0 !important;
    border-radius: 2px !important;
    height: 8px !important;
}
/* The actual moving fill line */
[data-testid="stProgress"] [role="progressbar"] {
    background: linear-gradient(90deg, #0f172a, #3b82f6) !important;
    border-radius: 2px !important;
    height: 8px !important;
    box-shadow: 0 0 12px rgba(59, 130, 246, 0.6) !important;
}"""

text = text.replace(old_css, new_css)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
