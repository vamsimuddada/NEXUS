import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

bad_block = """                st.dataframe(pd.DataFrame(ip_feed), use_container_width=True, hide_index=True, height=350)"""

html_table_generator = """                table_html = "<table style='width:100%; border-collapse: collapse; margin-top:8px;'>"
                table_html += "<tr style='border-bottom: 1px solid rgba(0,0,0,0.1);'><th style='text-align:left; padding:8px; color:#475569;'>IP Address</th><th style='text-align:left; padding:8px; color:#475569;'>Reason</th><th style='text-align:right; padding:8px; color:#475569;'>Action</th></tr>"
                for row in ip_feed:
                    table_html += f"<tr style='border-bottom: 1px solid rgba(0,0,0,0.05);'><td style='padding:12px 8px; font-family:monospace; color:#0f172a;'>{row['IP Address']}</td><td style='padding:12px 8px; color:#64748b;'>{row['Reason']}</td><td style='padding:12px 8px; text-align:right; color:#ef4444; font-weight:600;'>{row['Action']}</td></tr>"
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)"""

text = text.replace(bad_block, html_table_generator)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
