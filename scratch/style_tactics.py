import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Fix the font tags for the specific section headers
text = text.replace(
    "<h3 style='color:#0f172a; font-family: 'Space Grotesk', sans-serif; font-weight:800; letter-spacing:-1px; margin-top:32px; margin-bottom:16px;'>Tactics & Perimeter Defense</h3>",
    "<h3 style='color:#0f172a; font-family: \\'Space Grotesk\\', sans-serif !important; font-weight:800; letter-spacing:-1px; margin-top:32px; margin-bottom:16px;'>Tactics & Perimeter Defense</h3>"
)

text = text.replace(
    "<h4 style='color:#0f172a; font-family: 'Space Grotesk', sans-serif; font-weight:700; font-size:1.05rem; margin-bottom:12px;'>MITRE ATT&CK Matrix</h4>",
    "<h4 style='color:#0f172a; font-family: \\'Space Grotesk\\', sans-serif !important; font-weight:700; font-size:1.2rem; margin-bottom:12px;'>MITRE ATT&CK Matrix</h4>"
)

text = text.replace(
    "<h4 style='color:#0f172a; font-family: 'Space Grotesk', sans-serif; font-weight:700; font-size:1.05rem; margin-bottom:12px;'>Live Firewall Blocks</h4>",
    "<h4 style='color:#0f172a; font-family: \\'Space Grotesk\\', sans-serif !important; font-weight:700; font-size:1.2rem; margin-bottom:12px;'>Live Firewall Blocks</h4>"
)

# 2. Upgrade the Live Firewall Blocks table styling
old_table = """                table_html = "<table style='width:100%; border-collapse: collapse; margin-top:8px;'>"
                table_html += "<tr style='border-bottom: 1px solid rgba(0,0,0,0.1);'><th style='text-align:left; padding:8px; color:#475569;'>Source IP</th><th style='text-align:left; padding:8px; color:#475569;'>Technique Signature</th><th style='text-align:right; padding:8px; color:#475569;'>Action</th></tr>"
                for row in ip_feed:
                    act_color = "#10b981" if "BLOCK" in row["Action"] else "#f59e0b"
                    table_html += f"<tr style='border-bottom: 1px solid rgba(0,0,0,0.05);'><td style='padding:8px; font-family:monospace; color:#3b82f6;'>{row['IP Address']}</td><td style='padding:8px; color:#334155;'>{row['Reason']}</td><td style='padding:8px; text-align:right; color:{act_color}; font-weight:bold;'>{row['Action']}</td></tr>"
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)"""

new_table = """                table_html = "<table style='width:100%; border-collapse: separate; border-spacing: 0 4px; margin-top:4px; font-family: \\'Inter\\', sans-serif; font-size: 0.9rem;'>"
                table_html += "<tr><th style='text-align:left; padding:4px 12px; color:#64748b; font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;'>Source IP</th><th style='text-align:left; padding:4px 12px; color:#64748b; font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;'>Technique Signature</th><th style='text-align:right; padding:4px 12px; color:#64748b; font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;'>Action</th></tr>"
                for row in ip_feed:
                    if "BLOCK" in row["Action"]:
                        badge = "<span style='background-color:rgba(16, 185, 129, 0.15); color:#059669; padding:4px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; letter-spacing:0.5px;'>BLOCKED</span>"
                    else:
                        badge = "<span style='background-color:rgba(245, 158, 11, 0.15); color:#d97706; padding:4px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; letter-spacing:0.5px;'>DETECTED</span>"
                        
                    table_html += f"<tr style='background-color: #f8fafc; transition: all 0.2s;'><td style='padding:10px 12px; font-family:monospace; color:#3b82f6; border-radius: 8px 0 0 8px; border-left: 3px solid #3b82f6;'>{row['IP Address']}</td><td style='padding:10px 12px; color:#334155; font-weight:500;'>{row['Reason']}</td><td style='padding:10px 12px; text-align:right; border-radius: 0 8px 8px 0;'>{badge}</td></tr>"
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)"""

text = text.replace(old_table, new_table)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
