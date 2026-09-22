with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    code = f.read()

about_code = '''
if st.query_params.get("page") == "about":
    st.markdown("""
    <style>
    .about-container { max-width: 900px; margin: 0 auto; padding: 40px; background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 24px; box-shadow: 0 20px 40px rgba(15,23,42,0.05); border: 1px solid rgba(226,232,240,0.8); }
    .about-title { font-family: 'Google Sans', sans-serif; font-size: 3rem; font-weight: 800; color: #0f172a; letter-spacing: -1px; margin-bottom: 20px; }
    .about-text { font-size: 1.15rem; color: #475569; line-height: 1.8; margin-bottom: 24px; }
    .arch-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px; margin-bottom: 20px; }
    .arch-title { color: #2563eb; font-weight: 800; font-size: 1.2rem; display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("? Back to Command Center"):
        st.query_params.clear()
        st.rerun()
        
    st.markdown("""
    <div class="about-container">
        <div class="about-title">About NEXUS</div>
        <p class="about-text">
            <b>Neural Exploitation & eXplainable Unified Security (NEXUS)</b> is an autonomous, self-evolving cyber warfare simulation platform. It is designed to act as an intelligent proving ground where autonomous Red Team agents and Blue Team defense networks wage continuous, self-improving campaigns against each other.
        </p>
        
        <h3 style="color:#0f172a; margin-top:40px; margin-bottom:20px; font-weight:800;">System Architecture</h3>
        
        <div class="arch-box">
            <div class="arch-title">?? Red Team (Autonomous Attackers)</div>
            <p style="margin:0; color:#475569; font-size:1rem; line-height:1.6;">Powered by intelligent agents, the Red Team dynamically scans the network, selects targets, and launches exploits based on real-time threat intelligence (TAXII/STIX). They possess a <b>Semantic Vector Memory</b> that allows them to remember which attacks worked and adapt to the Blue Team's defenses.</p>
        </div>
        
        <div class="arch-box">
            <div class="arch-title">??? Blue Team (SIEM & Defense)</div>
            <p style="margin:0; color:#475569; font-size:1rem; line-height:1.6;">The Blue Team monitors a simulated network (represented by the Live Threat Graph) and generates alerts based on SIEM rules. When attacks are detected, they block the originating IPs and patch vulnerabilities, forcing the Red Team to evolve their tactics.</p>
        </div>
        
        <div class="arch-box">
            <div class="arch-title">?? The AI Brain (Provider)</div>
            <p style="margin:0; color:#475569; font-size:1rem; line-height:1.6;">The core reasoning engine of NEXUS can be toggled between an offline <b>Mock Engine</b> (for high-speed, deterministic simulations) or a live <b>Ollama Model</b> (for true, localized AI reasoning and decision making).</p>
        </div>
        
    </div>
    """, unsafe_allow_html=True)
    st.stop()
'''

# We also need to clear out the one at the end of the file if it exists!
end_block_idx = code.find('if st.query_params.get("page") == "about":')
if end_block_idx != -1:
    code = code[:end_block_idx]

target = 'initial_sidebar_state="expanded")'
code = code.replace(target, target + '\n' + about_code)

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Injected safely.")
