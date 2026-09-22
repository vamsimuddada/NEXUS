import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Remove the misplaced button from op_c2
# Let's find the exact text
start_idx = text.find('            st.markdown("<hr style=\'margin-top: 20px; margin-bottom: 20px;\'/>", unsafe_allow_html=True)')
end_idx = text.find('st.rerun()\n\n            \n        feed_html =')

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + text[end_idx+10:]

# 2. Inject it safely into op_c1
target_code = r"""                    threading.Thread(target=run_sim, args=(msg_q,), daemon=True).start()
                    st.rerun()"""

new_code = r"""                    threading.Thread(target=run_sim, args=(msg_q,), daemon=True).start()
                    st.rerun()
            
            st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px; border-color: transparent;'/>", unsafe_allow_html=True)
            if st.button("ANALYTICS & EXPORTS", use_container_width=True):
                st.session_state.current_page = 'analytics'
                st.rerun()"""

text = text.replace(target_code, new_code)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
