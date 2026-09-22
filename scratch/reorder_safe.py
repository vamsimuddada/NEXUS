import codecs

with codecs.open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Clean up any broken syntax from previous errors
code = code.replace('initial_sidebar_state="expanded")\\n\\n\\n\\n', 'initial_sidebar_state="expanded")')
code = code.replace('initial_sidebar_state="expanded")\n\n\n\n', 'initial_sidebar_state="expanded")')

# 1. Top Part
top_end = code.find('initial_sidebar_state="expanded")') + len('initial_sidebar_state="expanded")')
top_part = code[:top_end]

# 2. About Page (current) - Find it and rip it out
about_start = code.find('# ══════════════════════════════════════════════════════════════════════════════\n#  ABOUT PROJECT PAGE (ROUTING)')
about_end = code.find('st.stop()', about_start)
if about_end != -1:
    about_end += len('st.stop()')

# 3. Global Theme
theme_start = code.find('# ══════════════════════════════════════════════════════════════════════════════\n#  GLOBAL THEME')
theme_end = code.find('""", unsafe_allow_html=True)', theme_start)
if theme_end != -1:
    theme_end += len('""", unsafe_allow_html=True)')

# 4. Rest
rest_start = code.find('NEXUS_LAYOUT = dict(')

theme_part = code[theme_start:theme_end]
rest_part = code[rest_start:]

# New About Page using rich containers
ICON_SWORDS = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="14.5 17.5 3 6 3 3 6 3 17.5 14.5"></polyline><line x1="13" y1="19" x2="19" y2="13"></line><line x1="16" y1="16" x2="20" y2="20"></line><line x1="19" y1="21" x2="21" y2="19"></line><polyline points="14.5 6.5 18 3 21 3 21 6 17.5 9.5"></polyline><line x1="5" y1="14" x2="9" y2="18"></line><line x1="7" y1="17" x2="4" y2="20"></line><line x1="3" y1="19" x2="5" y2="21"></line></svg>'
ICON_SHIELD = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
ICON_BRAIN = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"></path></svg>'

new_about_part = f'''
# ══════════════════════════════════════════════════════════════════════════════
#  ABOUT PROJECT PAGE (ROUTING)
# ══════════════════════════════════════════════════════════════════════════════
if st.query_params.get("page") == "about":
    st.markdown("<div style='margin-bottom:24px;'>", unsafe_allow_html=True)
    if st.button("← Back to Command Center"):
        st.query_params.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='font-family:\\"Google Sans\\", sans-serif; font-size:3rem; font-weight:800; color:#0f172a; margin-bottom:16px;'>About NEXUS</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.15rem; color:#475569; line-height:1.8; margin-bottom:40px;'><b>Neural Exploitation & eXplainable Unified Security (NEXUS)</b> is an autonomous, self-evolving cyber warfare simulation platform. It acts as an intelligent proving ground where autonomous Red Team agents and Blue Team defense networks wage continuous, self-improving campaigns against each other.</p>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='font-family:\\"Google Sans\\", sans-serif; font-weight:800; color:#0f172a; margin-bottom:24px;'>System Architecture</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown(f"<div style='display:flex; align-items:center; gap:12px; margin-bottom:12px;'><div style='color:#ef4444;'>{{'{ICON_SWORDS}'}}</div><div style='font-family:\\"Google Sans\\", sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a;'>Red Team (Autonomous Attackers)</div></div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#475569; line-height:1.6;'>Powered by intelligent agents, the Red Team dynamically scans the network, selects targets, and launches exploits based on real-time threat intelligence (TAXII/STIX). They possess a <b>Semantic Vector Memory</b> that allows them to remember which attacks worked and adapt to the Blue Team's defenses.</p>", unsafe_allow_html=True)
        
    with st.container(border=True):
        st.markdown(f"<div style='display:flex; align-items:center; gap:12px; margin-bottom:12px;'><div style='color:#10b981;'>{{'{ICON_SHIELD}'}}</div><div style='font-family:\\"Google Sans\\", sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a;'>Blue Team (SIEM & Defense)</div></div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#475569; line-height:1.6;'>The Blue Team monitors a simulated network (represented by the Live Threat Graph) and generates alerts based on SIEM rules. When attacks are detected, they block the originating IPs and patch vulnerabilities, forcing the Red Team to evolve their tactics.</p>", unsafe_allow_html=True)
        
    with st.container(border=True):
        st.markdown(f"<div style='display:flex; align-items:center; gap:12px; margin-bottom:12px;'><div style='color:#8b5cf6;'>{{'{ICON_BRAIN}'}}</div><div style='font-family:\\"Google Sans\\", sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a;'>The AI Brain (Provider)</div></div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#475569; line-height:1.6;'>The core reasoning engine of NEXUS can be toggled between an offline <b>Mock Engine</b> (for high-speed, deterministic simulations) or a live <b>Ollama Model</b> (for true, localized AI reasoning and decision making).</p>", unsafe_allow_html=True)
        
    st.stop()
'''

final_code = top_part + '\n\n' + theme_part + '\n\n' + new_about_part + '\n\n' + rest_part

with codecs.open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(final_code)

