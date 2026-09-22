import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

idx_tab2 = text.find('with tab2:')
if idx_tab2 != -1:
    text = text[:idx_tab2]

new_tabs = """with tab2:
    st.markdown("<h2 style='color:#0f172a; font-family: \"Space Grotesk\", sans-serif; font-weight:800; letter-spacing:-1px; margin-bottom:24px;'>Threat Intelligence (TAXII)</h2>", unsafe_allow_html=True)
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from integrations.taxii_client import get_taxii
        client = get_taxii(use_live=False)
        groups = client.get_all_apt_groups()

        r1, r2 = st.columns([1, 2])
        with r1:
            with st.container(border=True):
                st.markdown("<h4 style='color:#0f172a; margin-top:0;'>Tracked Actors</h4>", unsafe_allow_html=True)
                selected_apt = st.radio("Select Profile", groups, label_visibility="collapsed")
            
        with r2:
            profile = client.get_apt_profile(selected_apt)
            with st.container(border=True):
                st.markdown(f"<h3 style='color:#ef4444; font-family: \"Space Grotesk\", sans-serif; margin-top:0;'>{selected_apt}</h3>", unsafe_allow_html=True)
                c_a, c_b, c_c = st.columns(3)
                c_a.metric("Origin", profile.get('origin', 'Unknown'))
                c_b.metric("Motivation", profile.get('motivation', 'Unknown'))
                c_c.metric("Primary Target", profile.get('targets', ['Unknown'])[0])
                st.markdown("---")
                st.markdown("**Known Signatures & Malware:**")
                for mw in profile.get('tools', []): 
                    st.markdown(f"<span style='background:rgba(239, 68, 68, 0.1); color:#ef4444; padding:4px 8px; border-radius:4px; font-family:monospace; margin-right:8px; font-size:0.85rem;'>{mw}</span>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to load Threat Intel: {e}")

with tab3:
    st.markdown("<h2 style='color:#0f172a; font-family: \"Space Grotesk\", sans-serif; font-weight:800; letter-spacing:-1px; margin-bottom:24px;'>Analytics & Export</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        with st.container(border=True):
            st.markdown("<h4 style='color:#0f172a; font-family: \"Space Grotesk\", sans-serif; margin-top:0;'>Executive Reporting</h4>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:0.9rem;'>Generate a high-level summary of the simulation, including overall agent performance, risk exposure, and MITRE ATT&CK coverage.</p>", unsafe_allow_html=True)
            st.button("📄 Generate Executive Report (PDF)", use_container_width=True, type="primary")

    with c2:
        with st.container(border=True):
            st.markdown("<h4 style='color:#0f172a; font-family: \"Space Grotesk\", sans-serif; margin-top:0;'>SIEM Telemetry</h4>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b; font-size:0.9rem;'>Download the raw SIEM logs from the simulation for ingestion into Splunk, Elastic, or Microsoft Sentinel.</p>", unsafe_allow_html=True)
            p = Path("data/siem/nexus_events.ndjson")
            if p.exists(): 
                st.download_button("💾 Download Logs (NDJSON)", data=p.read_bytes(), file_name=p.name, mime="application/x-ndjson", use_container_width=True)
            else: 
                st.button("💾 No Logs Available", disabled=True, use_container_width=True)
"""

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text + new_tabs)
