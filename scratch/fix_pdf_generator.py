import codecs

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Modify PDFPaperGenerator title and strip logic
old_title_block = """    TITLE   = ("NEXUS: Adversarial Co-Evolution Between LLM Attacker Swarms "
                "and Self-Modifying SOC Detection Systems")
    AUTHORS = "NEXUS Research Team"
    VENUE   = "arXiv preprint (submitted)\""""
new_title_block = """    TITLE   = "NEXUS EXECUTIVE INCIDENT REPORT"
    AUTHORS = "NEXUS Autonomous Operations Center"
    VENUE   = "CLASSIFICATION: STRICTLY CONFIDENTIAL\""""
text = text.replace(old_title_block, new_title_block)

old_strip_logic = """        # Strip the Markdown front-matter (title/author/venue lines)
        body_start = md.find("\\n## Abstract")
        if body_start == -1:
            body_start = md.find("\\n## 1.")
        body_md = md[body_start:].strip() if body_start > 0 else md"""
new_strip_logic = """        # Keep all markdown since we already formatted the header in paper_generator
        body_md = md"""
text = text.replace(old_strip_logic, new_strip_logic)

# Make the PDF CSS look professional (Slate / Space Grotesk) instead of academic
old_css_marker = "font-family: 'Georgia', serif;"
new_css = """
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
"""
if "Georgia" in text:
    text = text.replace("font-family: 'Georgia', serif;", "") # Just strip it and replace full block
    text = text.replace("body {", new_css + "\n/* body {")

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)
