import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Remove the discussion section from the generated markdown
old_sections = """            "\\n" + self.results(campaign_record),
            "\\n" + self.discussion(campaign_record)"""
new_sections = """            "\\n" + self.results(campaign_record)"""
text = text.replace(old_sections, new_sections)

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)


with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the pdf generator to completely skip the ugly markdown table separator rows
old_table = """                elif line.startswith("---"):
                    pdf.set_draw_color(226, 232, 240)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(8)
                elif "|" in line and "---" not in line:"""

new_table = """                elif line.startswith("---"):
                    pdf.set_draw_color(226, 232, 240)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(8)
                elif "|" in line and "---" in line:
                    continue # Completely skip the markdown separator rows
                elif "|" in line and "---" not in line:"""

text = text.replace(old_table, new_table)

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)
