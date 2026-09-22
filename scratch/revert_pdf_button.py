import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('pdfs = list(Path("data/research").glob("paper_*.html"))', 'pdfs = list(Path("data/research").glob("paper_*.pdf"))')
text = text.replace('st.download_button(" DOWNLOAD REPORT (HTML)", data=latest_pdf.read_bytes(), file_name="NEXUS_Executive_Report.html", mime="text/html"', 'st.download_button(" DOWNLOAD REPORT (PDF)", data=latest_pdf.read_bytes(), file_name="NEXUS_Executive_Report.pdf", mime="application/pdf"')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
