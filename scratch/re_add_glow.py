import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Add the beautiful rotating glow effect back, but fix the geometry bug!
css_injection = """
.kpi-card {
    background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(25px) saturate(150%); border-radius: 24px; padding: 22px;
    box-shadow: 0 15px 35px -10px rgba(15, 23, 42, 0.06), inset 0 2px 0 rgba(255,255,255,1);
    display: flex; flex-direction: column; border: 1px solid rgba(255, 255, 255, 1);
    transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1); margin-bottom: 24px; position: relative; overflow: hidden;
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.kpi-card::before {
    content: ''; position: absolute; top: 50%; left: 50%; 
    width: 800px; height: 800px; /* FIXED GEOMETRY: Must be a perfect square, otherwise gradient stretches into a rectangle! */
    background: conic-gradient(from 0deg, transparent 0%, rgba(56, 189, 248, 0.4) 20%, transparent 40%);
    animation: spin-glow 5s linear infinite; z-index: -1; opacity: 0; transition: opacity 0.6s ease;
    pointer-events: none;
}
.kpi-card:hover::before { opacity: 1; }
@keyframes spin-glow { 
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
}
.kpi-card:hover {
"""

text = text.replace(
    ".kpi-card {\n    background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(25px) saturate(150%); border-radius: 24px; padding: 22px;\n    box-shadow: 0 15px 35px -10px rgba(15, 23, 42, 0.06), inset 0 2px 0 rgba(255,255,255,1);\n    display: flex; flex-direction: column; border: 1px solid rgba(255, 255, 255, 1);\n    transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1); margin-bottom: 24px; position: relative; overflow: hidden;\n    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;\n}\n.kpi-card:hover {",
    css_injection
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
