import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace the existing header HTML with a pixel-perfect replica of the requested image
old_header = """<div style='display: flex; align-items: center; gap: 20px; margin-bottom: 24px; margin-top: 5px;'>
    <div style='width:60px; height:60px; border-radius:50%; background:linear-gradient(135deg, #e0e7ff, #ffffff); display:flex; align-items:center; justify-content:center; box-shadow: 0 10px 25px rgba(37, 99, 235, 0.15); border: 1px solid rgba(255,255,255,1);'>
        <svg width='32' height='32' viewBox='0 0 24 24' fill='none' stroke='#3b82f6' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>
            <path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'></path>
        </svg>
    </div>
    <div style="display: flex; align-items: baseline; gap: 12px;">
        <div style="font-family:'Google Sans', sans-serif; font-size:3.2rem; font-weight:800; color:#0f172a; line-height:1; letter-spacing:-2px;">NEXUS</div>
        <div style="font-family:'Google Sans', sans-serif; font-size:0.95rem; font-weight:600; color:#64748b; letter-spacing:0px;">- Neural Exploitation & eXplainable Unified Security</div>
        <a href="?page=about" target="_self" style="color:#3b82f6; margin-left:4px; margin-top:4px; opacity:0.6; transition:all 0.2s;" onmouseover="this.style.opacity=1; this.style.transform='scale(1.1)';" onmouseout="this.style.opacity=0.6; this.style.transform='scale(1)';" title="About Project">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
        </a>
    </div>
</div>"""

new_header = """<div style='display: flex; align-items: center; gap: 24px; margin-bottom: 24px; margin-top: 5px; margin-left: -10px;'>
    <div style='width:75px; height:75px; border-radius:50%; background:#ffffff; display:flex; align-items:center; justify-content:center; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.04);'>
        <svg width='36' height='36' viewBox='0 0 24 24' fill='none' stroke='#3b82f6' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>
            <path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'></path>
        </svg>
    </div>
    <div style="display: flex; align-items: baseline; gap: 14px;">
        <div style="font-family:'Inter', sans-serif; font-size:3.8rem; font-weight:900; color:#0B1121; line-height:1; letter-spacing:-3px;">NEXUS</div>
        <div style="font-family:'Inter', sans-serif; font-size:1.05rem; font-weight:600; color:#5A6B85; letter-spacing:-0.2px;">- Neural Exploitation & eXplainable Unified Security</div>
        <a href="?page=about" target="_self" style="color:#60A5FA; margin-left:6px; opacity:0.8; transition:all 0.2s;" onmouseover="this.style.opacity=1; this.style.transform='scale(1.1)';" onmouseout="this.style.opacity=0.8; this.style.transform='scale(1)';" title="About Project">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
        </a>
    </div>
</div>"""

text = text.replace(old_header, new_header)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
