import codecs
import re

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace the weasyprint try/except block with xhtml2pdf
old_try_except = """        # Generate PDF with weasyprint
        try:
            from weasyprint import HTML, CSS
            HTML(filename=html_path).write_pdf(output_path)
            size_kb = Path(output_path).stat().st_size // 1024
            print(f"[PDF] Generated  {output_path} ({size_kb}KB)")
            return output_path
        except ImportError:
            print("[PDF] weasyprint not available  HTML saved at", html_path)
            return html_path
        except Exception as e:
            print(f"[PDF] weasyprint failed ({e})  trying pandoc fallback")
            return self._pandoc_fallback(markdown_path, output_path)"""

new_try_except = """        # Generate PDF with xhtml2pdf (native python)
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

text = text.replace(old_try_except, new_try_except)

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)
