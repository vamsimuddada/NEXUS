import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

perfect_threat_intel = """
    st.markdown("<br><br><div class='hero-header' style='font-size: 2.8rem; letter-spacing: -1px; margin-top: 16px;'>Threat Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<p style=\\"font-family:'Inter', sans-serif; color:#64748b; margin-bottom:32px; font-size:1.1rem; font-weight:500;\\">Automated Dossier & Defense Playbook</p>", unsafe_allow_html=True)
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from integrations.taxii_client import get_taxii
        client = get_taxii(use_live=True)
        groups = client.get_all_apt_groups()

        r1, r2 = st.columns([1, 2])
        with r1:
            with st.container(border=True):
                st.markdown('<h4 style="font-family:\\'Inter\\', sans-serif; font-size:1.4rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px; margin-top:0; margin-bottom:16px;">Tracked Actors</h4>', unsafe_allow_html=True)
                selected_apt = st.radio("Select Profile", groups, label_visibility="collapsed")
            
        with r2:
            profile = client.get_apt_profile(selected_apt)
            with st.container(border=True):
                st.markdown(f'<h3 style="color:#ef4444; font-family:\\'Inter\\', sans-serif; font-size:1.8rem; font-weight:900; letter-spacing:-1px; margin-top:0; margin-bottom:24px;">{selected_apt}</h3>', unsafe_allow_html=True)
                
                # 4-Column Grid
                origin_val = profile.get('origin', 'Unknown')
                mot_val = profile.get('motivation', 'Unknown')
                target_val = ", ".join(profile.get('targets', ['Unknown']))
                soph_val = "VERY HIGH" if selected_apt in ["APT29", "APT28"] else "HIGH"
                
                grid_html = f'''
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; margin-top: 16px;">
<div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px;">
<div style="font-family:'Inter', sans-serif; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 8px;">Origin</div>
<div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{origin_val}</div>
</div>
<div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px;">
<div style="font-family:'Inter', sans-serif; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 8px;">Motivation</div>
<div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{mot_val}</div>
</div>
<div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px;">
<div style="font-family:'Inter', sans-serif; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 8px;">Target Sector</div>
<div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{target_val}">{target_val}</div>
</div>
<div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px;">
<div style="font-family:'Inter', sans-serif; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-bottom: 8px;">Sophistication</div>
<div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #ef4444;">{soph_val}</div>
</div>
</div>
'''
                st.markdown(grid_html, unsafe_allow_html=True)
                
                st.markdown("<hr style='margin-top:24px; margin-bottom:24px;'>", unsafe_allow_html=True)
                
                st.markdown('<h4 style="font-family:\\'Inter\\', sans-serif; font-size:1.1rem; font-weight:800; color:#0f172a; margin-bottom:16px;">Known Techniques & Signatures</h4>', unsafe_allow_html=True)
                
                from integrations.taxii_client import STATIC_TECHNIQUES
                techs = profile.get('techniques', [])
                if not techs:
                    techs = profile.get('tools', [])
                    
                tech_html = ""
                playbook_items = []
                for t in techs:
                    t_name = t
                    if t in STATIC_TECHNIQUES:
                        t_name = f"{t}: {STATIC_TECHNIQUES[t]['name']}"
                        
                        # SAFE MITIGATION RETRIEVAL
                        mitig = STATIC_TECHNIQUES[t].get('mitigations', '')
                        if isinstance(mitig, list) and len(mitig) > 0:
                            mitig = mitig[0]
                        elif isinstance(mitig, list):
                            mitig = "Network Isolation"
                            
                        playbook_items.append((t_name, STATIC_TECHNIQUES[t]['detection'], mitig))
                    tech_html += f"<span style='background:#f1f5f9; border: 1px solid #e2e8f0; color:#334155; padding:6px 12px; border-radius:6px; font-family:\\'JetBrains Mono\\', monospace; font-weight:600; font-size:0.85rem; margin-right:10px; margin-bottom:10px; display:inline-block;'>{t_name}</span>"
                
                st.markdown(f"<div>{tech_html}</div><br>", unsafe_allow_html=True)
                
                if playbook_items:
                    with st.expander("🛡️ Defense Playbook (SIEM Mitigations)"):
                        st.markdown('<p style="font-family:\\'Inter\\', sans-serif; font-size:0.95rem; color:#64748b; margin-bottom:20px;">Recommended SIEM detection rules and network mitigations for the techniques utilized by this threat actor.</p>', unsafe_allow_html=True)
                        for t_label, det, mit in playbook_items:
                            card_html = f\"\"\"
<div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #0f172a; padding: 24px; border-radius: 8px; margin-bottom: 24px; box-shadow: 0 4px 15px rgba(15,23,42,0.03);">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 16px; margin-bottom: 20px;">
<div style="font-family:'Inter', sans-serif; font-size: 1.15rem; font-weight: 900; color: #0f172a; letter-spacing: -0.5px;">{t_label}</div>
<div style="background: #f8fafc; color: #64748b; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; padding: 4px 12px; border-radius: 20px; font-weight: 700; border: 1px solid #e2e8f0; letter-spacing: 0.5px;">MITRE ATT&CK DATABASE</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
<div style="background: #f8fafc; padding: 20px; border-radius: 8px; border: 1px dashed rgba(245,158,11,0.3);">
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
<div style="background: rgba(245,158,11,0.15); color: #d97706; border: 1px solid rgba(245,158,11,0.3); padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px;">SIEM DETECTION</div>
</div>
<div style="font-family:'Inter', sans-serif; font-size: 0.9rem; color: #475569; line-height: 1.6;">{det}</div>
</div>
<div style="background: #f8fafc; padding: 20px; border-radius: 8px; border: 1px dashed rgba(16,185,129,0.3);">
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
<div style="background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px;">NETWORK MITIGATION</div>
</div>
<div style="font-family:'Inter', sans-serif; font-size: 0.9rem; color: #475569; line-height: 1.6;">{mit}</div>
</div>
</div>
</div>
\"\"\"
                            st.markdown(card_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to load Threat Intel: {e}")
"""

idx = text.find('with tab2:')
if idx != -1:
    text = text[:idx] + perfect_threat_intel + '\n\n' + text[idx:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
