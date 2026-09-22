import sys, re

with open('scratch/current_dash.py', 'r', encoding='utf-16') as f:
    code = f.read()

# Normalize line endings so regex works
code = code.replace('\r\n', '\n')

css_patch = '''
/* HIDE SIDEBAR ENTIRELY */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }
'''
code = code.replace('/* -- Floating Holographic Orbs -- */', css_patch + '\n/* -- Floating Holographic Orbs -- */')

branding = '''
# ------------------------------------------------------------------------------
#  MAIN DASHBOARD HEADER
# ------------------------------------------------------------------------------
c_logo, c_sys1, c_sys2, c_sys3 = st.columns([4, 2, 2, 2])
with c_logo:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 20px; margin-bottom: 12px; margin-top: -10px;'>
        <div style='width:60px; height:60px; border-radius:50%; background:linear-gradient(135deg, #e0e7ff, #ffffff); display:flex; align-items:center; justify-content:center; box-shadow: 0 10px 25px rgba(37, 99, 235, 0.15); border: 1px solid rgba(255,255,255,1);'>
            <svg width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='#3b82f6' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>
                <path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'></path>
            </svg>
        </div>
        <div>
            <div style='font-family:"Space Grotesk", sans-serif; font-size:2.8rem; font-weight:800; color:#0f172a; line-height:1; letter-spacing:-2px;'>NEXUS</div>
            <div style='font-size:0.8rem; font-weight:800; color:#3b82f6; letter-spacing:4px;'>COMMAND CENTER</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with c_sys1:
    st.markdown("""<div class="status-card" style="margin-top:10px;"><div class="status-title">Vector Engine</div><div class="status-value"><div class="pulse-dot"></div>Online</div></div>""", unsafe_allow_html=True)
with c_sys2:
    st.markdown("""<div class="status-card" style="margin-top:10px;"><div class="status-title">SIEM Forwarder</div><div class="status-value"><div class="pulse-dot" style="background:#f59e0b; box-shadow: 0 0 8px #f59e0b;"></div>Idle</div></div>""", unsafe_allow_html=True)
with c_sys3:
    st.markdown("""
    <div style='background:rgba(255,255,255,0.8); border:1px solid rgba(255,255,255,1); padding:8px 16px; border-radius:16px; display:flex; align-items:center; gap:12px; box-shadow: 0 4px 15px rgba(15,23,42,0.05); margin-top:10px;'>
        <div style='width:36px; height:36px; border-radius:50%; background:linear-gradient(135deg, #3b82f6, #8b5cf6); color:white; display:flex; align-items:center; justify-content:center; font-weight:800;'>V</div>
        <div>
            <div style='font-size:0.75rem; color:#64748b; font-weight:700; text-transform:uppercase;'>System Admin</div>
            <div style='font-size:0.9rem; color:#0f172a; font-weight:800; line-height:1;'>VAMSI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["SOC Overview", "Mission Control", "Threat Intelligence", "Analytics & Export"])
'''

# Delete the with st.sidebar block
code = re.sub(r'# ------------------------------------------------------------------------------\n#  SIDEBAR.*?# ------------------------------------------------------------------------------\n#  MAIN CONTENT', branding + '\n# ------------------------------------------------------------------------------\n#  MAIN CONTENT', code, flags=re.DOTALL)

code = code.replace('if page == "SOC Overview":', 'with tab1:')
code = code.replace('elif page == "Mission Control":', 'with tab2:')
code = code.replace('elif page == "Threat Intelligence":', 'with tab3:')
code = code.replace('elif page == "Analytics & Export":', 'with tab4:')

# Also replace st.markdown("<div class='hero-header'>Global SOC Overview</div>" inside tab1 so it doesnt have massive margin
code = code.replace("<div class='hero-header'>Global SOC Overview</div>", "<div class='hero-header' style='margin-top:-20px;'>Global SOC Overview</div>")

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Rewrote dashboard successfully.")
