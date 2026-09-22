import codecs

# Read original dream CSS
with codecs.open('scratch/current_dash.py', 'r', 'utf-16') as f:
    orig = f.read()

orig_style = orig[orig.find('<style>'):orig.find('</style>') + 8]

# Read current dashboard
with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    dash = f.read()

# Replace the style block
dash_start = dash.find('<style>')
dash_end = dash.find('</style>') + 8

new_dash = dash[:dash_start] + orig_style + dash[dash_end:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(new_dash)
