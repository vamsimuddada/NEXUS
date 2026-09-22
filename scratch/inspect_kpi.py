import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Fix the KPI block
# Find the SQL try/except block for KPIs
idx_kpi_start = text.find('total_battles = 0')
idx_kpi_end = text.find('st.markdown("<h3 style=\'color:#0f172a; font-family: \\\'Google Sans\\\', sans-serif; font-weight:800; letter-spacing:-1px; margin-top:32px; margin-bottom:16px;\'>Active Operation</h3>", unsafe_allow_html=True)')
if idx_kpi_end == -1:
    idx_kpi_end = text.find("Active Operation</h3>") - 200 # approximate if we changed fonts

print(text[idx_kpi_start:idx_kpi_start+1000])

# 2. Fix the Top Alerts block
idx_alert_start = text.find('Top Alerts by Severity</h3>')
idx_alert_end = text.find('Live Threat Graph</h3>')
print("\n===========\n")
print(text[idx_alert_start:idx_alert_start+1500])
