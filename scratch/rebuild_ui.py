import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

import re

# 1. Remove the Tabs setup
text = text.replace('tab1, tab2 = st.tabs(["SOC Overview", "Analytics & Export"])', '# NO TABS')
text = text.replace('with tab1:', 'if True:')

# 2. Modify op_c1 (Remove sliders, add export buttons under Start/Halt buttons)
old_op_c1 = r"""            st.markdown("---")
            hosts = st.slider("Target Hosts", 2, 20, 8)
            users = st.slider("Simulated Users", 5, 50, 24)
            if st.session_state.running:
                if st.button("HALT CAMPAIGN", use_container_width=True):
                    st.session_state.running = False
                    st.session_state.live_feed.append("=== SIMULATION ABORTED BY USER ===")
                    st.rerun()
            else:
                if st.button("START CAMPAIGN", use_container_width=True):"""

new_op_c1 = r"""            hosts = 8
            users = 24
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.session_state.running:
                if st.button("HALT CAMPAIGN", use_container_width=True):
                    st.session_state.running = False
                    st.session_state.live_feed.append("=== SIMULATION ABORTED BY USER ===")
                    st.rerun()
            else:
                if st.button("START CAMPAIGN", use_container_width=True):"""

text = text.replace(old_op_c1, new_op_c1)

# Now find where the progress bar and terminal end, so we can inject the export buttons
# Wait, the buttons are in op_c1.
# Let's find the end of `with op_c1:`
# The block ends around the `st.progress` / `st.rerun()` stuff.

# Let's just find `st.progress(100, text="✅ Simulation Complete")` and inject the export buttons right after it!
# Wait, `st.progress(100)` is in `with op_c1:`? Yes!

old_progress = r"""            if st.session_state.live_feed:
                st.progress(100, text="✅ Simulation Complete")"""

new_progress = r"""            if st.session_state.live_feed:
                st.progress(100, text="✅ Simulation Complete")
                
            # INJECTED EXPORT BUTTONS
            st.markdown("<hr style='margin-top: 20px; margin-bottom: 20px;'/>", unsafe_allow_html=True)
            st.markdown("<div style='font-family:\"Space Grotesk\", sans-serif; font-size:1.1rem; font-weight:800; color:#0f172a; margin-bottom: 12px;'>Data Export</div>", unsafe_allow_html=True)
            
            pdfs = list(Path("data/research").glob("paper_*.pdf"))
            if pdfs:
                latest_pdf = sorted(pdfs, key=lambda x: x.stat().st_mtime)[-1]
                st.download_button(" DOWNLOAD REPORT (PDF)", data=latest_pdf.read_bytes(), file_name=f"NEXUS_Executive_Report.pdf", mime="application/pdf", use_container_width=True, type="primary")
            else:
                st.button(" NO REPORTS AVAILABLE", disabled=True, use_container_width=True, type="primary")
                
            p = Path("data/siem/nexus_events.ndjson")
            if p.exists(): 
                st.download_button(" DOWNLOAD SIEM LOGS", data=p.read_bytes(), file_name=p.name, mime="application/x-ndjson", use_container_width=True)
            else: 
                st.button(" NO LOGS AVAILABLE", disabled=True, use_container_width=True)"""

text = text.replace(old_progress, new_progress)

# 3. Completely delete the `with tab2:` section
tab2_start = text.find('with tab2:')
if tab2_start != -1:
    text = text[:tab2_start]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
