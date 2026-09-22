import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Add session state for routing at the top
old_init = r"""if "running" not in st.session_state: st.session_state.running = False
if "msg_queue" not in st.session_state: st.session_state.msg_queue = queue.Queue()
if "live_feed" not in st.session_state: st.session_state.live_feed = []"""

new_init = r"""if "current_page" not in st.session_state: st.session_state.current_page = 'home'
if "running" not in st.session_state: st.session_state.running = False
if "msg_queue" not in st.session_state: st.session_state.msg_queue = queue.Queue()
if "live_feed" not in st.session_state: st.session_state.live_feed = []"""

text = text.replace(old_init, new_init)

# 2. Wrap the home page in `if st.session_state.current_page == 'home':`
# Wait, I previously changed `with tab1:` to `if True:`.
text = text.replace('if True:', "if st.session_state.current_page == 'home':")

# 3. Replace the injected export buttons with a Navigation Button
old_exports = r"""            # INJECTED EXPORT BUTTONS
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

new_exports = r"""            st.markdown("<hr style='margin-top: 20px; margin-bottom: 20px;'/>", unsafe_allow_html=True)
            if st.button("📊 ANALYTICS & EXPORTS", use_container_width=True):
                st.session_state.current_page = 'analytics'
                st.rerun()"""

text = text.replace(old_exports, new_exports)

# 4. Append the Analytics Page at the end of the file
analytics_page = r"""
elif st.session_state.current_page == 'analytics':
    st.markdown("<div class='hero-header' style='font-size: 2.8rem; letter-spacing: -1px; margin-top: 16px;'>Analytics & Export</div>", unsafe_allow_html=True)
    st.markdown("<p style=\"font-family:'Space Grotesk', sans-serif; color:#64748b; margin-bottom:32px; font-size:1.1rem; font-weight:500;\">Generate reports and export raw telemetry data.</p>", unsafe_allow_html=True)
    
    if st.button("⬅ BACK TO COMMAND CENTER", use_container_width=False):
        st.session_state.current_page = 'home'
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    
    with c1:
        with st.container(border=True):
            st.markdown('''
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                <div style="background:rgba(99,102,241,0.1); color:#6366f1; padding:8px; border-radius:8px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                </div>
                <div style="font-family:'Space Grotesk', sans-serif; font-size:1.4rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px;">Executive Reporting</div>
            </div>
            <p style="font-family:'Space Grotesk', sans-serif; color:#64748b; font-size:0.95rem; line-height:1.6; margin-bottom:20px; min-height: 75px;">Generate a high-level summary of the simulation, including overall agent performance, risk exposure, and MITRE ATT&CK coverage.</p>
            ''', unsafe_allow_html=True)
            
            pdfs = list(Path("data/research").glob("paper_*.pdf"))
            if pdfs:
                latest_pdf = sorted(pdfs, key=lambda x: x.stat().st_mtime)[-1]
                st.download_button(" DOWNLOAD LATEST REPORT (PDF)", data=latest_pdf.read_bytes(), file_name=f"NEXUS_Executive_Report.pdf", mime="application/pdf", use_container_width=True, type="primary")
            else:
                st.button(" NO REPORTS AVAILABLE", disabled=True, use_container_width=True, type="primary")

    with c2:
        with st.container(border=True):
            st.markdown('''
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                <div style="background:rgba(16,185,129,0.1); color:#10b981; padding:8px; border-radius:8px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                </div>
                <div style="font-family:'Space Grotesk', sans-serif; font-size:1.4rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px;">SIEM Telemetry</div>
            </div>
            <p style="font-family:'Space Grotesk', sans-serif; color:#64748b; font-size:0.95rem; line-height:1.6; margin-bottom:20px; min-height: 75px;">Download the raw SIEM logs from the simulation for ingestion into Splunk, Elastic, or Microsoft Sentinel.</p>
            ''', unsafe_allow_html=True)
            p = Path("data/siem/nexus_events.ndjson")
            if p.exists(): 
                st.download_button(" DOWNLOAD LOGS (NDJSON)", data=p.read_bytes(), file_name=p.name, mime="application/x-ndjson", use_container_width=True)
            else: 
                st.button(" NO LOGS AVAILABLE", disabled=True, use_container_width=True)
"""

text = text + analytics_page

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
