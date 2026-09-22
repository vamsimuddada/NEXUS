import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Replace the sliders with locked variables
old_sliders = """            hosts = st.slider("Target Hosts", 2, 20, 8)
            users = st.slider("Simulated Users", 5, 50, 24)"""
new_sliders = """            st.markdown("<p style='font-size: 0.85rem; color: #64748b; margin-top: 10px; margin-bottom: 2px;'>Target Hosts</p>", unsafe_allow_html=True)
            st.markdown("<div style='background: rgba(255,255,255,0.05); border: 1px solid #1e293b; padding: 10px 14px; border-radius: 6px; font-weight: 500; font-family: monospace; color: #0ea5e9;'>8 (LOCKED)</div>", unsafe_allow_html=True)
            hosts = 8
            st.markdown("<p style='font-size: 0.85rem; color: #64748b; margin-top: 15px; margin-bottom: 2px;'>Simulated Users</p>", unsafe_allow_html=True)
            st.markdown("<div style='background: rgba(255,255,255,0.05); border: 1px solid #1e293b; padding: 10px 14px; border-radius: 6px; font-weight: 500; font-family: monospace; color: #0ea5e9;'>24 (LOCKED)</div><br>", unsafe_allow_html=True)
            users = 24"""
text = text.replace(old_sliders, new_sliders)

# 2. Inject Analytics button under thread.start() \n st.rerun()
start_btn_block = """                    thread.start()
                    st.rerun()"""
inject_btn = """                    thread.start()
                    st.rerun()
            
            # Analytics Navigation Button
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
