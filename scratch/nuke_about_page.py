import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

idx_start = text.find('if st.query_params.get("page") == "about":')
idx_stop = text.find('st.stop()', idx_start)

perfect_about_page = """if st.query_params.get("page") == "about":
    st.markdown("<div style='margin-bottom:24px;'>", unsafe_allow_html=True)
    if st.button(" Back to Command Center"):
        st.query_params.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style=\\"font-family:'Inter', sans-serif; font-size:3.5rem; font-weight:900; color:#0f172a; letter-spacing:-2px; margin-bottom:16px;\\">PROJECT NEXUS MANIFESTO</div>", unsafe_allow_html=True)
    
    st.markdown(\"\"\"
    <div style="background: linear-gradient(135deg, rgba(37,99,235,0.05), rgba(139,92,246,0.05)); border: 1px solid rgba(37,99,235,0.1); border-radius: 16px; padding: 24px; margin-bottom: 40px;">
        <p style="font-family:'Inter', sans-serif; font-size:1.15rem; color:#334155; line-height:1.8; margin-bottom:16px;">
            <b>Neural Exploitation & eXplainable Unified Security (NEXUS)</b> is an autonomous, self-evolving cyber warfare simulation platform. It acts as an intelligent proving ground where autonomous Red Team agents and Blue Team defense networks wage continuous, self-improving campaigns against each other.
        </p>
        <p style="font-family:'Inter', sans-serif; font-size:1.05rem; color:#475569; line-height:1.7; margin-bottom:0;">
            <b>Context & Motivation:</b> Modern cybersecurity is a rapidly evolving arms race. Traditional static defenses and manual penetration testing can no longer keep up with AI-assisted threats. NEXUS was designed to research and simulate what happens when both attackers and defenders are powered by Large Language Models (LLMs). By allowing these models to battle in an isolated sandbox, security researchers can study emergent attack vectors, improve automated SIEM (Security Information and Event Management) detection logic, and build stronger, self-patching networks.
        </p>
    </div>
    \"\"\", unsafe_allow_html=True)
    
    st.markdown("<h3 style=\\"font-family:'Inter', sans-serif; font-weight:800; color:#0f172a; letter-spacing:-1px; margin-bottom:24px;\\">System Architecture</h3>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown(f"<div style=\\"display:flex; align-items:center; gap:12px; margin-bottom:12px;\\"><div style=\\"color:#ef4444;\\">{ICON_SWORDS}</div><div style=\\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px;\\">Red Team (Autonomous Attackers)</div></div>", unsafe_allow_html=True)
            st.markdown("<p style=\\"font-family:'Inter', sans-serif; color:#475569; line-height:1.6;\\">Powered by intelligent agents, the Red Team dynamically scans the network, selects targets, and launches exploits based on real-time threat intelligence (TAXII/STIX). They possess a <b>Semantic Vector Memory</b> that allows them to remember which attacks worked and adapt to the Blue Team's defenses.</p>", unsafe_allow_html=True)
    with c2:        
        with st.container(border=True):
            st.markdown(f"<div style=\\"display:flex; align-items:center; gap:12px; margin-bottom:12px;\\"><div style=\\"color:#10b981;\\">{ICON_SHIELD}</div><div style=\\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px;\\">Blue Team (SIEM & Defense)</div></div>", unsafe_allow_html=True)
            st.markdown("<p style=\\"font-family:'Inter', sans-serif; color:#475569; line-height:1.6;\\">The Blue Team monitors a simulated network (represented by the Live Threat Graph) and generates alerts based on SIEM rules. When attacks are detected, they block the originating IPs and patch vulnerabilities, forcing the Red Team to evolve their tactics.</p>", unsafe_allow_html=True)
            
    with st.container(border=True):
        st.markdown(f"<div style=\\"display:flex; align-items:center; gap:12px; margin-bottom:12px;\\"><div style=\\"color:#8b5cf6;\\">{ICON_BRAIN}</div><div style=\\"font-family:'Inter', sans-serif; font-size:1.3rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px;\\">The AI Brain & Technology Stack</div></div>", unsafe_allow_html=True)
        st.markdown(\"\"\"
        <div style="font-family:'Inter', sans-serif; color:#475569; line-height:1.6;">
        The core reasoning engine of NEXUS can be toggled between an offline <b>Mock Engine</b> (for high-speed, deterministic simulations) or a live <b>Ollama Model</b> (for true, localized AI reasoning and decision making).
        <br><br>
        <b>Built With:</b>
        <ul style="font-family:'Inter', sans-serif; color:#475569; line-height:1.6; margin-top:8px;">
            <li><b>Frontend:</b> Streamlit, Plotly, HTML/CSS Glassmorphism</li>
            <li><b>Backend Engine:</b> Pure Python, SQLite (for tracking campaign telemetry)</li>
            <li><b>Vector Storage:</b> Custom TF-IDF Semantic Memory (No external dependencies)</li>
            <li><b>AI Integration:</b> Local Ollama LLaMA models</li>
        </ul>
        </div>
        \"\"\", unsafe_allow_html=True)
        
    
    st.markdown("<h3 style=\\"font-family:'Inter', sans-serif; font-weight:800; color:#0f172a; letter-spacing:-1px; margin-top:32px; margin-bottom:24px;\\">Simulation Lifecycle</h3>", unsafe_allow_html=True)
    
    st.markdown(\"\"\"
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <ol style="font-family:'Inter', sans-serif; color:#475569; line-height:1.8; font-size:1.05rem; margin-bottom:0;">
            <li><b>Initialization:</b> The platform spawns a digital twin network topology (subnets, firewalls, and critical databases).</li>
            <li><b>Threat Ingestion:</b> Live STIX/TAXII threat feeds are pulled in to inform the Red Team's attack patterns, ensuring simulations model real-world APTs (Advanced Persistent Threats).</li>
            <li><b>Execution Phase:</b> The Red Team LLM analyzes the network graph and launches calculated SQL injections, phishing campaigns, or buffer overflows.</li>
            <li><b>Detection & Response:</b> The Blue Team SIEM engine parses system logs. If an attack is caught, the Blue Team dynamically alters firewall rules to isolate the compromised nodes.</li>
            <li><b>Evolution:</b> Both agents learn from the encounter and store the interaction in their vector memory, making subsequent rounds significantly harder.</li>
        </ol>
    </div>
    \"\"\", unsafe_allow_html=True)
"""

text = text[:idx_start] + perfect_about_page + '\n    ' + text[idx_stop:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
