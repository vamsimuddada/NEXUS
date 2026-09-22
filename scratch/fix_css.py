import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    code = f.read()

professional_css = """
/* 🌟🌟 Floating Holographic Orbs (Professional) 🌟🌟 */
.ambient-orb {
    position: fixed; border-radius: 50%; filter: blur(100px); z-index: -1;
    animation: drift 40s infinite ease-in-out alternate; opacity: 0.25;
    mix-blend-mode: multiply;
}
.orb-1 { top: -10%; left: -10%; width: 600px; height: 600px; background: linear-gradient(135deg, rgba(37, 99, 235, 0.3), rgba(139, 92, 246, 0.2)); animation-delay: 0s; }
.orb-2 { bottom: -20%; right: -10%; width: 700px; height: 700px; background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(236, 72, 153, 0.2)); animation-delay: -10s; }
.orb-3 { top: 30%; left: 50%; width: 500px; height: 500px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(56, 189, 248, 0.2)); animation-delay: -20s; }

@keyframes drift {
    0% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(30px, -30px) scale(1.05); }
    100% { transform: translate(-20px, 20px) scale(0.95); }
}

/* 🌟🌟 Modern Mesh Blueprint Background 🌟🌟 */
[data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important;
    background-image: 
        radial-gradient(circle at 50% 0%, rgba(255,255,255,0.8) 0%, transparent 70%),
        linear-gradient(rgba(37, 99, 235, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(37, 99, 235, 0.03) 1px, transparent 1px) !important;
    background-size: 100% 100%, 40px 40px, 40px 40px !important;
    background-position: center center !important;
    animation: grid-drift 120s linear infinite; position: relative; z-index: 1;
}
@keyframes grid-drift { 100% { background-position: center center, 40px 40px, 40px 40px; } }

/* 🌟🌟 Staggered Fade Up (Sleek) 🌟🌟 */
@keyframes fadeUp {
    0% { opacity: 0; transform: translateY(20px); filter: blur(4px); }
    100% { opacity: 1; transform: translateY(0); filter: blur(0); }
}
.stMarkdown, .stPlotlyChart, .stDataFrame, .stRadio, .stButton, [data-testid="stVerticalBlock"] > div {
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

"""

# Insert it before [data-testid="stSidebar"]
code = code.replace('[data-testid="stSidebar"] {\n    background: linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.7) 100%) !important;', professional_css + '[data-testid="stSidebar"] {\n    background: linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.7) 100%) !important;')

kpi_hover_new = """.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px -10px rgba(15, 23, 42, 0.08), inset 0 2px 0 rgba(255,255,255,1);
    border-color: rgba(37, 99, 235, 0.1);
}"""

# Replace the spinning border effect with a sleek hover lift
code = re.sub(r'\.kpi-card::before\s*{[^}]*}\s*\.kpi-card:hover::before\s*{[^}]*}\s*@keyframes spin\s*{[^}]*}', kpi_hover_new, code, flags=re.DOTALL)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(code)
