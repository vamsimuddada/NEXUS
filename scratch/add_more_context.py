import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

more_context = """
    st.markdown("<h3 style='font-family:\\'Space Grotesk\\', sans-serif; font-weight:800; color:#0f172a; margin-top:32px; margin-bottom:24px;'>Simulation Lifecycle</h3>", unsafe_allow_html=True)
    
    st.markdown(\"""
    <div style='background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>
        <ol style='color:#475569; line-height:1.8; font-size:1.05rem; margin-bottom:0;'>
            <li><b>Initialization:</b> The platform spawns a digital twin network topology (subnets, firewalls, and critical databases).</li>
            <li><b>Threat Ingestion:</b> Live STIX/TAXII threat feeds are pulled in to inform the Red Team's attack patterns, ensuring simulations model real-world APTs (Advanced Persistent Threats).</li>
            <li><b>Execution Phase:</b> The Red Team LLM analyzes the network graph and launches calculated SQL injections, phishing campaigns, or buffer overflows.</li>
            <li><b>Detection & Response:</b> The Blue Team SIEM engine parses system logs. If an attack is caught, the Blue Team dynamically alters firewall rules to isolate the compromised nodes.</li>
            <li><b>Evolution:</b> Both agents learn from the encounter and store the interaction in their vector memory, making subsequent rounds significantly harder.</li>
        </ol>
    </div>
    \""", unsafe_allow_html=True)
"""

text = text.replace('st.stop()', more_context + '\n    st.stop()')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
