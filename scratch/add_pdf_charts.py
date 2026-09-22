import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Add a method to generate charts
chart_method = """    def generate_charts(self, campaign_record):
        try:
            import plotly.express as px
            import pandas as pd
            import os
            
            # ELO Chart
            elo_hist = campaign_record.elo_history if hasattr(campaign_record, 'elo_history') else []
            if elo_hist:
                df_elo = pd.DataFrame(elo_hist).reset_index().melt(id_vars=["index"], var_name="Agent", value_name="ELO")
                fig_elo = px.line(df_elo, x="index", y="ELO", color="Agent", title="Agent Intelligence (ELO) Co-Evolution Trajectory")
                fig_elo.update_layout(font_family="Space Grotesk", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_title="Simulation Time", yaxis_title="ELO Rating")
                fig_elo.write_image("data/research/elo_chart.png", scale=2)
                
            # MITRE Chart
            tech_stats = campaign_record.technique_stats if hasattr(campaign_record, 'technique_stats') else []
            if tech_stats:
                df_tech = pd.DataFrame(tech_stats)
                df_tech = df_tech[df_tech['uses'] > 10].sort_values("uses", ascending=False)
                fig_tech = px.bar(df_tech, x="technique", y=["detected", "evaded"], title="MITRE ATT&CK Effectiveness", barmode="stack", color_discrete_sequence=["#3b82f6", "#ef4444"])
                fig_tech.update_layout(font_family="Space Grotesk", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_title="ATT&CK Technique", yaxis_title="Total Usages")
                fig_tech.write_image("data/research/mitre_chart.png", scale=2)
                
        except Exception as e:
            print("Failed to generate charts:", e)

    def generate_paper(self,"""

text = text.replace("    def generate_paper(self,", chart_method)

# Inject the image tags into the markdown
old_sections = """            "\\n" + self.results(campaign_record),
            "\\n" + self.appendix_personas(campaign_record),
            "\\n" + self.appendix_sigma_log(campaign_record)"""

new_sections = """            "\\n" + self.results(campaign_record),
            "\\n## D. THREAT EVOLUTION VISUALIZATION\\n",
            "![ELO Chart](data/research/elo_chart.png)\\n",
            "![MITRE Chart](data/research/mitre_chart.png)\\n",
            "\\n" + self.appendix_personas(campaign_record),
            "\\n" + self.appendix_sigma_log(campaign_record)"""

text = text.replace(old_sections, new_sections)

# Also ensure generate_charts is called at the top of generate_paper
old_gen = """    def generate_paper(self, campaign_record,
                       output_path: str = "data/research/nexus_paper.md") -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)"""

new_gen = """    def generate_paper(self, campaign_record,
                       output_path: str = "data/research/nexus_paper.md") -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.generate_charts(campaign_record)"""

text = text.replace(old_gen, new_gen)

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)


with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Add image parsing to the PDF generator
old_parse = """                elif line.startswith("## "):
                    pdf.set_font("SpaceGrotesk-Bold", "", 14)
                    pdf.set_text_color(15, 23, 42) # Slate 900
                    pdf.cell(0, 10, line.replace("## ", ""), 0, 1)
                    pdf.ln(2)"""

new_parse = """                elif line.startswith("## "):
                    pdf.set_font("SpaceGrotesk-Bold", "", 14)
                    pdf.set_text_color(15, 23, 42) # Slate 900
                    pdf.cell(0, 10, line.replace("## ", ""), 0, 1)
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
