import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Locate the old card_html string inside tab2
old_card_start = 'card_html = f"""\n                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; padding: 18px; border-radius: 8px; margin-bottom: 16px;">'
old_card_end = '</div>\n                    """\n                    st.markdown(card_html, unsafe_allow_html=True)'

idx_start = text.find(old_card_start)
idx_end = text.find(old_card_end) + len(old_card_end)

if idx_start != -1 and idx_end != -1:
    new_card = """card_html = f\"\"\"
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; padding: 24px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 15px rgba(15,23,42,0.03);">
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
                    st.markdown(card_html, unsafe_allow_html=True)"""
    
    text = text[:idx_start] + new_card + text[idx_end:]
    
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(text)
