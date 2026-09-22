import codecs
import base64
import re

# Read the image and base64 encode it
with open("assets/vamsi_profile.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
img_uri = f"data:image/jpeg;base64,{encoded_string}"

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace the broken indented markdown block with an unindented one containing the base64 image
# Find the start of the profile block
start_str = 'st.markdown(\'\'\''
end_str = "    ''', unsafe_allow_html=True)"

start_idx = text.find(start_str, text.find('About the Developer'))
end_idx = text.find(end_str, start_idx)
if end_idx != -1:
    end_idx += len(end_str)

if start_idx != -1 and end_idx != -1:
    old_block = text[start_idx:end_idx]
    
    # We define the new block completely unindented internally to avoid Markdown treating it as a code block
    new_block = f"""st.markdown('''
<div style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 32px; display: flex; align-items: center; gap: 32px; box-shadow: 0 10px 25px rgba(0,0,0,0.02);">
    <img src="{img_uri}" style="width: 160px; height: 160px; border-radius: 50%; object-fit: cover; border: 4px solid #f8fafc; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <div>
        <h2 style="font-family:'Space Grotesk', sans-serif; margin:0 0 8px 0; color:#0f172a; font-weight:800; font-size:1.8rem;">Vamsi Muddada</h2>
        
        <div style="display:flex; flex-direction:column; gap: 12px; margin-top: 16px;">
            <div style="display:flex; align-items:center; gap:12px; color:#475569;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                <span style="font-size:1.05rem; font-family:'Space Grotesk', sans-serif;">vamsimuddada633@gmail.com</span>
            </div>
            <div style="display:flex; align-items:center; gap:12px; color:#475569;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                <span style="font-size:1.05rem; font-family:'Space Grotesk', sans-serif;">+91 82 474 26 515</span>
            </div>
            <div style="display:flex; align-items:center; gap:12px; color:#475569;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>
                <a href="https://www.linkedin.com/in/vamsimuddada/" target="_blank" style="font-size:1.05rem; font-family:'Space Grotesk', sans-serif; color:#3b82f6; text-decoration:none;">linkedin.com/in/vamsimuddada/</a>
            </div>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)"""

    text = text.replace(old_block, new_block)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
