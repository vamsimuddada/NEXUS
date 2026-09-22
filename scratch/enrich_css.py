import sys, re
with open('scripts/dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_css = r'''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700;800&display=swap');

html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; color: #1e293b !important; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Floating Holographic Orbs ── */
.ambient-orb {
    position: fixed; border-radius: 50%; filter: blur(90px); z-index: -1;
    animation: float 25s infinite ease-in-out alternate; opacity: 0.45;
    mix-blend-mode: multiply;
}
.orb-1 { top: -10%; left: -10%; width: 600px; height: 600px; background: linear-gradient(135deg, rgba(37, 99, 235, 0.4), rgba(139, 92, 246, 0.4)); animation-delay: 0s; }
.orb-2 { bottom: -20%; right: -10%; width: 700px; height: 700px; background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(236, 72, 153, 0.3)); animation-delay: -5s; }
.orb-3 { top: 30%; left: 50%; width: 500px; height: 500px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(56, 189, 248, 0.3)); animation-delay: -10s; }

@keyframes float {
    0% { transform: translate(0, 0) scale(1) rotate(0deg); }
    33% { transform: translate(60px, -60px) scale(1.1) rotate(45deg); }
    66% { transform: translate(-40px, 50px) scale(0.9) rotate(-45deg); }
    100% { transform: translate(0, 0) scale(1) rotate(0deg); }
}

