import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Restore the marching ants CSS that worked perfectly before!
old_css = """/* Animate Plotly attack lines to literally GROW (laser beam effect) */
@keyframes draw-laser {
    0% {
        stroke-dashoffset: 800;
    }
    100% {
        stroke-dashoffset: 0;
    }
}
g.scatterlayer path.js-line[style*="dasharray"] {
    stroke-dasharray: 800 !important;
    animation: draw-laser 1.2s cubic-bezier(0.1, 0.9, 0.2, 1) forwards !important;
}"""

new_css = """/* Animate Plotly dashed lines (Attack Vectors) */
@keyframes dash-march {
    to {
        stroke-dashoffset: -100;
    }
}
g.scatterlayer path.js-line {
    animation: dash-march 3s linear infinite !important;
}"""

text = text.replace(old_css, new_css)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
