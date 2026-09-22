import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Find the start of the layout
start_idx = text.find('r1c1, r1c2 = st.columns([4, 6])')

# Find where the next section starts (Tactics & Perimeter Defense)
end_idx = text.find('# ── MITRE Heatmap & Firewall Feed ──')

# We'll replace everything between start_idx and end_idx with just a full-width Threat Graph
if start_idx != -1 and end_idx != -1:
    old_block = text[start_idx:end_idx]
    
    new_block = """with st.container(border=True):
        st.markdown("<h3 style='color:#0f172a; font-family:\\'Space Grotesk\\', sans-serif; margin-bottom:16px; font-weight:700;'>Live Threat Graph</h3>", unsafe_allow_html=True)
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from integrations.network_graph import build_graph_from_siem_logs
            fig2 = build_graph_from_siem_logs()
            fig2.update_layout(NEXUS_LAYOUT)
            fig2.update_layout(height=450)
            st.plotly_chart(fig2, use_container_width=True, theme=None)
        except Exception as e:
            st.warning(f"Graph engine error: {e}")
            
    """
    
    text = text.replace(old_block, new_block)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
