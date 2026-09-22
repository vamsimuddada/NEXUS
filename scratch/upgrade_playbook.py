import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

old_block = """            with st.expander("🛡️ Defense Playbook (SIEM Mitigations)"):
                st.markdown("<p style=\\"font-family:'Inter', sans-serif; font-size:0.95rem; color:#64748b; margin-bottom:16px;\\">Recommended SIEM detection rules and network mitigations for the techniques utilized by this threat actor.</p>", unsafe_allow_html=True)
                for t_label, det, mit in playbook_items:
                    st.markdown(f"<div style=\\"font-family:'Inter', sans-serif; font-weight:800; color:#0f172a; margin-top:12px; margin-bottom:4px;\\">{t_label}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style=\\"font-family:'Inter', sans-serif; font-size:0.9rem; color:#475569; margin-bottom:4px;\\"><b>Detection:</b> {det}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style=\\"font-family:'Inter', sans-serif; font-size:0.9rem; color:#475569; margin-bottom:12px;\\"><b>Mitigation:</b> {mit}</div>", unsafe_allow_html=True)"""

new_block = """            with st.expander("🛡️ Defense Playbook (SIEM Mitigations)"):
                st.markdown("<p style=\\"font-family:'Inter', sans-serif; font-size:0.95rem; color:#64748b; margin-bottom:20px;\\">Recommended SIEM detection rules and network mitigations for the techniques utilized by this threat actor.</p>", unsafe_allow_html=True)
                for t_label, det, mit in playbook_items:
                    card_html = f\"\"\"
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; padding: 18px; border-radius: 8px; margin-bottom: 16px;">
                       <div style="font-family:'Inter', sans-serif; font-size: 1.05rem; font-weight: 800; color: #0f172a; margin-bottom: 12px; letter-spacing: -0.3px;">{t_label}</div>
                       
                       <div style="display: flex; align-items: flex-start; gap: 12px; margin-bottom: 10px;">
                           <div style="background: rgba(245,158,11,0.1); color: #d97706; border: 1px solid rgba(245,158,11,0.2); padding: 4px 8px; border-radius: 6px; font-weight: 800; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px; margin-top: 2px; min-width: 90px; text-align: center;">DETECTION</div>
                           <div style="font-family:'Inter', sans-serif; font-size: 0.95rem; color: #475569; line-height: 1.5;">{det}</div>
                       </div>
                       
                       <div style="display: flex; align-items: flex-start; gap: 12px;">
                           <div style="background: rgba(16,185,129,0.1); color: #10b981; border: 1px solid rgba(16,185,129,0.2); padding: 4px 8px; border-radius: 6px; font-weight: 800; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px; margin-top: 2px; min-width: 90px; text-align: center;">MITIGATION</div>
                           <div style="font-family:'Inter', sans-serif; font-size: 0.95rem; color: #475569; line-height: 1.5;">{mit}</div>
                       </div>
                    </div>
                    \"\"\"
                    st.markdown(card_html, unsafe_allow_html=True)"""

text = text.replace(old_block, new_block)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