/* ── Modern Mesh Blueprint Background ── */
[data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important;
    background-image: 
        radial-gradient(circle at 50% 0%, rgba(255,255,255,0.8) 0%, transparent 70%),
        linear-gradient(rgba(37, 99, 235, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(37, 99, 235, 0.04) 1px, transparent 1px) !important;
    background-size: 100% 100%, 40px 40px, 40px 40px !important;
    background-position: center center !important;
    animation: grid-move 40s linear infinite; position: relative; z-index: 1;
}
@keyframes grid-move { 100% { background-position: center center, 40px 40px, 40px 40px; } }

/* ── Staggered Fade Up ── */
@keyframes fadeUp {
    0% { opacity: 0; transform: translateY(40px) scale(0.97); filter: blur(12px); }
    100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
}
.stMarkdown, .stPlotlyChart, .stDataFrame, .stRadio, .stButton, [data-testid="stVerticalBlock"] > div {
    animation: fadeUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* ── Sidebar Glassmorphism ── */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.75) !important;
    backdrop-filter: blur(50px) saturate(200%);
    border-right: 1px solid rgba(255,255,255,1) !important;
    box-shadow: 15px 0 40px rgba(15, 23, 42, 0.04);
}
[data-testid="stSidebar"] * { color: #334155 !important; font-family: 'Inter', sans-serif !important; }

/* ── NEXUS Animated Branding ── */
.nexus-brand {
    font-size: 2.4rem; font-weight: 800; letter-spacing: -1.5px;
    background: linear-gradient(300deg, #2563eb, #8b5cf6, #ec4899, #2563eb);
    background-size: 300% 300%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: gradient-shift 8s ease infinite; font-family: 'Space Grotesk', sans-serif;
    filter: drop-shadow(0 8px 16px rgba(37, 99, 235, 0.25));
}
@keyframes gradient-shift { 50% { background-position: 100% 50%; } }

/* ── Sleek Navigation Pills ── */
.stRadio > div { gap: 14px; }
.stRadio label {
    color: #64748b !important; padding: 14px 22px; border-radius: 14px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer; font-weight: 600;
    border: 1px solid transparent; background: transparent;
}
.stRadio label:hover {
    background: rgba(255,255,255,1) !important; color: #0f172a !important;
    transform: translateX(8px); box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
    border: 1px solid rgba(255,255,255,1);
}
div[role="radiogroup"] label > div:first-child { display: none; }
div[role="radiogroup"] label[data-selected="true"] {
    background: #ffffff !important; color: #2563eb !important; font-weight: 700;
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.15); border-left: 5px solid #2563eb;
    border-radius: 6px 14px 14px 6px;
}

h1, h2, h3, h4, h5, h6, .stMarkdown p { color: #0f172a !important; }

/* ── Hero Header ── */
.hero-header {
    font-family: 'Space Grotesk', sans-serif; font-weight: 800; letter-spacing: -2px;
    font-size: 3.2rem; margin-bottom: 8px; background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; filter: drop-shadow(0 6px 15px rgba(37, 99, 235, 0.15));
}

/* ── Ultra Premium KPI Cards ── */
.kpi-card {
    background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(25px) saturate(150%); border-radius: 28px; padding: 32px;
    box-shadow: 0 15px 35px -10px rgba(15, 23, 42, 0.06), inset 0 2px 0 rgba(255,255,255,1);
    display: flex; flex-direction: column; border: 1px solid rgba(255, 255, 255, 1);
    transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1); margin-bottom: 24px; position: relative; overflow: hidden;
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.kpi-card::before {
    content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: conic-gradient(from 0deg, transparent 0%, rgba(56, 189, 248, 0.5) 25%, transparent 50%);
    animation: spin 5s linear infinite; z-index: -1; opacity: 0; transition: opacity 0.6s ease;
}
.kpi-card:hover::before { opacity: 1; }
@keyframes spin { 100% { transform: rotate(360deg); } }
.kpi-card:hover {
    transform: translateY(-10px) scale(1.02); 
    box-shadow: 0 35px 60px -15px rgba(37, 99, 235, 0.15), 0 0 20px rgba(56, 189, 248, 0.1), inset 0 2px 0 rgba(255,255,255,1);
    border-color: rgba(255,255,255,1);
}
.kpi-title { font-family: 'Space Grotesk', sans-serif; font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 2.5px; font-weight: 800; margin-bottom: 14px; }
.kpi-value { font-family: 'Space Grotesk', sans-serif; font-size: 3.4rem; color: #0f172a; font-weight: 800; letter-spacing: -2px; line-height: 1; background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; filter: drop-shadow(0 4px 6px rgba(37, 99, 235, 0.1)); }
.kpi-trend { font-size: 0.95rem; color: #10b981; font-weight: 700; margin-top: 20px; display: flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.1); padding: 8px 16px; border-radius: 24px; width: fit-content; box-shadow: inset 0 1px 0 rgba(255,255,255,0.8); }

/* ── Native Streamlit Containers (Enriched Panels) ── */
[data-testid="stVerticalBlock"] > [style*="border"] {
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(30px) saturate(150%) !important;
    border-radius: 28px !important;
    border: 1px solid rgba(255, 255, 255, 1) !important;
    box-shadow: 0 15px 40px -10px rgba(15, 23, 42, 0.06), inset 0 2px 0 rgba(255,255,255,1) !important;
    padding: 32px !important;
    transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
[data-testid="stVerticalBlock"] > [style*="border"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 25px 50px -15px rgba(37, 99, 235, 0.12), inset 0 2px 0 rgba(255,255,255,1) !important;
}

/* ── Premium Cyber Buttons ── */
.stButton > button {
    border-radius: 16px !important; font-weight: 800 !important; letter-spacing: 1px !important;
    background: linear-gradient(135deg, #0f172a, #1e293b) !important; color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important; padding: 20px 40px !important;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.4), inset 0 2px 0 rgba(255,255,255,0.2) !important;
    transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) !important; text-transform: uppercase;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1e293b, #3b82f6) !important;
    box-shadow: 0 15px 35px -5px rgba(37, 99, 235, 0.5), inset 0 2px 0 rgba(255,255,255,0.3) !important;
    transform: translateY(-5px) scale(1.03) !important;
}

/* ── Event Feed ── */
.event-feed {
    font-family: 'JetBrains Mono', 'Roboto Mono', monospace; font-size: 0.9rem; line-height: 2; height: 500px; overflow-y: auto;
    background: rgba(255, 255, 255, 0.7); padding: 32px; border-radius: 24px; border: 1px solid rgba(226, 232, 240, 0.8);
    box-shadow: inset 0 4px 15px rgba(15, 23, 42, 0.04); color: #1e293b;
}
.event-feed::-webkit-scrollbar { width: 8px; }
.event-feed::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.5); border-radius: 10px; }
.event-feed::-webkit-scrollbar-thumb:hover { background: rgba(100, 116, 139, 0.8); }

/* ── Status Dots ── */
.status-dot {
    height: 10px; width: 10px; background-color: #10b981; border-radius: 50%; display: inline-block; position: relative; box-shadow: 0 0 15px rgba(16,185,129,0.8);
}
.status-dot::after {
    content: ''; position: absolute; top: -6px; left: -6px; right: -6px; bottom: -6px;
    border: 2px solid #10b981; border-radius: 50%; animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse { 100% { transform: scale(2.5); opacity: 0; } }
</style>'''

content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)

with open('scripts/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)
