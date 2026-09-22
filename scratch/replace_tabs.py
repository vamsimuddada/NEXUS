import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

sidebar_code = """with st.sidebar:
    st.markdown('''
    <div style='text-align:center; padding-bottom: 32px;'>
        <div style='margin-bottom:12px; color:#2563eb;'>
            <svg xmlns="http://www.w3.org/2000/svg" width="54" height="54" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="display:inline-block; filter: drop-shadow(0 4px 6px rgba(37, 99, 235, 0.2));">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
        </div>
        <div class="nexus-brand">NEXUS</div>
        <div style='font-size:0.8rem; color:#64748b; font-weight:700; letter-spacing:2px; margin-top:4px;'>COMMAND CENTER</div>
    </div>
    ''', unsafe_allow_html=True)
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "SOC Overview"
    
    st.session_state.current_page = st.radio("NAVIGATION", ["SOC Overview", "Mission Control", "Test Results", "Analytics & Export"], label_visibility="collapsed")
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption("SYSTEM STATUS")
    st.markdown("<div style='display:flex; align-items:center; gap:8px;'><span class='status-dot-green'></span> <span style='font-size:0.85rem; color:#5f6368; font-weight:600;'>Vector Engine</span></div>", unsafe_allow_html=True)
"""

text = re.sub(r'tabs = st\.tabs\(\[.*?tab_export = tabs', sidebar_code, text, flags=re.DOTALL)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
    print("Tabs replaced successfully!")
