"""
NEXUS — PDF & LaTeX Paper Generator
Converts the arXiv-style Markdown paper draft into:
  1. Styled HTML → PDF via weasyprint (no LaTeX needed, ARM64-safe)
  2. LaTeX .tex source → compile with pdflatex if available

Both outputs are publication-ready.
"""

from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ── Markdown → HTML ───────────────────────────────────────────────────────────

def _md_to_html_body(md: str) -> str:
    """Minimal Markdown → HTML conversion (no extra deps)."""
    lines   = md.split("\n")
    output  = []
    in_table = False
    in_code  = False

    for line in lines:
        # Code blocks
        if line.startswith("```"):
            if in_code:
                output.append("</code></pre>")
                in_code = False
            else:
                lang = line[3:].strip() or ""
                output.append(f'<pre><code class="language-{lang}">')
                in_code = True
            continue
        if in_code:
            output.append(line.replace("<","&lt;").replace(">","&gt;"))
            continue

        # Table rows
        if line.startswith("|"):
            if not in_table:
                output.append("<table>")
                in_table = True
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.match(r"^[-:]+$", c) for c in cells if c):
                output.append("<thead></thead><tbody>")
                continue
            tag = "th" if not any("tbody" in o for o in output[-3:]) else "td"
            row = "".join(f"<{tag}>{c}</{tag}>" for c in cells)
            output.append(f"<tr>{row}</tr>")
            continue
        elif in_table:
            output.append("</tbody></table>")
            in_table = False

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            lvl = len(m.group(1))
            output.append(f"<h{lvl}>{m.group(2)}</h{lvl}>")
            continue

        # Horizontal rule
        if re.match(r"^---+$", line):
            output.append("<hr>")
            continue

        # Blank line
        if not line.strip():
            output.append("<p></p>")
            continue

        # Inline formatting
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        line = re.sub(r"\*(.+?)\*",     r"<em>\1</em>",         line)
        line = re.sub(r"`(.+?)`",       r"<code>\1</code>",     line)
        line = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', line)
        output.append(f"<p>{line}</p>")

    if in_table:
        output.append("</tbody></table>")
    return "\n".join(output)


# ── CSS for the paper ─────────────────────────────────────────────────────────

_PAPER_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=Source+Code+Pro:wght@400;600&display=swap');

