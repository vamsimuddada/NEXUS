import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Use regex to find the table rendering block
pattern = re.compile(r'table_html\s*=\s*"<table.*?st\.markdown\(table_html,\s*unsafe_allow_html=True\)', re.DOTALL)

new_table = """table_html = "<style>.fw-row { background-color: #ffffff; box-shadow: 0 1px 2px rgba(15,23,42,0.04); transition: all 0.2s ease; } .fw-row:hover { transform: translateX(4px); box-shadow: 0 4px 12px rgba(15,23,42,0.08); border-left-color: #0f172a !important; }</style>"
                table_html += "<table style='width:100%; border-collapse: separate; border-spacing: 0 6px; margin-top:0px; font-family: \\'Inter\\', sans-serif; font-size: 0.85rem;'>"
                table_html += "<tr><th style='text-align:left; padding:0px 12px 4px 12px; color:#94a3b8; font-weight:700; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em;'>Source IP</th><th style='text-align:left; padding:0px 12px 4px 12px; color:#94a3b8; font-weight:700; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em;'>Signature</th><th style='text-align:right; padding:0px 12px 4px 12px; color:#94a3b8; font-weight:700; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em;'>Action</th></tr>"
                for row in ip_feed:
                    if "BLOCK" in row["Action"]:
                        badge = "<span style='background-color:rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color:#10b981; padding:4px 8px; border-radius:4px; font-weight:800; font-size:0.7rem; letter-spacing:0.5px;'>BLOCKED</span>"
                    else:
                        badge = "<span style='background-color:rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); color:#f59e0b; padding:4px 8px; border-radius:4px; font-weight:800; font-size:0.7rem; letter-spacing:0.5px;'>DETECTED</span>"
                        
                    table_html += f"<tr class='fw-row'><td style='padding:10px 12px; font-family:\\'Space Grotesk\\', monospace; font-weight:800; color:#0f172a; border-radius: 6px 0 0 6px; border-left: 4px solid #3b82f6;'>{row['IP Address']}</td><td style='padding:10px 12px; color:#475569; font-weight:500;'>{row['Reason']}</td><td style='padding:10px 12px; text-align:right; border-radius: 0 6px 6px 0;'>{badge}</td></tr>"
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)"""

text = pattern.sub(new_table, text)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
