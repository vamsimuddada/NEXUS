import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Use regex to find the table rendering block
pattern = re.compile(r'table_html\s*=\s*"<table[^>]*>".*?st\.markdown\(table_html,\s*unsafe_allow_html=True\)', re.DOTALL)

new_table = """table_html = "<table style='width:100%; border-collapse: separate; border-spacing: 0 4px; margin-top:4px; font-family: \\'Inter\\', sans-serif; font-size: 0.9rem;'>"
                table_html += "<tr><th style='text-align:left; padding:4px 12px; color:#64748b; font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;'>Source IP</th><th style='text-align:left; padding:4px 12px; color:#64748b; font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;'>Technique Signature</th><th style='text-align:right; padding:4px 12px; color:#64748b; font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;'>Action</th></tr>"
                for row in ip_feed:
                    if "BLOCK" in row["Action"]:
                        badge = "<span style='background-color:rgba(16, 185, 129, 0.15); color:#059669; padding:4px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; letter-spacing:0.5px;'>BLOCKED</span>"
                    else:
                        badge = "<span style='background-color:rgba(245, 158, 11, 0.15); color:#d97706; padding:4px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; letter-spacing:0.5px;'>DETECTED</span>"
                        
                    table_html += f"<tr style='background-color: #f8fafc; transition: all 0.2s;'><td style='padding:10px 12px; font-family:monospace; color:#3b82f6; border-radius: 8px 0 0 8px; border-left: 3px solid #3b82f6;'>{row['IP Address']}</td><td style='padding:10px 12px; color:#334155; font-weight:500;'>{row['Reason']}</td><td style='padding:10px 12px; text-align:right; border-radius: 0 8px 8px 0;'>{badge}</td></tr>"
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)"""

text = pattern.sub(new_table, text)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