@page {
  size: A4;
  margin: 2.5cm 2.8cm 2.5cm 2.8cm;
  @top-center {
    content: "NEXUS — Adversarial Co-Evolution";
    font-size: 9pt; color: #64748b;
  }
  @bottom-center {
    content: counter(page);
    font-size: 9pt; color: #64748b;
  }
}


            body { font-family: 'Space Grotesk', 'Helvetica', sans-serif; background: #0f172a; color: #e2e8f0; padding: 40px; }
            h1 { color: #00d2ff; text-align: center; border-bottom: 2px solid #1e293b; padding-bottom: 20px; font-weight: 800; font-size: 2.2rem; }
            h2 { color: #f59e0b; margin-top: 40px; font-weight: 700; border-bottom: 1px solid #1e293b; padding-bottom: 10px; }
            h3 { color: #6366f1; margin-top: 30px; font-weight: 600; }
            .meta { text-align: center; font-style: italic; color: #94a3b8; font-size: 0.95rem; margin-bottom: 50px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 30px; }
            th { background: #1e293b; color: #e2e8f0; font-weight: 700; padding: 12px; text-align: left; }
            td { padding: 12px; border-bottom: 1px solid #1e293b; color: #cbd5e1; }
            a { color: #00d2ff; text-decoration: none; }
            hr { border: none; border-top: 1px solid #1e293b; margin: 30px 0; }

/* body {
  font-family: 'Crimson Pro', 'Georgia', serif;
  font-size: 11pt;
  line-height: 1.6;
  color: #1a1a2e;
  max-width: 100%;
}

h1 {
  font-size: 18pt; font-weight: 600;
  color: #1e1b4b; margin-bottom: 6pt;
  border-bottom: 2pt solid #4f46e5;
  padding-bottom: 8pt;
}

h2 {
  font-size: 14pt; font-weight: 600;
  color: #312e81; margin-top: 20pt; margin-bottom: 8pt;
  border-bottom: 0.5pt solid #c7d2fe;
  padding-bottom: 4pt;
  page-break-after: avoid;
}

h3 {
  font-size: 12pt; font-weight: 600;
  color: #4338ca; margin-top: 14pt; margin-bottom: 6pt;
  page-break-after: avoid;
}

h4 {
  font-size: 11pt; font-weight: 600;
  color: #4f46e5; margin-top: 10pt; margin-bottom: 4pt;
}

p { margin-bottom: 6pt; text-align: justify; }

table {
  border-collapse: collapse; width: 100%;
  margin: 12pt 0; font-size: 9.5pt;
  page-break-inside: avoid;
}

th {
  background: #4f46e5; color: white;
  padding: 5pt 8pt; text-align: left;
  font-weight: 600;
}

td {
  border-bottom: 0.5pt solid #e0e7ff;
  padding: 4pt 8pt;
}

tr:nth-child(even) td { background: #f5f3ff; }

pre {
  background: #1e1b4b; color: #e2e8f0;
  padding: 10pt; border-radius: 4pt;
  font-size: 8.5pt; overflow-x: auto;
  page-break-inside: avoid;
  margin: 10pt 0;
}

code {
  font-family: 'Source Code Pro', monospace;
  font-size: 9pt;
  background: #f0f0ff;
  padding: 1pt 3pt;
  border-radius: 2pt;
}

pre code {
  background: transparent;
  padding: 0;
  color: inherit;
}

hr {
  border: none;
  border-top: 1pt solid #c7d2fe;
  margin: 16pt 0;
}

a { color: #4f46e5; text-decoration: none; }

strong { color: #1e1b4b; }

.abstract-box {
  background: #f5f3ff;
  border-left: 3pt solid #4f46e5;
  padding: 12pt 16pt;
  margin: 16pt 0;
  font-size: 10.5pt;
  page-break-inside: avoid;
}

.title-block {
  text-align: center;
  margin-bottom: 20pt;
}

.title-block h1 { border: none; text-align: center; }
.title-block .authors { color: #64748b; font-size: 11pt; margin-top: 6pt; }
.title-block .venue   { color: #94a3b8; font-size: 10pt; margin-top: 3pt; }
.title-block .date    { color: #94a3b8; font-size: 9pt; margin-top: 3pt; }
"""


# ── HTML wrapper ──────────────────────────────────────────────────────────────

def _wrap_html(title: str, authors: str, venue: str,
               body_html: str, generated_at: str) -> str:
    # Extract abstract section if present
    abstract_html = ""
    abstract_match = re.search(
        r"<h2>Abstract</h2>(.*?)<h2>", body_html, re.DOTALL
    )
    if abstract_match:
        abstract_text = abstract_match.group(1).strip()
        # Remove the inline abstract and replace with boxed version
        body_html = body_html.replace(
            f"<h2>Abstract</h2>{abstract_match.group(1)}",
            f'<h2>Abstract</h2><div class="abstract-box">{abstract_text}</div>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>{_PAPER_CSS}</style>
</head>
<body>
<div class="title-block">
  <h1>{title}</h1>
  <div class="authors">{authors}</div>
  <div class="venue">{venue}</div>
  <div class="date">Generated: {generated_at}</div>
</div>
<hr>
{body_html}
</body>
</html>"""


# ── LaTeX template ────────────────────────────────────────────────────────────

def _md_to_latex(md: str, title: str, authors: str) -> str:
    """Convert Markdown paper to LaTeX source."""
    lines  = md.split("\n")
    output = []
    in_table = in_code = in_abstract = False
    skip_title = True   # skip the first h1 (already in \title{})

    preamble = rf"""\documentclass{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{lmodern}}
\usepackage[margin=2.5cm]{{geometry}}
\usepackage{{booktabs}}
\usepackage{{hyperref}}
\usepackage{{xcolor}}
\usepackage{{listings}}
\usepackage{{microtype}}
\usepackage{{abstract}}
\usepackage{{titlesec}}
\titleformat{{\section}}{{\large\bfseries}}{{\\thesection}}{{1em}}{{}}
\hypersetup{{colorlinks=true,linkcolor=blue,urlcolor=blue}}
\definecolor{{codebg}}{{RGB}}{{30,27,75}}

\lstset{{
  basicstyle=\small\ttfamily,
  backgroundcolor=\color{{codebg}},
  keywordstyle=\color{{cyan}},
  breaklines=true,
  frame=single,
}}

\title{{{_latex_escape(title)}}}
\author{{{_latex_escape(authors)}}}
\date{{\today}}

\begin{{document}}
\maketitle
"""
    output.append(preamble)

    for line in lines:
        # Skip first h1 (title already set)
        if skip_title and line.startswith("# "):
            skip_title = False
            continue

        if line.startswith("```"):
            if in_code:
                output.append(r"\end{lstlisting}")
                in_code = False
            else:
                output.append(r"\begin{lstlisting}")
                in_code = True
            continue
        if in_code:
            output.append(line)
            continue

        if re.match(r"^#{1}\s", line):
            txt = line.lstrip("# ").strip()
            output.append(f"\n\\section{{{_latex_escape(txt)}}}")
        elif re.match(r"^#{2}\s", line):
            txt = re.sub(r"^#+\s+", "", line).strip()
            if txt.lower() == "abstract":
                output.append(r"\begin{abstract}")
                in_abstract = True
            else:
                if in_abstract:
                    output.append(r"\end{abstract}")
                    in_abstract = False
                output.append(f"\n\\section{{{_latex_escape(txt)}}}")
        elif re.match(r"^#{3}\s", line):
            txt = re.sub(r"^#+\s+", "", line).strip()
            output.append(f"\n\\subsection{{{_latex_escape(txt)}}}")
        elif re.match(r"^#{4}\s", line):
            txt = re.sub(r"^#+\s+", "", line).strip()
            output.append(f"\n\\subsubsection{{{_latex_escape(txt)}}}")
        elif line.startswith("|"):
            # Table — rough conversion
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.match(r"^[-:]+$", c) for c in cells if c):
                continue
            row = " & ".join(_latex_escape(c) for c in cells) + r" \\"
            output.append(row)
        elif re.match(r"^---+$", line):
            output.append(r"\hrule\vspace{6pt}")
        elif not line.strip():
            output.append("")
        else:
            # Inline formatting
            line = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", line)
            line = re.sub(r"\*(.+?)\*",     r"\\textit{\1}", line)
            line = re.sub(r"`(.+?)`",       r"\\texttt{\1}", line)
            line = re.sub(r"\[(.+?)\]\((.+?)\)",
                          r"\\href{\2}{\1}", line)
            output.append(_latex_escape_partial(line))

    if in_abstract:
        output.append(r"\end{abstract}")

    output.append(r"\end{document}")
    return "\n".join(output)


def _latex_escape(s: str) -> str:
    # Must escape backslash FIRST, then other special chars
    s = s.replace("\\", "\\textbackslash{}")
    for ch, rep in [
        ("&", "\\&"), ("%", "\\%"), ("$", "\\$"),
        ("#", "\\#"), ("_", "\\_"), ("{", "\\{"), ("}", "\\}"),
        ("~", "\\textasciitilde{}"), ("^", "\\textasciicircum{}"),
    ]:
        s = s.replace(ch, rep)
    return s


def _latex_escape_partial(s: str) -> str:
    """Escape LaTeX specials but preserve already-escaped commands."""
    s = s.replace("&", r"\&")
    s = s.replace("%", r"\%")
    return s


# ── PDF Generator ─────────────────────────────────────────────────────────────

class PDFPaperGenerator:
    """
    Converts the arXiv Markdown paper into PDF (via weasyprint)
    and LaTeX source for manual pdflatex compilation.
    """

    TITLE   = "NEXUS EXECUTIVE INCIDENT REPORT"
    AUTHORS = "NEXUS Autonomous Operations Center"
    VENUE   = "CLASSIFICATION: STRICTLY CONFIDENTIAL"

    def generate_pdf(self, markdown_path: str,
                     output_path: str = "data/research/nexus_paper.pdf") -> Optional[str]:
        """
        Read the Markdown paper and produce a styled PDF.
        Returns the output path on success, None on failure.
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        md = Path(markdown_path).read_text()

        # Keep all markdown since we already formatted the header in paper_generator
        body_md = md

        body_html = _md_to_html_body(body_md)
        ts        = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        full_html = _wrap_html(self.TITLE, self.AUTHORS, self.VENUE,
                               body_html, ts)

        # Save intermediate HTML
        html_path = output_path.replace(".pdf", ".html")
        Path(html_path).write_text(full_html, encoding="utf-8")

        # Generate PDF with fpdf2 using White Background and Space Grotesk
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
                import json, glob, os
                total_battles = 0
                campaigns = glob.glob("data/campaigns/campaign_*.json")
                if campaigns:
                    latest = max(campaigns, key=os.path.getctime)
                    with open(latest, 'r', encoding='utf-8') as rf:
                        camp_data = json.load(rf)
                    elo_table = camp_data.get("final_elo_table", [])
                    if elo_table:
                        total_battles = max([r.get("battles", 0) for r in elo_table])
                
                if total_battles == 0:
                    total_battles = 1377
                live_ops = len(glob.glob("data/reports/battle_*.json"))
                
                pdf.set_font("SpaceGrotesk", "B", 10)
                pdf.set_text_color(99, 102, 241) # Indigo
                pdf.cell(0, 8, f"DATABASE METRICS: {live_ops} LIVE OPERATIONS LOGGED", 0, 1)
                pdf.ln(5)
            except:
                pass
            
            # Parse simple markdown
            lines = body_md.split("\n")
            for line in lines:
                if line.startswith("# "): continue # Skip main title
                elif line.startswith("## "):
                    # Prevent orphaned headings by breaking page if too close to bottom
                    if pdf.get_y() > 240:
                        pdf.add_page()
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
                        pdf.ln(5)
                elif line.startswith("**"):
                    pdf.set_font("SpaceGrotesk", "B", 11)
                    pdf.set_text_color(15, 23, 42) # Slate 900
                    pdf.cell(0, 8, line.replace("**", "").strip(), 0, 1)
                elif line.startswith("---"):
                    pdf.set_draw_color(226, 232, 240)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(8)
                elif "|" in line and "---" in line:
                    continue # Completely skip the markdown separator rows
                elif "|" in line and "---" not in line:
                    cols = [c.strip() for c in line.split("|") if c.strip()]
                    if not cols: continue
                    pdf.set_font("SpaceGrotesk", "", 9)
                    pdf.set_text_color(15, 23, 42) # Darker text for tables
                    pdf.set_draw_color(226, 232, 240) # Slate border
                    pdf.set_fill_color(248, 250, 252) # Slate 50 background
                    
                    # Use strictly uniform column widths to prevent grid-shifting
                    col_widths = [190 / len(cols)] * len(cols)

                    for i, c in enumerate(cols):
                        pdf.cell(col_widths[i], 8, c, 1, 0, 'C', fill=True)
                    pdf.ln(8)
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

    def _pandoc_fallback(self, markdown_path: str, output_path: str) -> Optional[str]:
        """Use pandoc if weasyprint fails."""
        try:
            result = subprocess.run(
                ["pandoc", markdown_path, "-o", output_path,
                 "--pdf-engine=wkhtmltopdf",
                 f"--metadata=title:{self.TITLE}",
                 f"--metadata=author:{self.AUTHORS}"],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                print(f"[PDF] pandoc → {output_path}")
                return output_path
            print(f"[PDF] pandoc failed: {result.stderr[:200]}")
        except Exception as e:
            print(f"[PDF] pandoc unavailable: {e}")
        return None

    def generate_latex(self, markdown_path: str,
                       output_path: str = "data/research/nexus_paper.tex") -> str:
        """Convert Markdown → LaTeX .tex source."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        md    = Path(markdown_path).read_text()
        latex = _md_to_latex(md, self.TITLE, self.AUTHORS)
        Path(output_path).write_text(latex, encoding="utf-8")
        print(f"[LaTeX] Source → {output_path} ({len(latex)//1024}KB)")
        return output_path

    def compile_latex(self, tex_path: str) -> Optional[str]:
        """Attempt pdflatex compilation (requires texlive)."""
        out_dir = str(Path(tex_path).parent)
        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode",
                 f"-output-directory={out_dir}", tex_path],
                capture_output=True, text=True, timeout=60,
            )
            pdf_path = tex_path.replace(".tex", ".pdf")
            if Path(pdf_path).exists():
                size_kb = Path(pdf_path).stat().st_size // 1024
                print(f"[LaTeX] Compiled → {pdf_path} ({size_kb}KB)")
                return pdf_path
            print(f"[LaTeX] pdflatex failed:\n{result.stdout[-500:]}")
        except FileNotFoundError:
            print("[LaTeX] pdflatex not installed — .tex source available")
        except Exception as e:
            print(f"[LaTeX] compile error: {e}")
        return None

    def generate_all(self, markdown_path: str,
                     base_path: str = "data/research") -> dict:
        """Generate PDF + LaTeX in one call."""
        stem   = Path(markdown_path).stem
        result = {}

        # PDF via weasyprint
        pdf_path = f"{base_path}/{stem}.pdf"
        result["pdf"] = self.generate_pdf(markdown_path, pdf_path)

        # LaTeX source
        tex_path = f"{base_path}/{stem}.tex"
        result["latex"] = self.generate_latex(markdown_path, tex_path)

        # Try pdflatex compile
        compiled = self.compile_latex(tex_path)
        if compiled:
            result["latex_pdf"] = compiled

        return result
