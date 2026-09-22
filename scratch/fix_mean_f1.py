import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix Mean F1 Score calculation
old_f1 = """        reports = glob.glob("data/reports/battle_*.json")
        if reports:
            total_battles = len(reports)
            latest = max(reports, key=os.path.getctime)
            with codecs.open(latest, 'r', 'utf-8') as rf:
                rep_data = json.load(rf)
            avg_f1 = rep_data.get("metrics", {}).get("f1_score", 0.0)"""

new_f1 = """        campaigns = glob.glob("data/campaigns/campaign_*.json")
        if campaigns:
            latest = max(campaigns, key=os.path.getctime)
            with codecs.open(latest, 'r', 'utf-8') as rf:
                camp_data = json.load(rf)
            f1_hist = camp_data.get("f1_history", [])
            if f1_hist:
                avg_f1 = sum(f1_hist) / len(f1_hist)
            total_battles = camp_data.get("battles_completed", 0)"""

text = text.replace(old_f1, new_f1)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
