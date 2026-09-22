import codecs
import os
import glob
import json

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Add the "TEST RESULTS" button in between START CAMPAIGN and ANALYTICS
old_buttons = """            st.markdown("<br>", unsafe_allow_html=True)
            if st.session_state.current_page == 'home':
                if st.button("ANALYTICS & EXPORTS", use_container_width=True):
                    st.session_state.current_page = 'analytics'
                    st.rerun()
            else:
                if st.button("BACK TO SOC", use_container_width=True):"""

new_buttons = """            st.markdown("<br>", unsafe_allow_html=True)
            if st.session_state.current_page == 'home':
                if st.button("TEST RESULTS", use_container_width=True):
                    st.session_state.current_page = 'results'
                    st.rerun()
                if st.button("ANALYTICS & EXPORTS", use_container_width=True):
                    st.session_state.current_page = 'analytics'
                    st.rerun()
            else:
                if st.button("BACK TO SOC", use_container_width=True):"""

text = text.replace(old_buttons, new_buttons)

# 2. Add the UI logic for the 'results' page!
results_page_code = """
if st.session_state.current_page == 'results':
    st.markdown("<div class='hero-header' style='font-size: 2.8rem; letter-spacing: -1px; margin-top: 16px;'>Operation After-Action Report</div>", unsafe_allow_html=True)
    st.markdown("<p style=\"font-family:'Space Grotesk', sans-serif; color:#64748b; margin-bottom:32px; font-size:1.1rem; font-weight:500;\">Detailed breakdown of the most recent campaign, including executed attacks, blue team mitigations, and dynamic rule generation.</p>", unsafe_allow_html=True)
    
    # Load the most recent report
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "data", "reports")
    report_files = sorted(glob.glob(os.path.join(reports_dir, "*.json")), key=os.path.getmtime, reverse=True)
    
    if not report_files:
        st.warning("No campaign reports found. Run a simulation first.")
    else:
        latest_report = report_files[0]
        try:
            with open(latest_report, "r") as f:
                report_data = json.load(f)
            
            c1, c2 = st.columns([1, 1.5])
            
            with c1:
                with st.container(border=True):
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Campaign overview</h3>", unsafe_allow_html=True)
                    st.write(f"**Battle ID:** `{report_data.get('battle_id', 'N/A')}`")
                    st.write(f"**Timestamp:** `{report_data.get('timestamp', 'N/A')}`")
                    winner = report_data.get('winner', 'unknown').upper()
                    win_color = "#10b981" if winner == "DEFENDER" else "#ef4444"
                    st.markdown(f"**Outcome:** <span style='color:{win_color}; font-weight:800;'>{winner} VICTORY</span>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Blue Team Mitigations</h3>", unsafe_allow_html=True)
                    stats = report_data.get('stats', {})
                    st.write(f"**SIGMA Rules Deployed:** `{stats.get('total_sigma_rules', 0)}` dynamic rules written")
                    st.write(f"**Final Accuracy:** `{(stats.get('accuracy', 0)*100):.1f}%`")
                    st.write(f"**Precision:** `{(stats.get('precision', 0)*100):.1f}%`")
                    st.write(f"**Recall:** `{(stats.get('recall', 0)*100):.1f}%`")
                    
                    st.markdown("<p style='color:#64748b; font-size:0.9rem; margin-top:16px;'>The autonomous Blue Team agent successfully analyzed the network traffic in real-time, identifying malicious signatures and deploying new SIGMA rules to block the execution pathways.</p>", unsafe_allow_html=True)

            with c2:
                with st.container(border=True):
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Executed Attack Vectors</h3>", unsafe_allow_html=True)
                    logs = report_data.get('attacker_logs', [])
                    if not logs:
                        st.info("No attacks executed during this campaign.")
                    else:
                        for idx, log in enumerate(logs):
                            attacker = log.get('attacker', 'Unknown')
                            tech = log.get('attack_technique', 'N/A')
                            target = log.get('host', 'N/A')
                            detected = log.get('detected', False)
                            status = "<span style='color:#10b981; font-weight:700;'>BLOCKED</span>" if detected else "<span style='color:#ef4444; font-weight:700;'>BYPASSED</span>"
                            
                            st.markdown(f\"\"\"
                            <div style='background:#f8fafc; border:1px solid #e2e8f0; padding:12px 16px; border-radius:8px; margin-bottom:8px;'>
                                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>
                                    <strong style='color:#0f172a;'>{attacker} executed {tech}</strong>
                                    <div>{status}</div>
                                </div>
                                <div style='font-family:monospace; color:#64748b; font-size:0.85rem;'>Target: {target} | Src: {log.get('ip_src')} → Dst: {log.get('ip_dst')}</div>
                            </div>
                            \"\"\", unsafe_allow_html=True)
                            if idx >= 9:
                                st.markdown("*... showing first 10 attacks*")
                                break
                                
        except Exception as e:
            st.error(f"Error parsing report: {e}")

"""

# Insert the results page before the analytics page logic
text = text.replace("if st.session_state.current_page == 'analytics':", results_page_code + "\n\nif st.session_state.current_page == 'analytics':")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
