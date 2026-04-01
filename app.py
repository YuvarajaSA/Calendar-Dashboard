# app.py
# ══════════════════════════════════════════════════════════════
#  Cricket Player Availability & Conflict Dashboard  v2
#  Entry point — auth gate + sidebar navigation
#  Run:  streamlit run app.py
# ══════════════════════════════════════════════════════════════

import streamlit as st

# ── Page config (must be FIRST Streamlit call) ────────────────
st.set_page_config(
    page_title="Cricket Availability Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────
from config.styles import inject
inject()

# ── Auth ──────────────────────────────────────────────────────
from db.auth import is_logged_in, logout, current_email, get_role, can_edit, is_admin

# Show login page if not authenticated
if not is_logged_in():
    from views.login import render as login_page
    login_page()
    st.stop()

# ── Page modules (imported after auth check) ──────────────────
from views import (
    dashboard, calendar_view, search,
    add_event, add_team, add_squad,
    conflicts, availability, timeline, admin,
)
from db.operations import load_events, load_teams, load_squad
from utils.conflicts import detect_event_overlaps, detect_player_conflicts

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="padding:1.2rem 0 1.4rem;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;
                    color:#f0b429;letter-spacing:.06em;line-height:1;">
            🏏 CRICKET
        </div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:.82rem;
                    color:#8b949e;letter-spacing:.18em;margin-top:.1rem;">
            AVAILABILITY DASHBOARD
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Role pill for current user
    role = get_role()
    role_cls  = {"admin":"role-admin","editor":"role-editor","viewer":"role-viewer"}.get(role,"role-viewer")
    role_icon = {"admin":"👑","editor":"✏️","viewer":"👁"}.get(role,"👁")
    st.markdown(
        f'<div style="margin-bottom:1rem;">'
        f'<span style="font-size:.72rem;color:#8b949e;">{current_email()}</span><br>'
        f'<span class="role-pill {role_cls}">{role_icon} {role}</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Navigation — show admin link only to admins
    nav_options = [
        "📊  Dashboard",
        "📅  Calendar",
        "🔍  Search",
        "⚠️  Conflicts",
        "🔍  Availability",
        "📈  Timeline",
    ]
    if can_edit():
        nav_options += ["➕  Add Event", "🏟  Add Team", "👥  Add Squad"]
    if is_admin():
        nav_options += ["🛡  Admin"]

    page = st.radio("NAVIGATE", nav_options)

    st.markdown("---")

    # Live quick-stats (cached)
    events_df = load_events()
    teams_df  = load_teams()
    squad_df  = load_squad()

    total_events  = len(events_df)
    total_teams   = teams_df["team_name"].nunique() if not teams_df.empty else 0
    total_players = squad_df["player_name"].nunique() if not squad_df.empty else 0

    eo = detect_event_overlaps(events_df)
    pc = detect_player_conflicts(squad_df)

    st.markdown(f"""
    <div style="font-size:.62rem;font-weight:800;letter-spacing:.14em;
                text-transform:uppercase;color:#8b949e;margin-bottom:.7rem;">
        QUICK STATS
    </div>
    <div style="display:flex;flex-direction:column;gap:.4rem;">
        {''.join(
            f'<div style="background:#1c2128;border:1px solid #30363d;border-radius:8px;'
            f'padding:.5rem .9rem;display:flex;align-items:center;gap:.8rem;">'
            f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1.4rem;'
            f'color:{c};min-width:2rem;text-align:right;">{v}</span>'
            f'<span style="font-size:.72rem;font-weight:700;letter-spacing:.07em;'
            f'text-transform:uppercase;color:#8b949e;">{l}</span></div>'
            for v, l, c in [
                (total_events,  "Events",          "#f0b429"),
                (total_teams,   "Teams",            "#3fb950"),
                (total_players, "Players",          "#58a6ff"),
                (len(eo),       "Date Conflicts",   "#f85149" if eo else "#3fb950"),
                (len(pc),       "Player Conflicts", "#f85149" if pc else "#3fb950"),
            ]
        )}
    </div>
    """, unsafe_allow_html=True)

    # Logout
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪  Log Out", use_container_width=True, key="logout_btn"):
        logout()
        st.rerun()

    st.markdown("""
    <div style="font-size:.65rem;color:#8b949e;margin-top:.8rem;line-height:1.6;text-align:center;">
        Powered by <b style="color:#f0b429;">Supabase</b> + Streamlit<br>
        🔒 Internal use only
    </div>
    """, unsafe_allow_html=True)


# ── Page router ───────────────────────────────────────────────
ROUTES = {
    "📊  Dashboard":   dashboard.render,
    "📅  Calendar":    calendar_view.render,
    "🔍  Search":      search.render,
    "⚠️  Conflicts":   conflicts.render,
    "🔍  Availability":availability.render,
    "📈  Timeline":    timeline.render,
    "➕  Add Event":   add_event.render,
    "🏟  Add Team":    add_team.render,
    "👥  Add Squad":   add_squad.render,
    "🛡  Admin":       admin.render,
}

if page in ROUTES:
    ROUTES[page]()
