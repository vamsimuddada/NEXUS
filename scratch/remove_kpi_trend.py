import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Remove the kpi-trend div completely from the HTML card
old_kpi = """        <div class="kpi-value">{value}</div>
        <div class="kpi-trend">{trend}</div>
    </div>"""

new_kpi = """        <div class="kpi-value" style="margin-bottom: 12px;">{value}</div>
    </div>"""

text = text.replace(old_kpi, new_kpi)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
