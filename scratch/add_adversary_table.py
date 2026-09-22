import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

old_block = """                    st.markdown("<p style='color:#64748b; font-size:0.9rem; margin-top:16px;'>The autonomous Blue Team agent successfully analyzed the network traffic in real-time, identifying malicious signatures and deploying new SIGMA rules to block the execution pathways.</p>", unsafe_allow_html=True)

            with c2:"""

new_block = """                    st.markdown("<p style='color:#64748b; font-size:0.9rem; margin-top:16px;'>The autonomous Blue Team agent successfully analyzed the network traffic in real-time, identifying malicious signatures and deploying new SIGMA rules to block the execution pathways.</p>", unsafe_allow_html=True)

                with st.container(border=True):
                    st.markdown("<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:8px; font-weight:800;'>Adversary Intelligence</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='color:#64748b; font-size:0.9rem; margin-bottom:16px;'>Profiles of Red Team AI agents observed during this campaign.</p>", unsafe_allow_html=True)
                    
                    agents = report_data.get('metrics', {}).get('gnn_stats', {}).get('memory', {}).get('agents', [])
                    if not agents:
                        st.info("No adversary intelligence available.")
                    else:
                        table_html = "<table style='width:100%; border-collapse:collapse; font-size:0.85rem; margin-bottom:8px;'>"
                        table_html += "<tr><th style='text-align:left; border-bottom:2px solid #e2e8f0; padding-bottom:8px; color:#64748b; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.5px;'>Threat Actor</th><th style='text-align:left; border-bottom:2px solid #e2e8f0; padding-bottom:8px; color:#64748b; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.5px;'>Top TTP</th><th style='text-align:right; border-bottom:2px solid #e2e8f0; padding-bottom:8px; color:#64748b; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.5px;'>Avg Stealth</th></tr>"
                        for idx, agent in enumerate(agents[:6]): # Limit to top 6 to fit beautifully in the empty space
                            bg_color = "#f8fafc" if idx % 2 == 0 else "#ffffff"
                            table_html += f"<tr style='background-color:{bg_color};'><td style='padding:10px 8px; border-bottom:1px solid #f1f5f9; font-weight:700; color:#0f172a;'>{agent.get('name')}</td><td style='padding:10px 8px; border-bottom:1px solid #f1f5f9; font-family:monospace; color:#ef4444; font-weight:600;'>{agent.get('top_technique')}</td><td style='padding:10px 8px; border-bottom:1px solid #f1f5f9; text-align:right; font-weight:700; color:#3b82f6;'>{agent.get('avg_stealth')}</td></tr>"
                        table_html += "</table>"
                        st.markdown(table_html, unsafe_allow_html=True)

            with c2:"""

text = text.replace(old_block, new_block)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
