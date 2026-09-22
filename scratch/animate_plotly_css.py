import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Inject the SVG CSS animation right before </style>
css_injection = """
/* Animate Plotly dashed lines (Attack Vectors) */
@keyframes dash-march {
    to {
        stroke-dashoffset: -100;
    }
}
g.scatterlayer path.js-line {
    animation: dash-march 3s linear infinite !important;
}
</style>"""

text = text.replace("</style>", css_injection, 1)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
