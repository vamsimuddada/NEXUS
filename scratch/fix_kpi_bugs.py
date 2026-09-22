import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Fix Defend Win Rate counting logic (it should count "success", not "failure")
old_outcome_logic = """if json.loads(line).get("event", {}).get("outcome") == "failure":"""
new_outcome_logic = """if json.loads(line).get("event", {}).get("outcome") == "success":"""
text = text.replace(old_outcome_logic, new_outcome_logic)

# 2. Remove the green trend tiles from the KPI cards
old_kpi_card_html = """      <div class="kpi-card" style="border-top-color: {color};">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
              <div class="kpi-title">{title}</div>
              <div style="color: {color}; opacity: 0.8; width: 20px; height: 20px;">{icon_svg}</div>
          </div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-trend">{trend}</div>
      </div>"""

new_kpi_card_html = """      <div class="kpi-card" style="border-top-color: {color};">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
              <div class="kpi-title">{title}</div>
              <div style="color: {color}; opacity: 0.8; width: 20px; height: 20px;">{icon_svg}</div>
          </div>
          <div class="kpi-value" style="margin-bottom: 12px;">{value}</div>
      </div>"""
      
text = text.replace(old_kpi_card_html, new_kpi_card_html)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
