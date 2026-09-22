import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

old_pdf_button = 'st.button(" GENERATE EXECUTIVE REPORT (PDF)", use_container_width=True, type="primary")'
new_pdf_button = """
            pdfs = list(Path("data/research").glob("paper_*.pdf"))
            if pdfs:
                latest_pdf = sorted(pdfs, key=lambda x: x.stat().st_mtime)[-1]
                st.download_button(" DOWNLOAD LATEST REPORT (PDF)", data=latest_pdf.read_bytes(), file_name="NEXUS_Executive_Report.pdf", mime="application/pdf", use_container_width=True, type="primary")
            else:
                st.button(" NO REPORTS AVAILABLE", disabled=True, use_container_width=True, type="primary")
"""

text = text.replace(old_pdf_button, new_pdf_button)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
