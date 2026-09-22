import codecs
import re
from pathlib import Path

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace the PDF generation method to use fpdf2 natively
old_try_except = """        # Generate PDF with xhtml2pdf (native python)
        try:
            from xhtml2pdf import pisa
            with open(output_path, "w+b") as out_pdf:
                pisa_status = pisa.CreatePDF(full_html, dest=out_pdf)
            if pisa_status.err:
                print("[PDF] xhtml2pdf encountered errors")
            size_kb = Path(output_path).stat().st_size // 1024
            print(f"[PDF] Generated natively via xhtml2pdf: {output_path} ({size_kb}KB)")
            return output_path
        except Exception as e:
            print(f"[PDF] xhtml2pdf failed ({e}) - returning HTML")
            return html_path"""

new_try_except = """        # Generate PDF with fpdf2 (pure python, no C extensions required)
        try:
            from fpdf import FPDF
            
            class ExecutiveReport(FPDF):
                def header(self):
                    self.set_fill_color(15, 23, 42) # #0f172a
                    self.rect(0, 0, 210, 297, 'F')
                    self.set_font("helvetica", "B", 18)
                    self.set_text_color(0, 210, 255) # Cyan
                    self.cell(0, 15, "NEXUS EXECUTIVE INCIDENT REPORT", 0, 1, "C")
                    self.set_draw_color(30, 41, 59) # Slate
                    self.line(10, 25, 200, 25)
                    self.ln(10)
                    
                def footer(self):
                    self.set_y(-15)
                    self.set_font("helvetica", "I", 8)
                    self.set_text_color(148, 163, 184)
                    self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

            pdf = ExecutiveReport()
            pdf.add_page()
            
            # Parse simple markdown
            lines = body_md.split("\\n")
            for line in lines:
                if line.startswith("# "): continue # Skip main title
                elif line.startswith("## "):
                    pdf.set_font("helvetica", "B", 14)
                    pdf.set_text_color(245, 158, 11) # Amber
                    pdf.cell(0, 10, line.replace("## ", "").strip(), 0, 1)
                    pdf.ln(2)
                elif line.startswith("**"):
                    pdf.set_font("helvetica", "B", 11)
                    pdf.set_text_color(99, 102, 241) # Indigo
                    pdf.cell(0, 8, line.replace("**", "").strip(), 0, 1)
                elif line.startswith("---"):
                    pdf.set_draw_color(30, 41, 59)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(8)
                elif "|" in line and "---" not in line:
                    pdf.set_font("courier", "", 9)
                    pdf.set_text_color(203, 213, 225)
                    pdf.cell(0, 6, line.strip(), 0, 1)
                elif line.strip():
                    pdf.set_font("helvetica", "", 10)
                    pdf.set_text_color(226, 232, 240)
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
            return html_path"""

text = text.replace(old_try_except, new_try_except)

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)
