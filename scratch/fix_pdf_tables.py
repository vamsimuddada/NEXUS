import codecs

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

old_table_logic = """                elif "|" in line and "---" not in line:
                    pdf.set_font("SpaceGrotesk", "", 9)
                    pdf.set_text_color(71, 85, 105) # Slate 600
                    pdf.cell(0, 6, line.strip(), 0, 1)"""

new_table_logic = """                elif "|" in line and "---" not in line:
                    cols = [c.strip() for c in line.split("|") if c.strip()]
                    if not cols: continue
                    pdf.set_font("SpaceGrotesk", "", 9)
                    pdf.set_text_color(15, 23, 42) # Darker text for tables
                    pdf.set_draw_color(226, 232, 240) # Slate border
                    pdf.set_fill_color(248, 250, 252) # Slate 50 background
                    
                    # Calculate proportional column widths (Rank is small, Entity is larger, etc)
                    col_widths = []
                    for c in cols:
                        w = 20 if len(c) < 5 else (40 if len(c) < 15 else 50)
                        col_widths.append(w)
                    
                    # Normalize to 190mm page width
                    total_w = sum(col_widths)
                    if total_w > 0:
                        col_widths = [w * (190 / total_w) for w in col_widths]
                    else:
                        col_widths = [190 / len(cols)] * len(cols)

                    for i, c in enumerate(cols):
                        pdf.cell(col_widths[i], 8, c, 1, 0, 'C', fill=True)
                    pdf.ln(8)"""

text = text.replace(old_table_logic, new_table_logic)

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)
