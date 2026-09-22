import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Locate the ultra-premium playbook block and strip all leading whitespace to fix the raw HTML bug.
# Also remove the blue left border and replace it with a cleaner, more subtle top border.

old_card_start = 'card_html = f"""\n                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6;'
idx = text.find(old_card_start)
if idx != -1:
    end_idx = text.find('st.markdown(card_html, unsafe_allow_html=True)', idx)
    old_block = text[idx:end_idx]
    
    new_card_html = """card_html = f\"\"\"
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
                    """
    text = text.replace(old_block, new_card_html)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
