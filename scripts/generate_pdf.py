import glob
import json
import os
from datetime import datetime
from fpdf import FPDF

class NexusPDF(FPDF):
    def header(self):
        # Add extra top margin
        if self.page_no() == 1:
            self.ln(10)
            self.set_font('SpaceGrotesk', 'B', 24)
            self.set_text_color(15, 23, 42)
            self.cell(0, 12, 'NEXUS EXECUTIVE REPORT', border=False, ln=True, align='L')
            
            # Draw a sleek horizontal line under the title
            self.set_draw_color(226, 232, 240)
            self.set_line_width(0.5)
            self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
            self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font('SpaceGrotesk', '', 9)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'PAGE {self.page_no()}', 0, 0, 'C')
        
    def section_title(self, title):
        self.ln(8)
        self.set_font('SpaceGrotesk', 'B', 16)
        self.set_text_color(15, 23, 42)
        self.cell(0, 10, title, ln=True)
        self.ln(3)
        
    def body_text(self, text):
        self.set_font('SpaceGrotesk', '', 10)
        self.set_text_color(71, 85, 105)
        # Using a line height of 6 for airy, modern paragraph spacing
        self.multi_cell(0, 6, text)
        self.ln(4)

MITRE_MAP = {
    "T1071": "App Layer Protocol",
    "T1021": "Remote Services",
    "T1078": "Valid Accounts",
    "T1486": "Ransomware / Encrypt",
    "T1003": "Credential Dumping",
    "T1083": "File Discovery",
    "T1059": "CLI Scripting",
    "T1055": "Process Injection",
    "T1566": "Phishing",
    "T1190": "Public App Exploit",
    "T1110": "Brute Force"
}

