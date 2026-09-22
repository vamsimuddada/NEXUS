import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 2. Inject Analytics button under the START CAMPAIGN block
start_btn_block = """                    threading.Thread(target=run_sim, args=(msg_q,), daemon=True).start()
                    st.rerun()"""

inject_btn = """                    threading.Thread(target=run_sim, args=(msg_q,), daemon=True).start()
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.session_state.current_page == 'home':
                if st.button("📊 ANALYTICS & EXPORTS", use_container_width=True):
                    st.session_state.current_page = 'analytics'
                    st.rerun()
            else:
                if st.button("🛡️ BACK TO SOC", use_container_width=True):
                    st.session_state.current_page = 'home'
                    st.rerun()"""

text = text.replace(start_btn_block, inject_btn)

# 3. Remove st.tabs and replace with if/else routing
text = text.replace('tab1, tab2 = st.tabs(["SOC Overview", "Analytics & Export"])', '')
text = text.replace('with tab1:', "if st.session_state.current_page == 'home':")
text = text.replace('with tab2:', "if st.session_state.current_page == 'analytics':")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
