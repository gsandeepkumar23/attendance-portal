import streamlit as st
import json
import bcrypt
import csv
import os
from datetime import datetime
import pytz
import pandas as pd

# ---------- CONFIG ----------
IST = pytz.timezone('Asia/Kolkata')
LOG_FILE = "logs.csv"
USER_FILE = "users.json"
SESSION_FILE = "sessions.json"

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="OneStepB | Attendance Portal",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- SESSION DEFAULTS ----------
defaults = {
    "logged_in": False,
    "username": None,
    "login_time": None,
    "role": None,
    "page": "Home"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------- GLOBAL CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --accent: #4f8ef7;
    --accent2: #7c3aed;
    --success: #22c55e;
    --danger: #ef4444;
    --text-primary: #f0f4ff;
    --text-secondary: #8892aa;
    --bg-card: rgba(19, 22, 30, 0.96);
    --bg-card2: rgba(26, 30, 40, 0.98);
    --border: rgba(79, 142, 247, 0.18);
    --border-hover: rgba(79, 142, 247, 0.45);
    --glow: rgba(79, 142, 247, 0.22);
}

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif !important;
    color: var(--text-primary) !important;
}

/* Clean gradient background — no image */
.stApp {
    background: linear-gradient(135deg, #0d0f14 0%, #111520 40%, #0e1018 100%) !important;
    min-height: 100vh;
}

header, #MainMenu, footer { display: none !important; }
.block-container { padding: 2rem 2.5rem 5rem !important; max-width: 1200px; }

section[data-testid="stSidebar"] {
    background: rgba(10, 12, 18, 0.98) !important;
    border-right: 1px solid var(--border) !important;
    backdrop-filter: blur(12px);
}
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* Nav buttons */
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    text-align: left !important;
    font-weight: 400 !important;
    font-size: 0.88rem !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(79,142,247,0.10) !important;
    border-color: var(--border-hover) !important;
    color: var(--text-primary) !important;
}
.nav-active button {
    background: rgba(79,142,247,0.15) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
}
.logout-wrap button {
    background: rgba(239,68,68,0.10) !important;
    border-color: rgba(239,68,68,0.28) !important;
    color: #f87171 !important;
}
.logout-wrap button:hover {
    background: rgba(239,68,68,0.20) !important;
    border-color: #ef4444 !important;
    color: #fca5a5 !important;
}

/* Main buttons */
.stButton button {
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.4rem !important;
    border: none !important;
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    width: 100%;
    transition: all 0.2s !important;
}
.stButton button:hover {
    opacity: 0.88;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px var(--glow) !important;
}

input, textarea {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Sora', sans-serif !important;
    transition: border 0.2s, box-shadow 0.2s !important;
}
input:focus, textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow) !important;
    outline: none !important;
}
label { color: var(--text-secondary) !important; font-size: 0.82rem !important; }

div[data-testid="stSelectbox"] > div > div {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

div[data-testid="stTabs"] button {
    font-family: 'Sora', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 0.55rem 1.4rem !important;
    background: transparent !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: rgba(79,142,247,0.06) !important;
}
div[data-testid="stTabContent"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 14px 14px !important;
    padding: 1.8rem !important;
    backdrop-filter: blur(10px);
}

.stDataFrame { border-radius: 14px !important; overflow: hidden !important; }

div[data-testid="stAlert"] {
    border-radius: 12px !important;
    background: rgba(79,142,247,0.08) !important;
    border-left: 3px solid var(--accent) !important;
    color: var(--text-primary) !important;
}

.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    backdrop-filter: blur(10px);
    transition: border-color 0.2s, box-shadow 0.2s;
    margin-bottom: 0.5rem;
}
.metric-card:hover { border-color: var(--border-hover); box-shadow: 0 0 24px var(--glow); }
.metric-card .label { font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 0.5rem; }
.metric-card .value { font-size: 2rem; font-weight: 700; line-height: 1; }
.metric-card .sub { font-size: 0.76rem; color: var(--text-secondary); margin-top: 0.4rem; }

.action-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.6rem;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: border-color 0.2s, box-shadow 0.2s;
}
.action-card:hover { border-color: var(--border-hover); box-shadow: 0 0 24px var(--glow); }
.action-card .icon { font-size: 2rem; margin-bottom: 0.5rem; }
.action-card .action-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 0.3rem; }
.action-card .action-sub { font-size: 0.75rem; color: var(--text-secondary); }

.section-header {
    font-size: 1.25rem; font-weight: 600;
    margin-bottom: 1.4rem; padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
}