def build_live_report():
    files = sorted(glob.glob('data/reports/*.json'), key=os.path.getmtime)
    target_files = files[-10:] if len(files) >= 10 else files
    
    # -- GATHER ALL STATS FIRST --
    total_attacks = 0
    tactic_stats = {}
    op_metrics = []
    
    for i, file in enumerate(target_files):
        with open(file, 'r') as f:
            try:
                data = json.load(f)
                battle_id = data.get('battle_id', f'Op {i+1}')
                m = data.get('metrics', {})
                f1 = m.get('f1_score', 0.0)
                prec = m.get('precision', 0.0)
                rec = m.get('recall', 0.0)
                sigma = m.get('sigma_rules', 10)
                
                logs = data.get('attacker_logs', [])
                num_attacks = len(logs)
                total_attacks += num_attacks
                
                op_metrics.append({
                    'op': f"Op {battle_id[:8]}", 'f1': f1, 'prec': prec, 'rec': rec, 
                    'attacks': num_attacks, 'sigma': sigma,
                    'winner': data.get('winner', 'Unknown')
                })
                
                for log in logs:
                    tech = log.get('attack_technique') or log.get('technique')
                    if tech:
                        if tech not in tactic_stats:
                            tactic_stats[tech] = {'uses': 0, 'evaded': 0}
                        tactic_stats[tech]['uses'] += 1
                        det = log.get('detected', False)
                        if str(det).lower() != 'true':
                            tactic_stats[tech]['evaded'] += 1
            except Exception:
                pass

    top_tech = "None"
    if tactic_stats:
        top_tech = sorted(tactic_stats.items(), key=lambda x: x[1]['uses'], reverse=True)[0][0]
        
    start_rules = op_metrics[0]['sigma'] if op_metrics else 10
    end_rules = op_metrics[-1]['sigma'] if op_metrics else 10
    new_rules = max(0, end_rules - start_rules)
    
    # -- BUILD PDF --
    pdf = NexusPDF()
    # Register Space Grotesk fonts
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_reg = os.path.join(base_dir, 'assets', 'fonts', 'SpaceGrotesk-Regular.ttf')
    font_bold = os.path.join(base_dir, 'assets', 'fonts', 'SpaceGrotesk-Bold.ttf')
    
    pdf.add_font('SpaceGrotesk', '', font_reg)
    pdf.add_font('SpaceGrotesk', 'B', font_bold)
    
    pdf.set_margins(left=15, top=15, right=15)
    pdf.add_page()
    
    # Top metadata
    pdf.set_font('SpaceGrotesk', 'B', 10)
    pdf.set_text_color(37, 99, 235) # Premium blue
    pdf.cell(0, 6, f'DATABASE METRICS: {len(target_files)} LIVE OPERATIONS LOGGED', ln=True)
    pdf.ln(2)
    
    pdf.set_font('SpaceGrotesk', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    report_id = target_files[-1].split('_')[-1].replace('.json', '') if target_files else "Unknown"
    pdf.cell(0, 6, f'Report ID: {report_id}', ln=True)
    pdf.cell(0, 6, f'Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}', ln=True)
    pdf.cell(0, 6, 'Classification: STRICTLY CONFIDENTIAL', ln=True)
    pdf.ln(6)
    
    # Executive Summary
    pdf.section_title('Executive Summary')
    pdf.body_text('This document serves as an automated post-action report following a simulated cyber warfare campaign. The following data details the adversarial threat exposure, Blue Team SIEM detection rates, and active mitigation performance.')
    
    # 1. Project Overview & Architecture
    pdf.section_title('1. Project Overview & Architecture')
    pdf.body_text('NEXUS (Neural Exploitation and eXplainable Unified Security) is a strictly isolated, autonomous cyber-warfare simulation matrix. The platform pits an ensemble of highly specialized, LLM-driven adversarial agents against a self-evolving SOC (Security Operations Center). The SOC combines dynamic SIGMA rule generation, graph-neural-network anomaly detection, and active threat mitigation protocols. This intelligence report details the co-evolutionary adaptation of both offensive and defensive systems over the course of the simulation.')
    
    # 2. Tactical Deployment Details
    pdf.section_title('2. Tactical Deployment Details')
    pdf.body_text(f"The simulation stress-tested the defensive architecture across {len(target_files)} manual tactical engagements, simulating thousands of distinct behavioral artifacts. In total, the adversarial Red Team deployed MITRE ATT&CK techniques {total_attacks} times. The most heavily utilized operational vector was technique {top_tech} ({MITRE_MAP.get(top_tech, 'Unknown')}), demonstrating the attackers' preference for exploiting structural vulnerabilities in the simulated enterprise environment. The following telemetry data rigorously quantifies the exact effectiveness of these tactical deployments.")
    
    # 3. Recent Agent Performance
    if pdf.get_y() > 220:
        pdf.add_page()
        
    pdf.section_title('3. Recent Agent Performance (TELEMETRY EXTRACTS)')
    pdf.body_text('This table details detection performance for the most recent operations with full JSON telemetry exports.')
    
    # Table 1 - Agent Performance
    def draw_perf_header():
        pdf.set_draw_color(203, 213, 225)
        pdf.set_line_width(0.3)
        pdf.set_fill_color(248, 250, 252)
        pdf.set_font('SpaceGrotesk', 'B', 10)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(40, 10, 'Operation', border='B', fill=True, align='C')
        pdf.cell(30, 10, 'F1 Score', border='B', fill=True, align='C')
        pdf.cell(30, 10, 'Precision', border='B', fill=True, align='C')
        pdf.cell(30, 10, 'Recall', border='B', fill=True, align='C')
        pdf.cell(50, 10, 'Outcome (Winner)', border='B', fill=True, align='C')
        pdf.ln()

    draw_perf_header()
    
    pdf.set_font('SpaceGrotesk', '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.set_fill_color(255, 255, 255)
    
    for op in op_metrics:
        if pdf.get_y() > 260:
            pdf.add_page()
            draw_perf_header()
            pdf.set_font('SpaceGrotesk', '', 10)
            pdf.set_text_color(71, 85, 105)
            pdf.set_fill_color(255, 255, 255)
            
        pdf.cell(40, 10, str(op['op']), border='B', fill=True, align='C')
        pdf.cell(30, 10, f"{op['f1']:.2f}", border='B', fill=True, align='C')
        pdf.cell(30, 10, f"{op['prec']:.2f}", border='B', fill=True, align='C')
        pdf.cell(30, 10, f"{op['rec']:.2f}", border='B', fill=True, align='C')
        
        # Color code the winner for better context
        winner_text = str(op.get('winner', 'Unknown')).upper()
        if winner_text == 'DEFENDER':
            pdf.set_text_color(16, 185, 129) # Emerald green
        elif winner_text == 'ATTACKER':
            pdf.set_text_color(239, 68, 68) # Red
        else:
            pdf.set_text_color(71, 85, 105)
            
        pdf.cell(50, 10, winner_text, border='B', fill=True, align='C')
        pdf.set_text_color(71, 85, 105) # Reset text color
        pdf.ln()
        
    pdf.ln(8)
    
    # 4. MITRE ATT&CK
    if pdf.get_y() > 220:
        pdf.add_page()
        
    pdf.section_title('4. MITRE ATT&CK Tactic Effectiveness')
    
    # Table 2 - MITRE Effectiveness
    def draw_mitre_header():
        pdf.set_fill_color(248, 250, 252)
        pdf.set_font('SpaceGrotesk', 'B', 10)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(60, 10, 'Technique', border='B', fill=True, align='L')
        pdf.cell(30, 10, 'Uses', border='B', fill=True, align='C')
        pdf.cell(30, 10, 'Evaded', border='B', fill=True, align='C')
        pdf.cell(30, 10, 'Evasion Rate', border='B', fill=True, align='C')
        pdf.cell(30, 10, 'Detection Rate', border='B', fill=True, align='C')
        pdf.ln()

    draw_mitre_header()
    
    pdf.set_font('SpaceGrotesk', '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.set_fill_color(255, 255, 255)
    
    sorted_tactics = sorted(tactic_stats.items(), key=lambda x: x[1]['uses'], reverse=True)
    for tech, stats in sorted_tactics:
        if pdf.get_y() > 260:
            pdf.add_page()
            draw_mitre_header()
            pdf.set_font('SpaceGrotesk', '', 10)
            pdf.set_text_color(71, 85, 105)
            pdf.set_fill_color(255, 255, 255)
            
        uses = stats['uses']
        evaded = stats['evaded']
        evasion_rate = (evaded / uses) * 100 if uses > 0 else 0
        det_rate = 100 - evasion_rate
        
        tech_name = MITRE_MAP.get(tech, 'Unknown')
        display_tech = f"{tech} ({tech_name})"
        
        pdf.cell(60, 10, display_tech, border='B', fill=True, align='L')
        pdf.cell(30, 10, str(uses), border='B', fill=True, align='C')
        pdf.cell(30, 10, str(evaded), border='B', fill=True, align='C')
        pdf.cell(30, 10, f"{evasion_rate:.1f}%", border='B', fill=True, align='C')
        pdf.cell(30, 10, f"{det_rate:.1f}%", border='B', fill=True, align='C')
        pdf.ln()
        
    pdf.ln(8)
    
    # 5. SIGMA Rule Evolution Log
    if pdf.get_y() > 240:
        pdf.add_page()
    pdf.section_title('5. SIGMA Rule Evolution Log')
    pdf.body_text(f"The Evolution Engine actively synthesizes new SIGMA detection rules in response to zero-day adversarial behaviors. The campaign started with {start_rules} baseline rules and concluded with {end_rules} active rules, representing the autonomous generation of {new_rules} new behavioral heuristic(s) over the course of the live operations.")
    
    pdf.set_font('SpaceGrotesk', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, "Rule count per operation:", ln=True)
    pdf.set_font('SpaceGrotesk', '', 10)
    pdf.set_text_color(71, 85, 105)
    
    for i, op in enumerate(op_metrics):
        pdf.cell(0, 8, f"- Operation {i+1}: {op['sigma']} rules", ln=True)
        
    return bytes(pdf.output())
