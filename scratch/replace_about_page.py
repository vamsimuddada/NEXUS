import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace the entire About block
start_str = 'if st.query_params.get("page") == "about":'
# The block ends before the MAIN DASHBOARD section
end_str = 'if "current_page" not in st.session_state:'

start_idx = text.find(start_str)
end_idx = text.find(end_str)

if start_idx != -1 and end_idx != -1:
    old_block = text[start_idx:end_idx]
    
    new_block = '''if st.query_params.get("page") == "about":
    st.markdown("<div style='margin-bottom:24px;'>", unsafe_allow_html=True)
    if st.button(" Back to Command Center"):
        st.query_params.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style=\\"font-family:'Space Grotesk', sans-serif; font-size:3.5rem; font-weight:900; color:#0f172a; letter-spacing:-2px; margin-bottom:32px;\\">ABOUT THE CREATOR</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        # Profile Picture Box
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fafc, #f1f5f9); border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.02);">
            <img src="https://ui-avatars.com/api/?name=Vamsi&background=3b82f6&color=fff&size=256" style="width: 160px; height: 160px; border-radius: 50%; border: 4px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <h2 style="font-family:'Space Grotesk', sans-serif; margin:0; color:#0f172a; font-weight:800; font-size:1.8rem;">Vamsi</h2>
            <p style="color:#64748b; font-weight:600; font-size:0.95rem; margin-top:4px; margin-bottom:20px;">Lead Security Engineer</p>
            
            <div style="text-align: left; margin-top: 24px; border-top: 1px solid #e2e8f0; padding-top: 20px;">
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px; color:#475569;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                    <span style="font-size:0.95rem;">vamsi@example.com</span>
                </div>
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px; color:#475569;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                    <span style="font-size:0.95rem;">+1 (555) 000-0000</span>
                </div>
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px; color:#475569;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>
                    <span style="font-size:0.95rem;">linkedin.com/in/vamsi</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 32px; box-shadow: 0 10px 25px rgba(0,0,0,0.02); height: 100%;">
            <h3 style="font-family:'Space Grotesk', sans-serif; color:#0f172a; margin-top:0; margin-bottom:20px; font-size:1.5rem;">Professional Summary</h3>
            <p style="color:#475569; font-size:1.05rem; line-height:1.8; margin-bottom:24px;">
                I am a passionate Security Engineer and Architect with a focus on AI-driven threat intelligence and autonomous defense systems. I developed Project NEXUS to push the boundaries of how we simulate cyber warfare and build self-patching enterprise networks.
            </p>
            <p style="color:#475569; font-size:1.05rem; line-height:1.8; margin-bottom:32px;">
                With expertise in Python, Large Language Models (LLMs), and SIEM integrations, my goal is to automate the Security Operations Center (SOC) and build resilient networks capable of defending against next-generation persistent threats.
            </p>
            
            <h3 style="font-family:'Space Grotesk', sans-serif; color:#0f172a; margin-top:0; margin-bottom:20px; font-size:1.5rem;">Project NEXUS Details</h3>
            <div style="background: #f8fafc; border-left: 4px solid #3b82f6; padding: 16px 20px; border-radius: 4px;">
                <ul style="margin: 0; padding-left: 20px; color: #475569; line-height: 1.8;">
                    <li><b>Architecture:</b> Multi-Agent Swarm vs Tri-Brain Defense Ensemble</li>
                    <li><b>SIEM Integration:</b> Native ECS & NDJSON compatibility (Splunk/Elastic)</li>
                    <li><b>Threat Modeling:</b> Strictly adheres to the MITRE ATT&CK Framework</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.stop()  # Stop rendering the rest of the dashboard when on the about page

'''
    
    text = text.replace(old_block, new_block)
    
    with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
        f.write(text)

