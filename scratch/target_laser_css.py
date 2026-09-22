import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Update the CSS to use the signature targeting and fix the topology line disappearance
old_css_block = """/* 1. Animate solid lines to shoot like a laser beam (including topology boot-up) */
@keyframes laser-shoot {
    0% { stroke-dasharray: 800; stroke-dashoffset: 800; }
    50% { stroke-dasharray: 800; stroke-dashoffset: 0; opacity: 1; }
    100% { stroke-dasharray: 800; stroke-dashoffset: 0; opacity: 0; }
}
g.scatterlayer path.js-line:not([style*="dasharray"]) {
    stroke-dasharray: 800;
    animation: laser-shoot 1.5s cubic-bezier(0.1, 0.9, 0.2, 1) forwards !important;
}

/* 2. Fade in the flowing data stream right as the laser hits */
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
        dash-march 1.2s linear infinite !important;
    opacity: 0;
}"""

new_css_block = """/* 1. Animate the laser lines (Signature: 1000px) */
@keyframes laser-shoot {
    0% { stroke-dasharray: 800; stroke-dashoffset: 800; }
    50% { stroke-dasharray: 800; stroke-dashoffset: 0; opacity: 1; }
    100% { stroke-dasharray: 800; stroke-dashoffset: 0; opacity: 0; }
}
g.scatterlayer path.js-line[style*="1000px"] {
    stroke-dasharray: 800 !important;
    animation: laser-shoot 1.5s cubic-bezier(0.1, 0.9, 0.2, 1) forwards !important;
}

/* 2. Animate the data stream flow (All other dashed lines) */
@keyframes dash-march {
    to { stroke-dashoffset: -100; }
}
@keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
}
g.scatterlayer path.js-line[style*="dasharray"]:not([style*="1000px"]) {
    animation: 
        fade-in 0.2s ease-out 0.6s forwards,
        dash-march 1.5s linear infinite !important;
    opacity: 0;
}"""

text = text.replace(old_css_block, new_css_block)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
