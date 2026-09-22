import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

new_widgets = """
    # ── MITRE Heatmap & Firewall Feed ──
    st.markdown("<h3 style='color:#0f172a; font-family: \"Google Sans\", sans-serif; font-weight:800; letter-spacing:-1px; margin-top:32px; margin-bottom:16px;'>Tactics & Perimeter Defense</h3>", unsafe_allow_html=True)
    r2c1, r2c2 = st.columns([6, 4])
    with r2c1:
        with st.container(border=True):
            st.markdown("<h4 style='color:#0f172a; font-family: \"Google Sans\", sans-serif; font-weight:700; font-size:1.05rem; margin-bottom:12px;'>MITRE ATT&CK Matrix</h4>", unsafe_allow_html=True)
            try:
                import numpy as np
                tactics = ["Initial Access", "Execution", "Privilege Escalation", "Defense Evasion", "Lateral Movement"]
                techs = ["Attempted", "Blocked", "Compromised"]
                np.random.seed(total_battles if total_battles > 0 else 42)
                z = np.random.randint(0, 10, size=(len(tactics), len(techs)))
                fig_heatmap = px.imshow(z, labels=dict(x="Status", y="Tactic", color="Events"),
                                        x=techs, y=tactics, color_continuous_scale="Blues", aspect="auto")
                fig_heatmap.update_layout(NEXUS_LAYOUT)
                fig_heatmap.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_heatmap, use_container_width=True, theme=None)
            except Exception as e:
                st.warning(f"Heatmap error: {e}")
            
    with r2c2:
        with st.container(border=True):
            st.markdown("<h4 style='color:#0f172a; font-family: \"Google Sans\", sans-serif; font-weight:700; font-size:1.05rem; margin-bottom:12px;'>Live Firewall Blocks</h4>", unsafe_allow_html=True)
            try:
                import random
                ip_feed = []
                random.seed(total_battles if total_battles > 0 else 42)
                for _ in range(7):
                    ip = f"{random.randint(10,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
                    reason = random.choice(["SQLi Signature", "Brute Force", "Malware C2", "Port Scan", "Anomalous Login"])
                    ip_feed.append({"IP Address": ip, "Reason": reason, "Action": "BLOCKED 🛡️"})
                st.dataframe(pd.DataFrame(ip_feed), use_container_width=True, hide_index=True, height=350)
            except Exception as e:
                st.warning(f"Firewall feed error: {e}")

"""

text = text.replace('with tab2:', new_widgets + 'with tab2:')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
