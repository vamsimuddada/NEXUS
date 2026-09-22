import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

widget_css = """
/*  Widget Integration & Styling  */
[data-testid="stWidgetLabel"] p {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: #475569 !important;
    font-size: 0.95rem !important;
    letter-spacing: -0.2px !important;
}

[data-testid="stSelectbox"] > div > div {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
    color: #1e293b !important;
    box-shadow: 0 2px 4px rgba(15, 23, 42, 0.02) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: #3b82f6 !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1) !important;
}

/* Slider Customization */
[data-testid="stSlider"] > div > div > div > div {
    background: #3b82f6 !important;
}
[data-testid="stThumbValue"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    color: #2563eb !important;
}

/* Base button cleanup */
[data-testid="baseButton-secondary"] {
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
    background: #ffffff !important;
    color: #475569 !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
[data-testid="baseButton-secondary"]:hover {
    border-color: #94a3b8 !important;
    color: #1e293b !important;
    background: #f8fafc !important;
}

/* Primary Button Upgrade (Initiate Wargames) */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 20px -8px rgba(15, 23, 42, 0.8), inset 0 1px 0 rgba(255,255,255,0.1) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
[data-testid="baseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 25px -8px rgba(15, 23, 42, 0.9), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
}
[data-testid="baseButton-primary"]:active {
    transform: translateY(0px) !important;
}
"""

text = text.replace('</style>', widget_css + '\n</style>')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
