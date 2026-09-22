import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

start_idx = text.find('with tab2:')
end_idx = text.find('if __name__ == "__main__":')

if start_idx != -1 and end_idx != -1:
    new_tab2 = """with tab2:
    st.markdown("<div class='hero-header' style='font-size: 2.8rem; letter-spacing: -1px; margin-top: 16px;'>Analytics & Export</div>", unsafe_allow_html=True)
    st.markdown("<p style=\\"font-family:'Space Grotesk', sans-serif; color:#64748b; margin-bottom:32px; font-size:1.1rem; font-weight:500;\\">Generate reports and export raw telemetry data.</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown(\"\"\"
        <div style="background:#0f172a; border:1px solid #1e293b; border-left:3px solid #00d2ff; padding:20px; border-radius:6px; margin-bottom:16px;">
            <div style="font-family:'Space Grotesk', sans-serif; font-size:0.75rem; font-weight:700; color:#00d2ff; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:12px;">Data Export</div>
            <div style="font-family:'Space Grotesk', sans-serif; font-size:1.4rem; font-weight:700; color:#e2e8f0; margin-bottom:8px;">Executive Reporting</div>
            <p style="font-family:'Space Grotesk', sans-serif; color:#94a3b8; font-size:0.95rem; line-height:1.6; margin-bottom:0;">High-level summary of the simulation, agent performance, risk exposure, and MITRE ATT&CK coverage.</p>
        </div>
        \"\"\", unsafe_allow_html=True)
        
        pdfs = list(Path("data/research").glob("paper_*.pdf"))
        if pdfs:
            latest_pdf = sorted(pdfs, key=lambda x: x.stat().st_mtime)[-1]
            st.download_button(" DOWNLOAD REPORT (PDF)", data=latest_pdf.read_bytes(), file_name="NEXUS_Executive_Report.pdf", mime="application/pdf", use_container_width=True, type="primary")
        else:
            st.button(" NO REPORTS AVAILABLE", disabled=True, use_container_width=True, type="primary")

    with c2:
        st.markdown(\"\"\"
        <div style="background:#0f172a; border:1px solid #1e293b; border-left:3px solid #f59e0b; padding:20px; border-radius:6px; margin-bottom:16px;">
            <div style="font-family:'Space Grotesk', sans-serif; font-size:0.75rem; font-weight:700; color:#f59e0b; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:12px;">Raw Telemetry</div>
            <div style="font-family:'Space Grotesk', sans-serif; font-size:1.4rem; font-weight:700; color:#e2e8f0; margin-bottom:8px;">SIEM Logs</div>
            <p style="font-family:'Space Grotesk', sans-serif; color:#94a3b8; font-size:0.95rem; line-height:1.6; margin-bottom:0;">Download raw NDJSON SIEM logs for direct ingestion into Splunk, Elastic, or Microsoft Sentinel.</p>
        </div>
        \"\"\", unsafe_allow_html=True)
        
        p = Path("data/siem/nexus_events.ndjson")
        if p.exists() and p.stat().st_size > 0: 
            st.download_button(" DOWNLOAD LOGS (NDJSON)", data=p.read_bytes(), file_name=p.name, mime="application/x-ndjson", use_container_width=True)
        else: 
            st.button(" NO LOGS AVAILABLE", disabled=True, use_container_width=True)
\n"""
    
    text = text[:start_idx] + new_tab2 + text[end_idx:]
    
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(text)
