import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Locate the exact tab2 block we need to replace
start_marker = "with r2:"
end_marker = "except Exception as e:"
idx_start = text.find(start_marker)
idx_end = text.find(end_marker)

new_block = """with r2:
            profile = client.get_apt_profile(selected_apt)
            targets = profile.get('targets', ['Unknown'])
            target_str = targets[0] if isinstance(targets, list) else targets
            soph = str(profile.get('sophistication', 'Unknown')).replace('_', ' ').upper()
            
            from integrations.taxii_client import STATIC_TECHNIQUES
            
            tools_html_list = []
            playbook_items = []
            
            for mw in profile.get('techniques', []):
                tech_info = STATIC_TECHNIQUES.get(mw, {})
                name = tech_info.get('name', 'Unknown Signature')
                t_label = f"{mw}: {name}"
                tools_html_list.append(f"<span style=\\"background:#f8fafc; color:#334155; padding:8px 16px; border-radius:8px; font-family:'JetBrains Mono', monospace; font-size:0.9rem; font-weight:600; border:1px solid #e2e8f0;\\">{t_label}</span>")
                
                det = tech_info.get('detection', 'No detection strategy known.')
                mit = tech_info.get('mitigations', ['No mitigation known.'])
                mit_str = ", ".join(mit) if isinstance(mit, list) else mit
                
                playbook_items.append((t_label, det, mit_str))
                
            tools_html = "".join(tools_html_list)
            
            st.markdown(f\"\"\"
<div style='background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); margin-bottom: 20px;'>
<div style='display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 20px; margin-bottom: 24px;'>
<div style="font-family:'Inter', sans-serif; font-size: 2rem; font-weight: 900; color: #ef4444; letter-spacing: -1px;">{selected_apt}</div>
<div style='background: rgba(239,68,68,0.08); color: #ef4444; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; border: 1px solid rgba(239,68,68,0.2); letter-spacing:0.5px;'>ACTIVE THREAT</div>
</div>

<div style='display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 24px; margin-bottom: 32px;'>
<div>
<div style="font-family:'Inter', sans-serif; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Origin</div>
<div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a;">{profile.get('origin', 'Unknown')}</div>
</div>
<div>
<div style="font-family:'Inter', sans-serif; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Motivation</div>
<div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a;">{profile.get('motivation', 'Unknown')}</div>
</div>
<div>
<div style="font-family:'Inter', sans-serif; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Target</div>
<div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a;">{target_str}</div>
</div>
<div>
<div style="font-family:'Inter', sans-serif; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Sophistication</div>
<div style="font-family:'Inter', sans-serif; font-size: 1.25rem; font-weight: 800; color: #ef4444;">{soph}</div>
</div>
</div>

<div style="font-family:'Inter', sans-serif; font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px;">Known Signatures & Techniques</div>
<div style='display: flex; flex-wrap: wrap; gap: 10px;'>
{tools_html}
</div>
</div>
\"\"\", unsafe_allow_html=True)

            with st.expander("🛡️ Defense Playbook (SIEM Mitigations)"):
                st.markdown("<p style=\\"font-family:'Inter', sans-serif; font-size:0.95rem; color:#64748b; margin-bottom:16px;\\">Recommended SIEM detection rules and network mitigations for the techniques utilized by this threat actor.</p>", unsafe_allow_html=True)
                for t_label, det, mit in playbook_items:
                    st.markdown(f"<div style=\\"font-family:'Inter', sans-serif; font-weight:800; color:#0f172a; margin-top:12px; margin-bottom:4px;\\">{t_label}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style=\\"font-family:'Inter', sans-serif; font-size:0.9rem; color:#475569; margin-bottom:4px;\\"><b>Detection:</b> {det}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style=\\"font-family:'Inter', sans-serif; font-size:0.9rem; color:#475569; margin-bottom:12px;\\"><b>Mitigation:</b> {mit}</div>", unsafe_allow_html=True)
                    
    """

text = text[:idx_start] + new_block + text[idx_end:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
