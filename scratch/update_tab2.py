import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# We need to extract everything from "with tab2:" to "with tab3:" and replace it.
pattern = re.compile(r'with tab2:.*?with tab3:', re.DOTALL)

new_tab2 = """with tab2:
    st.markdown("<div class='hero-header' style='font-size: 2.8rem; letter-spacing: -1px; margin-top: 16px;'>Threat Intelligence (TAXII)</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-family:\\'Inter\\', sans-serif; color:#64748b; margin-bottom:32px; font-size:1.1rem; font-weight:500;'>Live adversarial profiles and APT tracking database.</p>", unsafe_allow_html=True)
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from integrations.taxii_client import get_taxii
        client = get_taxii(use_live=True)
        groups = client.get_all_apt_groups()

        r1, r2 = st.columns([1, 2.5])
        with r1:
            st.markdown("<h4 style='font-family:\\'Inter\\', sans-serif; font-weight:800; color:#0B1121; margin-top:0; margin-bottom:16px; letter-spacing:-0.5px;'>Tracked Actors</h4>", unsafe_allow_html=True)
            selected_apt = st.radio("Select Profile", groups, label_visibility="collapsed")
            
        with r2:
            profile = client.get_apt_profile(selected_apt)
            targets = profile.get('targets', ['Unknown'])
            target_str = targets[0] if isinstance(targets, list) else targets
            
            tools_html = "".join([f"<span style='background:#f8fafc; color:#334155; padding:8px 16px; border-radius:8px; font-family:\\'JetBrains Mono\\', monospace; font-size:0.9rem; font-weight:600; border:1px solid #e2e8f0;'>{mw}</span>" for mw in profile.get('tools', [])])
            
            st.markdown(f\"\"\"
            <div style='background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.03);'>
                <div style='display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 20px; margin-bottom: 24px;'>
                    <div style='font-family:\\'Inter\\', sans-serif; font-size: 2rem; font-weight: 900; color: #ef4444; letter-spacing: -1px;'>{selected_apt}</div>
                    <div style='background: rgba(239,68,68,0.08); color: #ef4444; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; border: 1px solid rgba(239,68,68,0.2); letter-spacing:0.5px;'>ACTIVE THREAT</div>
                </div>
                
                <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; margin-bottom: 32px;'>
                    <div>
                        <div style='font-family:\\'Inter\\', sans-serif; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Origin</div>
                        <div style='font-family:\\'Inter\\', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a;'>{profile.get('origin', 'Unknown')}</div>
                    </div>
                    <div>
                        <div style='font-family:\\'Inter\\', sans-serif; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Motivation</div>
                        <div style='font-family:\\'Inter\\', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a;'>{profile.get('motivation', 'Unknown')}</div>
                    </div>
                    <div>
                        <div style='font-family:\\'Inter\\', sans-serif; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Primary Target</div>
                        <div style='font-family:\\'Inter\\', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a;'>{target_str}</div>
                    </div>
                </div>
                
                <div style='font-family:\\'Inter\\', sans-serif; font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px;'>Known Signatures & Tools</div>
                <div style='display: flex; flex-wrap: wrap; gap: 10px;'>
                    {tools_html}
                </div>
            </div>
            \"\"\", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to load Threat Intel: {e}")

with tab3:"""

text = pattern.sub(new_tab2, text)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
