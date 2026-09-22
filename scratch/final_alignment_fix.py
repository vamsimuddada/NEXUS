import codecs

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix table column widths so they are strictly uniform and don't dynamically shift when string length changes
old_table_width = """                    # Calculate proportional column widths (Rank is small, Entity is larger, etc)
                    col_widths = []
                    for c in cols:
                        w = 20 if len(c) < 5 else (40 if len(c) < 15 else 50)
                        col_widths.append(w)
                    
                    # Normalize to 190mm page width
                    total_w = sum(col_widths)
                    if total_w > 0:
                        col_widths = [w * (190 / total_w) for w in col_widths]
                    else:
                        col_widths = [190 / len(cols)] * len(cols)"""

new_table_width = """                    # Use strictly uniform column widths to prevent grid-shifting
                    col_widths = [190 / len(cols)] * len(cols)"""

text = text.replace(old_table_width, new_table_width)

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)


with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Restore the Appendices so the user gets their 8-page SOC threat intelligence data back
old_sections = """            "\\n" + self.results(campaign_record)
        ]"""
new_sections = """            "\\n" + self.results(campaign_record),
            "\\n" + self.appendix_personas(campaign_record),
            "\\n" + self.appendix_sigma_log(campaign_record)
        ]"""
text = text.replace(old_sections, new_sections)

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
