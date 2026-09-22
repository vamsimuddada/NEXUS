import codecs

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

old_parse = """                elif line.startswith("## "):
                    pdf.set_font("SpaceGrotesk", "B", 16)
                    pdf.set_text_color(30, 41, 59) # Slate 800
                    pdf.cell(0, 10, line.replace("## ", "").strip(), 0, 1)
                    pdf.ln(2)"""

new_parse = """                elif line.startswith("## "):
                    pdf.set_font("SpaceGrotesk", "B", 16)
                    pdf.set_text_color(30, 41, 59) # Slate 800
                    pdf.cell(0, 10, line.replace("## ", "").strip(), 0, 1)
                    pdf.ln(2)
                elif line.startswith("![") and "](" in line:
                    import os
                    img_path = line.split("](")[1].split(")")[0]
                    if os.path.exists(img_path):
                        # Ensure there is enough vertical space
                        if pdf.get_y() > 200: pdf.add_page()
                        pdf.image(img_path, x=15, w=180)
                        pdf.ln(5)"""

text = text.replace(old_parse, new_parse)

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)
