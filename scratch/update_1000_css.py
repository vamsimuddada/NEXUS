import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

old_css_block = """/* 1. Animate the laser lines using the bulletproof legendgroup class target! */
@keyframes laser-shoot {
    0% { stroke-dasharray: 800; stroke-dashoffset: 800; }
    50% { stroke-dasharray: 800; stroke-dashoffset: 0; opacity: 1; }
    100% { stroke-dasharray: 800; stroke-dashoffset: 0; opacity: 0; }
}
g.legendgroup-laser path.js-line {
    stroke-dasharray: 800 !important;
    animation: laser-shoot 1.5s cubic-bezier(0.1, 0.9, 0.2, 1) forwards !important;
}

/* 2. Animate the data stream flow (All dashed lines) */
@keyframes dash-march {
    to { stroke-dashoffset: -100; }
}
@keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
}
g.scatterlayer path.js-line[style*="dasharray"] {
    animation: 
        fade-in 0.2s ease-out 0.6s forwards,
        dash-march 1.5s linear infinite !important;
    opacity: 0;
}"""

new_css_block = """/* 1. Animate the laser lines (Signature: 1000px without 'px' suffix to bypass Plotly DOM stripping) */
@keyframes laser-shoot {
    0% { stroke-dasharray: 800 !important; stroke-dashoffset: 800; }
    50% { stroke-dasharray: 800 !important; stroke-dashoffset: 0; opacity: 1; }
    100% { stroke-dasharray: 800 !important; stroke-dashoffset: 0; opacity: 0; }
}
g.scatterlayer path.js-line[style*="1000"] {
    stroke-dasharray: 800 !important;
    animation: laser-shoot 1.5s cubic-bezier(0.1, 0.9, 0.2, 1) forwards !important;
}

/* 2. Animate the data stream flow (All dashed lines EXCEPT the 1000 signature) */
@keyframes dash-march {
    to { stroke-dashoffset: -100; }
}
@keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
}
g.scatterlayer path.js-line[style*="dasharray"]:not([style*="1000"]) {
    animation: 
        fade-in 0.2s ease-out 0.6s forwards,
        dash-march 1.5s linear infinite !important;
    opacity: 0;
}"""

text = text.replace(old_css_block, new_css_block)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
