import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# I will just find the newly broken string block and fix it.
idx_start = text.find('card_html = f"""')
idx_end = text.find('st.markdown(card_html, unsafe_allow_html=True)', idx_start)

if idx_start != -1 and idx_end != -1:
    new_card_html = """card_html = f\"\"\"
<div style="background: #ffffff; border: 1px solid #cbd5e1; border-left: 4px solid #0f172a; padding: 24px; border-radius: 6px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 20px;">
<div style="font-family:'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a; letter-spacing: -0.5px;">{t_label}</div>
<div style="background: #0f172a; color: #ffffff; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; padding: 4px 10px; border-radius: 4px; font-weight: 700; letter-spacing: 0.5px;">ACTION REQUIRED</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 32px;">
<div>
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">
<div style="color: #334155; font-weight: 800; font-size: 0.75rem; font-family: 'Inter', sans-serif; letter-spacing: 1px;">PHASE 1: SIEM DETECTION</div>
</div>
<div style="font-family:'Inter', sans-serif; font-size: 0.95rem; color: #334155; line-height: 1.6; background: #f8fafc; padding: 16px; border-radius: 4px; border: 1px solid #e2e8f0;">
<b>Context:</b> The adversary utilizes this technique to establish persistence or execute lateral movement. <br><br>
<b>Rule Logic:</b> {det}
</div>
</div>
<div>
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">
<div style="color: #334155; font-weight: 800; font-size: 0.75rem; font-family: 'Inter', sans-serif; letter-spacing: 1px;">PHASE 2: NETWORK REMEDIATION</div>
</div>
<div style="font-family:'Inter', sans-serif; font-size: 0.95rem; color: #334155; line-height: 1.6; background: #f8fafc; padding: 16px; border-radius: 4px; border: 1px solid #e2e8f0;">
<b>Objective:</b> Immediately sever the attack path and harden the vulnerable vector. <br><br>
<b>Action:</b> Initiate {mit} protocol across affected subnets. Enforce strict access controls and verify telemetry isolation.
</div>
</div>
</div>
</div>
\"\"\"
                            """
    text = text[:idx_start] + new_card_html + text[idx_end:]

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
