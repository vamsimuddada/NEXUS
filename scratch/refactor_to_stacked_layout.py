import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

pattern = re.compile(r"c1, c2 = st\.columns\(\[1, 1\.5\]\).*?st\.error\(f\"Error parsing report: \{e\}\"\)", re.DOTALL)

new_text = """c1, c2 = st.columns(2)
            
            with c1:
                with st.container(border=True):
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Campaign overview</h3>", unsafe_allow_html=True)
                    st.write(f"**Battle ID:** `{report_data.get('battle_id', 'N/A')}`")
                    st.write(f"**Timestamp:** `{report_data.get('timestamp', 'N/A')}`")
                    st.markdown(f"**Outcome:** <span style='color:{win_color}; font-weight:800;'>{winner} VICTORY</span>", unsafe_allow_html=True)
            
            with c2:
                with st.container(border=True):
                    st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Blue Team Mitigations</h3>", unsafe_allow_html=True)
                    st.write(f"**SIGMA Rules Deployed:** `{metrics.get('sigma_rules', 0)}` dynamic rules written")
                    st.write(f"**Final Accuracy (F1):** `{(metrics.get('f1_score', 0)*100):.1f}%`")
                    st.write(f"**Precision:** `{(metrics.get('precision', 0)*100):.1f}%`")
                    st.write(f"**Recall:** `{(metrics.get('recall', 0)*100):.1f}%`")
                    st.markdown("<p style='color:#64748b; font-size:0.9rem; margin-top:16px;'>The autonomous Blue Team agent successfully analyzed the network traffic in real-time, identifying malicious signatures and deploying new SIGMA rules to block the execution pathways.</p>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f"<h3 style='color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:16px; font-weight:800;'>Executed Attack Vectors</h3>", unsafe_allow_html=True)
                if not logs:
                    st.info("No attacks executed during this campaign.")
                else:
                    for log in logs[:24]:
                        render_attack_card(log)
                    if len(logs) > 24:
                        st.markdown("<p style='color:#64748b; font-size:0.9rem;'><i>... showing first 24 attacks</i></p>", unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"Error parsing report: {e}")"""

match = pattern.search(text)
if match:
    text = text[:match.start()] + new_text + text[match.end():]
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(text)
    print("Replaced!")
else:
    print("Failed to match regex.")
