import codecs
import base64

# Base64 encode the image
with open("assets/vamsi_profile.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
img_uri = f"data:image/jpeg;base64,{encoded_string}"

# New HTML layout with the Professional Summary
raw_html = f"""<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 48px 0;'>
<h3 style="font-family:'Space Grotesk', sans-serif; font-weight:800; color:#0f172a; letter-spacing:-1px; margin-bottom:24px;">About the Developer</h3>
<div style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 40px; display: flex; gap: 48px; box-shadow: 0 10px 25px rgba(0,0,0,0.02); align-items: center; flex-wrap: wrap;">
    <div style="display: flex; flex-direction: column; align-items: center; min-width: 250px;">
        <img src="{img_uri}" style="width: 170px; height: 170px; border-radius: 50%; object-fit: cover; border: 4px solid #f8fafc; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 24px;">
        <h2 style="font-family:'Space Grotesk', sans-serif; margin:0 0 20px 0; color:#0f172a; font-weight:800; font-size:1.7rem; text-align: center;">Vamsi Muddada</h2>
        <div style="display:flex; flex-direction:column; gap: 14px; width: 100%;">
            <div style="display:flex; align-items:center; gap:14px; color:#475569;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                <span style="font-size:1.0rem; font-family:'Space Grotesk', sans-serif;">vamsimuddada633@gmail.com</span>
            </div>
            <div style="display:flex; align-items:center; gap:14px; color:#475569;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                <span style="font-size:1.0rem; font-family:'Space Grotesk', sans-serif;">+91 82 474 26 515</span>
            </div>
            <div style="display:flex; align-items:center; gap:14px; color:#475569;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>
                <a href="https://www.linkedin.com/in/vamsimuddada/" target="_blank" style="font-size:1.0rem; font-family:'Space Grotesk', sans-serif; color:#3b82f6; text-decoration:none;">LinkedIn Profile</a>
            </div>
        </div>
    </div>
    <div style="flex: 1; min-width: 300px; padding-left: 10px;">
        <h3 style="font-family:'Space Grotesk', sans-serif; margin:0 0 16px 0; color:#0f172a; font-weight:800; font-size:1.5rem;">Professional Summary</h3>
        <p style="color:#475569; font-size:1.05rem; line-height:1.75; font-family:'Segoe UI', sans-serif; margin-bottom: 20px;">
            I am a passionate Security Engineer and Architect specializing in AI-driven threat intelligence, network defense systems, and autonomous cybersecurity operations. As the creator of Project NEXUS, I have pioneered research into simulated cyber warfare environments where Large Language Models (LLMs) operate as both Red Team attackers and Blue Team defenders.
        </p>
        <p style="color:#475569; font-size:1.05rem; line-height:1.75; font-family:'Segoe UI', sans-serif;">
            My technical expertise bridges the gap between modern software engineering and advanced security operations. By integrating live STIX/TAXII threat feeds, SIEM monitoring, and autonomous agent swarms, my goal is to push the boundaries of how enterprises build self-patching, resilient networks capable of defending against next-generation persistent threats.
        </p>
    </div>
</div>"""

# Minify it perfectly
minified_html = raw_html.replace('\n', '')

# Ensure we escape double quotes for the python f-string, or we can just use ''' for the wrapper.
python_line = f"    st.markdown('''{minified_html}''', unsafe_allow_html=True)\n"

# Replace line 442 in dashboard.py
with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    lines = f.readlines()

# Find the exact line that has the old st.markdown profile block
for i, line in enumerate(lines):
    if line.startswith('    st.markdown("<hr style=\'border: none;') and 'About the Developer' in line:
        lines[i] = python_line
        break

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.writelines(lines)
