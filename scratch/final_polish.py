import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Remove the weird rotating blue gradient from the KPI cards
text = re.sub(
    r'\.kpi-card::before\s*\{[^}]+\}\s*\.kpi-card:hover::before\s*\{\s*opacity:\s*1;\s*\}',
    '',
    text
)

# 2. Fix the Terminal Feed layout, remove double border, add title, and implement CSS-only auto-scroll!
old_feed_block = """        feed_html = "<div class='terminal-feed' style='background: white; border: 1px solid #e2e8f0; border-radius: 24px; padding: 24px; font-family: monospace; font-size: 0.85rem; line-height: 1.8; max-height: 450px; overflow-y: auto; color: #334155; height: 450px;'><div style='color:#0f172a;'>"
        if st.session_state.live_feed:
            for line in st.session_state.live_feed:
                if "Battle" in line or "WINNER" in line: feed_html += f"<div style='color:#f59e0b; font-weight:700;'>{line}</div>"
                elif "ATTACK" in line: feed_html += f"<div style='color:#ef4444;'>{line}</div>"
                elif "DETECT" in line or "SIGMA" in line: feed_html += f"<div style='color:#10b981;'>{line}</div>"
                else: feed_html += f"<div>{line}</div>"
        else: feed_html += "System standing by. No active campaigns."
        feed_html += "</div></div>"
        st.markdown(feed_html, unsafe_allow_html=True)"""

new_feed_block = """        with st.container(border=True):
            st.markdown('<h3 style="color:#0f172a; font-family:\\\'Space Grotesk\\\', sans-serif; margin-top:0px; margin-bottom:12px; font-weight:800; letter-spacing:-0.5px;">Live Terminal Feed</h3>', unsafe_allow_html=True)
            
            # CSS auto-scroll hack: use flex column-reverse and reverse the DOM!
            feed_html = "<div class='terminal-feed' style='display: flex; flex-direction: column-reverse; font-family: monospace; font-size: 0.85rem; line-height: 1.8; max-height: 380px; overflow-y: auto; color: #334155; height: 380px; padding-right: 10px;'><div style='display: flex; flex-direction: column;'>"
            
            if st.session_state.live_feed:
                for line in st.session_state.live_feed:
                    if "Battle" in line or "WINNER" in line: feed_html += f"<div style='color:#f59e0b; font-weight:700;'>{line}</div>"
                    elif "ATTACK" in line: feed_html += f"<div style='color:#ef4444;'>{line}</div>"
                    elif "DETECT" in line or "SIGMA" in line: feed_html += f"<div style='color:#10b981;'>{line}</div>"
                    else: feed_html += f"<div>{line}</div>"
            else: feed_html += "<div>System standing by. No active campaigns.</div>"
            
            feed_html += "</div></div>"
            st.markdown(feed_html, unsafe_allow_html=True)"""

text = text.replace(old_feed_block, new_feed_block)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
