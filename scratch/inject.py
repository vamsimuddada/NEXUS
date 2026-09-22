import sys

# Get the missing functions from current_dash.py
missing_code = '''
def kpi_card(title, value, trend, color, icon_svg):
    return f"""
    <div class="kpi-card" style="border-top-color: {color};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div class="kpi-title">{title}</div>
            <div style="color: {color}; opacity: 0.8; width: 20px; height: 20px;">{icon_svg}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-trend">{trend}</div>
    </div>
    """

ICON_F1 = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>'
ICON_SHIELD = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>'
ICON_DB = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>'
ICON_WARN = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>'
'''

with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Inject right before tab1, tab2, tab3, tab4 = st.tabs(...)
code = code.replace('tab1, tab2, tab3, tab4 = st.tabs', missing_code + '\n\ntab1, tab2, tab3, tab4 = st.tabs')

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Injected successfully.")