.role-badge {
    display: inline-block; padding: 0.18rem 0.65rem;
    border-radius: 20px; font-size: 0.70rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.07em;
}
.badge-admin { background: rgba(124,58,237,0.18); color: #a78bfa; border: 1px solid rgba(124,58,237,0.3); }
.badge-employee { background: rgba(79,142,247,0.15); color: #7eb3f9; border: 1px solid rgba(79,142,247,0.25); }
.badge-intern { background: rgba(34,197,94,0.13); color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }

.login-wrap {
    max-width: 420px; margin: 5vh auto 0;
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 24px; padding: 2.6rem 2.4rem 2.2rem;
    box-shadow: 0 24px 64px rgba(0,0,0,0.55);
    backdrop-filter: blur(20px);
}
.login-title { text-align: center; margin-bottom: 1.8rem; }
.login-title h2 {
    font-size: 1.75rem; font-weight: 700; margin: 0 0 0.3rem;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.login-title p { color: var(--text-secondary); font-size: 0.82rem; margin: 0; }

.footer-bar {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: rgba(10,12,18,0.97); border-top: 1px solid var(--border);
    text-align: center; padding: 0.55rem;
    font-size: 0.73rem; color: var(--text-secondary);
    z-index: 999; backdrop-filter: blur(8px);
}

.status-active {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(34,197,94,0.12); border: 1px solid rgba(34,197,94,0.3);
    color: #4ade80; border-radius: 20px; padding: 0.3rem 0.8rem;
    font-size: 0.78rem; font-weight: 600;
}
.status-inactive {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(239,68,68,0.10); border: 1px solid rgba(239,68,68,0.25);
    color: #f87171; border-radius: 20px; padding: 0.3rem 0.8rem;
    font-size: 0.78rem; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------- INIT FILES ----------
def init_files():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow(["username", "date", "login_time", "logout_time", "duration_hours"])
    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w") as f:
            json.dump({}, f)

init_files()

# ---------- HELPERS ----------
def get_time():
    return datetime.now(IST)

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)["users"]

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump({"users": users}, f, indent=4)

def load_sessions():
    with open(SESSION_FILE, "r") as f:
        return json.load(f)

def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=4)

def authenticate(username, password):
    for user in load_users():
        if user["username"] == username:
            try:
                if bcrypt.checkpw(password.encode(), user["password"].encode()):
                    return user
            except Exception:
                return None
    return None

def write_log(username, login_time, logout_time):
    duration = (logout_time - login_time).total_seconds() / 3600
    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([
            username, login_time.strftime("%Y-%m-%d"),
            login_time.strftime("%H:%M:%S"), logout_time.strftime("%H:%M:%S"),
            round(duration, 2)
        ])

def role_badge(role):
    safe = (role or "intern").strip().lower()
    cls = f"badge-{safe}" if safe in ["admin", "employee", "intern"] else "badge-intern"
    return f'<span class="role-badge {cls}">{safe}</span>'

# ============================================================
# SIGN IN PAGE
# ============================================================
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div class="login-wrap">
            <div class="login-title">
                <h2>🏢 OneStepB</h2>
                <p>Attendance Portal — Sign in to continue</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        if st.button("Sign In  →", use_container_width=True):
            user = authenticate(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.login_time = None   # user must click Login on Home
                st.session_state.role = user.get("role", "intern").strip().lower()
                st.session_state.page = "Home"
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

# ============================================================
# MAIN APP
# ============================================================
else:
    role = (st.session_state.role or "").strip().lower()
    is_admin = role == "admin"

    # ------ SIDEBAR ------
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1.2rem 0 1rem;border-bottom:1px solid var(--border);margin-bottom:1rem;">
            <div style="font-size:1.4rem;font-weight:700;background:linear-gradient(135deg,var(--accent),var(--accent2));
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;">OneStepB</div>
            <div style="font-size:0.72rem;color:var(--text-secondary);margin-top:2px;">HR Attendance Portal</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="padding:0.8rem 1rem;background:rgba(79,142,247,0.07);
             border:1px solid var(--border);border-radius:12px;margin-bottom:1.2rem;">
            <div style="font-weight:600;font-size:0.9rem;">👤 {st.session_state.username}</div>
            <div style="margin-top:0.35rem;">{role_badge(role)}</div>
        </div>
        """, unsafe_allow_html=True)

        nav_pages = [("🏠  Home", "Home"), ("📊  Dashboard", "Dashboard")]
        if is_admin:
            nav_pages.append(("👑  Admin Panel", "Admin Panel"))

        for label, pkey in nav_pages:
            active = st.session_state.page == pkey
            if active:
                st.markdown('<div class="nav-active">', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{pkey}", use_container_width=True):
                st.session_state.page = pkey
                st.rerun()
            if active:
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="logout-wrap">', unsafe_allow_html=True)
        if st.button("🚪  Sign Out", key="signout_btn", use_container_width=True):
            if st.session_state.login_time:
                write_log(st.session_state.username, st.session_state.login_time, get_time())
            sessions = load_sessions()
            sessions.pop(st.session_state.username, None)
            save_sessions(sessions)
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    page = st.session_state.page

    # ==================== HOME ====================
    if page == "Home":
        st.markdown('<div class="section-header">🏠 Home</div>', unsafe_allow_html=True)
        now = get_time()

        # Active session indicator
        if st.session_state.login_time is not None:
            elapsed_hrs = (now - st.session_state.login_time).total_seconds() / 3600
            status_html = '<span class="status-active">● Active Session</span>'
        else:
            elapsed_hrs = 0
            status_html = '<span class="status-inactive">● No Active Session</span>'

        st.markdown(status_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        try:
            df_all = pd.read_csv(LOG_FILE)
            today = now.strftime("%Y-%m-%d")
            user_today = df_all[(df_all["username"] == st.session_state.username) & (df_all["date"] == today)]
            total_hrs = user_today["duration_hours"].sum()
            session_count = len(user_today)
        except Exception:
            total_hrs, session_count = 0.0, 0

        c1, c2, c3 = st.columns(3)
        with c1:
            login_str = st.session_state.login_time.strftime("%H:%M:%S") if st.session_state.login_time else "--:--:--"
            date_str = st.session_state.login_time.strftime("%d %B %Y") if st.session_state.login_time else "Not logged in"
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">Session Started</div>
                <div class="value" style="font-size:1.3rem;font-family:'JetBrains Mono',monospace;color:var(--accent);">{login_str}</div>
                <div class="sub">{date_str}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">Active Duration</div>
                <div class="value" style="color:var(--accent);">{elapsed_hrs:.2f}h</div>
                <div class="sub">Current session</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">Sessions Today</div>
                <div class="value" style="color:var(--success);">{session_count}</div>
                <div class="sub">{total_hrs:.2f}h completed</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### ⏱ Attendance Actions")
        st.markdown("<br>", unsafe_allow_html=True)

        colA, colB = st.columns(2)

        # LOGIN BUTTON
        with colA:
            st.markdown("""
            <div class="action-card">
                <div class="icon">🟢</div>
                <div class="action-title">Mark Login</div>
                <div class="action-sub">Record your start time for this session</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login", key="home_login_btn", use_container_width=True):
                if st.session_state.login_time is not None:
                    st.warning("⚠️ You already have an active session. Please logout first.")
                else:
                    login_time = get_time()
                    st.session_state.login_time = login_time
                    sessions = load_sessions()
                    sessions[st.session_state.username] = login_time.isoformat()
                    save_sessions(sessions)
                    st.success(f"✅ Logged in at **{login_time.strftime('%H:%M:%S IST')}**")
                    st.rerun()

        # LOGOUT BUTTON
        with colB:
            st.markdown("""
            <div class="action-card">
                <div class="icon">🔴</div>
                <div class="action-title">Mark Logout</div>
                <div class="action-sub">Record your end time and save the session</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Logout", key="home_logout_btn", use_container_width=True):
                if st.session_state.login_time is None:
                    st.warning("⚠️ No active login session found.")
                else:
                    logout_time = get_time()
                    write_log(
                        st.session_state.username,
                        st.session_state.login_time,
                        logout_time
                    )
                    sessions = load_sessions()
                    sessions.pop(st.session_state.username, None)
                    save_sessions(sessions)

                    duration = (logout_time - st.session_state.login_time).total_seconds() / 3600
                    login_str = st.session_state.login_time.strftime('%H:%M:%S')
                    logout_str = logout_time.strftime('%H:%M:%S')

                    st.session_state.login_time = None
                    st.success(
                        f"✅ Session recorded!\n\n"
                        f"🕒 Login: **{login_str}** &nbsp;|&nbsp; 🔴 Logout: **{logout_str}** &nbsp;|&nbsp; ⏳ Duration: **{duration:.2f}h**"
                    )
                    st.rerun()

    # ==================== DASHBOARD ====================
    elif page == "Dashboard":
        st.markdown('<div class="section-header">📊 Attendance Dashboard</div>', unsafe_allow_html=True)
        try:
            df = pd.read_csv(LOG_FILE)
        except Exception:
            df = pd.DataFrame(columns=["username", "date", "login_time", "logout_time", "duration_hours"])

        if not is_admin:
            df = df[df["username"] == st.session_state.username]

        if df.empty:
            st.info("No attendance records found yet.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="metric-card"><div class="label">Total Records</div><div class="value">{len(df)}</div><div class="sub">All sessions</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="metric-card"><div class="label">Total Hours</div><div class="value" style="color:var(--accent);">{df["duration_hours"].sum():.1f}h</div><div class="sub">Combined</div></div>', unsafe_allow_html=True)
            with c3:
                avg = df["duration_hours"].mean()
                st.markdown(f'<div class="metric-card"><div class="label">Avg Session</div><div class="value" style="color:var(--success);">{avg:.2f}h</div><div class="sub">Per session</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if is_admin:
                col1, col2 = st.columns(2)
                with col1:
                    sel_user = st.selectbox("Filter by User", ["All"] + sorted(df["username"].unique().tolist()))
                with col2:
                    sel_date = st.selectbox("Filter by Date", ["All"] + sorted(df["date"].unique().tolist(), reverse=True))
                if sel_user != "All":
                    df = df[df["username"] == sel_user]
                if sel_date != "All":
                    df = df[df["date"] == sel_date]

            st.dataframe(df, use_container_width=True, hide_index=True)

    # ==================== ADMIN PANEL ====================
    elif page == "Admin Panel":
        if not is_admin:
            st.error("🚫 Access denied.")
            st.stop()

        st.markdown('<div class="section-header">👑 Admin Panel</div>', unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["➕  Add User", "👥  Manage Users", "📈  Usage Stats"])

        with tab1:
            st.markdown("#### Create New Account")
            c1, c2 = st.columns(2)
            with c1:
                new_user = st.text_input("Username", placeholder="e.g. john_doe", key="nu")
                new_pass = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="np")
            with c2:
                new_role = st.selectbox("Role", ["intern", "employee", "admin"], key="nr")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅  Create User", key="create_btn", use_container_width=True):
                    if not new_user or not new_pass:
                        st.error("Both fields are required.")
                    elif len(new_pass) < 6:
                        st.warning("Password must be at least 6 characters.")
                    else:
                        users = load_users()
                        if any(u["username"] == new_user for u in users):
                            st.error(f"User **{new_user}** already exists.")
                        else:
                            hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
                            users.append({"username": new_user, "password": hashed, "role": new_role})
                            save_users(users)
                            st.success(f"✅ Created **{new_user}** as **{new_role}**.")
                            st.rerun()

        with tab2:
            st.markdown("#### All Registered Users")
            users = load_users()
            for i, user in enumerate(users):
                uname = user["username"]
                urole = user.get("role", "intern").strip().lower()
                is_self = uname == st.session_state.username
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.markdown(f"**{uname}**{'  *(you)*' if is_self else ''}")
                with col2:
                    st.markdown(role_badge(urole), unsafe_allow_html=True)
                with col3:
                    if not is_self:
                        opts = ["intern", "employee", "admin"]
                        new_r = st.selectbox("", opts, index=opts.index(urole) if urole in opts else 0, key=f"r_{i}", label_visibility="collapsed")
                        if new_r != urole:
                            if st.button("Save", key=f"s_{i}"):
                                users[i]["role"] = new_r
                                save_users(users)
                                st.success(f"Updated **{uname}** to **{new_r}**.")
                                st.rerun()
                with col4:
                    if not is_self:
                        if st.button("🗑️", key=f"d_{i}"):
                            users.pop(i)
                            save_users(users)
                            st.success(f"Deleted **{uname}**.")
                            st.rerun()
                    else:
                        st.caption("—")
                st.markdown('<hr style="border:none;border-top:1px solid var(--border);margin:0.1rem 0;">', unsafe_allow_html=True)

        with tab3:
            st.markdown("#### Usage Overview — All Users")
            try:
                df = pd.read_csv(LOG_FILE)
                if df.empty:
                    st.info("No log data yet.")
                else:
                    summary = df.groupby("username")["duration_hours"].agg(
                        Sessions="count", Total_Hours="sum", Avg_Hours="mean"
                    ).reset_index()
                    summary.columns = ["Username", "Sessions", "Total Hours", "Avg Hrs/Session"]
                    summary["Total Hours"] = summary["Total Hours"].round(2)
                    summary["Avg Hrs/Session"] = summary["Avg Hrs/Session"].round(2)
                    summary = summary.sort_values("Total Hours", ascending=False)
                    st.dataframe(summary, use_container_width=True, hide_index=True)
                    st.markdown("<br>**Total Hours by User**", unsafe_allow_html=True)
                    st.bar_chart(summary.set_index("Username")["Total Hours"])
            except Exception as e:
                st.error(f"Error loading logs: {e}")

# ---------- FOOTER ----------
st.markdown("""
<div class="footer-bar">
    © 2026 OneStepB &nbsp;·&nbsp; All Rights Reserved &nbsp;·&nbsp; onestepb7@gmail.com
</div>
""", unsafe_allow_html=True)