import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

bad_slider = """/* Slider Customization */
[data-testid="stSlider"] > div > div > div > div {
    background: #3b82f6 !important;
}"""

good_slider = """/* Slider Customization */"""

text = text.replace(bad_slider, good_slider)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
