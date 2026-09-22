import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Remove the "Target Hosts" and "Simulated Users" visual blocks entirely
old_target_hosts = "st.markdown(\"<p style='font-size: 0.85rem; color: #64748b; margin-top: 10px; margin-bottom: 2px;'>Target Hosts</p>\", unsafe_allow_html=True)"
old_target_box = "st.markdown(\"<div style='background: rgba(255,255,255,0.05); border: 1px solid #1e293b; padding: 10px 14px; border-radius: 6px; font-weight: 500; font-family: monospace; color: #0ea5e9;'>8 (LOCKED)</div>\", unsafe_allow_html=True)"
old_sim_users = "st.markdown(\"<p style='font-size: 0.85rem; color: #64748b; margin-top: 15px; margin-bottom: 2px;'>Simulated Users</p>\", unsafe_allow_html=True)"
old_sim_box = "st.markdown(\"<div style='background: rgba(255,255,255,0.05); border: 1px solid #1e293b; padding: 10px 14px; border-radius: 6px; font-weight: 500; font-family: monospace; color: #0ea5e9;'>24 (LOCKED)</div><br>\", unsafe_allow_html=True)"

text = text.replace(old_target_hosts, "")
text = text.replace(old_target_box, "")
text = text.replace(old_sim_users, "")
text = text.replace(old_sim_box, "")

# 2. Remove emojis from the buttons
text = text.replace('st.button("📊 ANALYTICS & EXPORTS"', 'st.button("ANALYTICS & EXPORTS"')
text = text.replace('st.button("🛡️ BACK TO SOC"', 'st.button("BACK TO SOC"')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
