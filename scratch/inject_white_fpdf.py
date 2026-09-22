import codecs

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

start_idx = text.find('        # Generate PDF with fpdf2')
end_idx = text.find('    def _pandoc_fallback')

new_block = """        # Generate PDF with fpdf2 using White Background and Space Grotesk
        try:
            from fpdf import FPDF
            import os
            
            class ExecutiveReport(FPDF):
                def header(self):
                    self.set_fill_color(255, 255, 255) # White Background
                    self.rect(0, 0, 210, 297, 'F')
                    self.set_font("SpaceGrotesk", "B", 22)
                    self.set_text_color(15, 23, 42) # Slate 900 (Dark Navy)
                    self.cell(0, 15, "NEXUS EXECUTIVE REPORT", 0, 1, "L")
                    self.set_draw_color(226, 232, 240) # Slate 200
                    self.line(10, 25, 200, 25)
                    self.ln(10)
                    
                def footer(self):
                    self.set_y(-15)
                    self.set_font("SpaceGrotesk", "", 9)
                    self.set_text_color(148, 163, 184)
                    self.cell(0, 10, f"PAGE {self.page_no()}", 0, 0, "C")

            pdf = ExecutiveReport()
            # Register Space Grotesk
            font_dir = "assets/fonts"
            pdf.add_font("SpaceGrotesk", "", os.path.join(font_dir, "SpaceGrotesk-Regular.ttf"), uni=True)
            pdf.add_font("SpaceGrotesk", "B", os.path.join(font_dir, "SpaceGrotesk-Bold.ttf"), uni=True)
            
            pdf.add_page()
            
            # Global Stats Hack
            try:
                import glob, json
                total_battles = len(glob.glob("data/reports/battle_*.json"))
                pdf.set_font("SpaceGrotesk", "B", 10)
                pdf.set_text_color(99, 102, 241) # Indigo
                pdf.cell(0, 8, f"DATABASE METRICS: {total_battles} HISTORICAL BATTLES LOGGED ACROSS ALL CAMPAIGNS", 0, 1)
                pdf.ln(5)
            except:
                pass
            
            # Parse simple markdown
            lines = body_md.split("\\n")
            for line in lines:
                if line.startswith("# "): continue # Skip main title
                elif line.startswith("## "):
                    pdf.set_font("SpaceGrotesk", "B", 16)
                    pdf.set_text_color(30, 41, 59) # Slate 800
                    pdf.cell(0, 10, line.replace("## ", "").strip(), 0, 1)
                    pdf.ln(2)
                elif line.startswith("**"):
                    pdf.set_font("SpaceGrotesk", "B", 11)
                    pdf.set_text_color(15, 23, 42) # Slate 900
                    pdf.cell(0, 8, line.replace("**", "").strip(), 0, 1)
                elif line.startswith("---"):
                    pdf.set_draw_color(226, 232, 240)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(8)
                elif "|" in line and "---" not in line:
                    pdf.set_font("SpaceGrotesk", "", 9)
                    pdf.set_text_color(71, 85, 105) # Slate 600
                    pdf.cell(0, 6, line.strip(), 0, 1)
                elif line.strip():
                    pdf.set_font("SpaceGrotesk", "", 10)
                    pdf.set_text_color(51, 65, 85) # Slate 700
                    # Handle encoding properly without failing
                    pdf.multi_cell(0, 6, line.strip())
                    pdf.ln(2)
                    
            pdf.output(output_path)
            size_kb = Path(output_path).stat().st_size // 1024
            print(f"[PDF] Generated natively via fpdf2: {output_path} ({size_kb}KB)")
            return output_path
            
        except ImportError:
            print("[PDF] fpdf2 not installed")
            return html_path
        except Exception as e:
            print(f"[PDF] fpdf2 failed ({e})")
            return html_path

"""

text = text[:start_idx] + new_block + text[end_idx:]

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)
