import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Replace the button logic in the left column
old_start_btn = """            if st.button("🚀 INITIATE WARGAMES", use_container_width=True):
                # Wipe the old logs so the dashboard only shows the current test
                try:
                    open("data/siem/nexus_events.ndjson", "w").close()
                    import sqlite3
                    with sqlite3.connect("data/simulation_results.db") as conn:
                        conn.execute("DELETE FROM simulation_results")
                except: pass
                st.session_state.running = True
                st.session_state.live_feed.append(f"Initializing campaign with {turns} turns...")
                msg_q = st.session_state.msg_queue
                def run_sim(q):
                    import subprocess
                    prov = "mock" if "Mock" in provider else "ollama"
                    cmd = [sys.executable, "scripts/run_simulation.py", "--provider", prov, "--turns", str(turns)]
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
                    for line in iter(process.stdout.readline, ""):
                        if line.strip(): q.put(line.strip())
                    process.stdout.close()
                    q.put("__DONE__")
                threading.Thread(target=run_sim, args=(msg_q,), daemon=True).start()
                st.rerun()"""

new_start_btn = """            if st.session_state.running:
                if st.button("🛑 HALT CAMPAIGN", use_container_width=True):
                    st.session_state.running = False
                    st.session_state.live_feed.append("=== SIMULATION ABORTED BY USER ===")
                    st.rerun()
            else:
                if st.button("🚀 START CAMPAIGN", use_container_width=True):
                    # Wipe the old logs so the dashboard only shows the current test
                    try:
                        open("data/siem/nexus_events.ndjson", "w").close()
                        import sqlite3
                        with sqlite3.connect("data/simulation_results.db") as conn:
                            conn.execute("DELETE FROM simulation_results")
                    except: pass
                    st.session_state.running = True
                    st.session_state.live_feed.append(f"Initializing campaign with {turns} turns...")
                    msg_q = st.session_state.msg_queue
                    def run_sim(q):
                        import subprocess
                        prov = "mock" if "Mock" in provider else "ollama"
                        cmd = [sys.executable, "scripts/run_simulation.py", "--provider", prov, "--turns", str(turns)]
                        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
                        for line in iter(process.stdout.readline, ""):
                            if line.strip(): q.put(line.strip())
                        process.stdout.close()
                        q.put("__DONE__")
                    threading.Thread(target=run_sim, args=(msg_q,), daemon=True).start()
                    st.rerun()"""

text = text.replace(old_start_btn, new_start_btn)


# 2. Refactor the right column (remove the separate halt button, update progress bar, and fix realtime reading)
old_right_col = """    with op_c2:
        if st.session_state.running:
            c1, c2 = st.columns([3, 1])
            with c2:
                if st.button(" HALT WARGAMES", use_container_width=True):
                    st.session_state.running = False
                    st.session_state.live_feed.append("=== SIMULATION ABORTED BY USER ===")
                    st.rerun()
            with c1:
                # Mock a progress bar based on feed length
                prog = min(len(st.session_state.live_feed) * 2, 95)
                st.progress(prog, text=" AI Simulation in Progress...")

            try:
                while True:
                    msg = st.session_state.msg_queue.get_nowait()
                    if msg == "__DONE__":
                        st.session_state.running = False
                        st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                        st.rerun()
                    else: st.session_state.live_feed.append(msg)
            except queue.Empty: pass
            if st.session_state.running: time.sleep(0.3); st.rerun()"""

new_right_col = """    with op_c2:
        if st.session_state.running:
            # Mock a progress bar based on feed length
            prog = min(len(st.session_state.live_feed) * 2, 95)
            st.progress(prog, text=f" AI Simulation in Progress... {prog}%")

            try:
                # Removed 'while True' to read one line at a time for realtime cinematic effect
                msg = st.session_state.msg_queue.get_nowait()
                if msg == "__DONE__":
                    st.session_state.running = False
                    st.session_state.live_feed.append("=== CAMPAIGN CONCLUDED ===")
                    st.rerun()
                else: 
                    st.session_state.live_feed.append(msg)
            except queue.Empty: pass
            
            if st.session_state.running: 
                time.sleep(0.05)
                st.rerun()"""

text = text.replace(old_right_col, new_right_col)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
