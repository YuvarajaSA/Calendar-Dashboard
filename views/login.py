# # pages/login.py
# # ──────────────────────────────────────────────────────────────
# #  Login gate — shown to unauthenticated visitors.
# #  Supports:
# #    • Email + Password  (works out of the box)
# #    • Google OAuth      (needs Google provider enabled in Supabase)
# # ──────────────────────────────────────────────────────────────

# import streamlit as st
# from db.auth import login_with_password, handle_oauth_callback, login_with_google


# def render() -> None:
#     # Check for OAuth redirect callback first
#     if handle_oauth_callback():
#         st.rerun()

#     st.markdown("""
#     <div class="login-box">
#         <div class="login-logo">🏏 CRICKET</div>
#         <div class="login-sub">Availability & Conflict Dashboard<br>
#             <span style="font-size:0.78rem;color:#30363d;">— Internal Staff Access Only —</span>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

#     # Centre the form
#     _, mid, _ = st.columns([1, 2, 1])
#     with mid:
#         st.markdown('<div class="login-box">', unsafe_allow_html=True)

#         tab_email, tab_google = st.tabs(["✉️  Email & Password", "🔵  Google Login"])

#         # ── Email / Password ──────────────────────────────────
#         with tab_email:
#             st.markdown("<br>", unsafe_allow_html=True)
#             email    = st.text_input("Email address", placeholder="you@yourcompany.com", key="li_email")
#             password = st.text_input("Password", type="password", key="li_pass")

#             if st.button("Log In", use_container_width=True, key="btn_email_login"):
#                 if not email.strip() or not password:
#                     st.error("Please enter both email and password.")
#                 else:
#                     with st.spinner("Verifying…"):
#                         ok, msg = login_with_password(email.strip(), password)
#                     if ok:
#                         st.success(msg)
#                         st.rerun()
#                     else:
#                         st.error(f"Login failed: {msg}")

#             st.markdown("""
#             <div style="font-size:0.78rem;color:#8b949e;margin-top:1rem;text-align:center;">
#                 Forgot password? Contact your admin to reset it via the Supabase dashboard.
#             </div>
#             """, unsafe_allow_html=True)

#         # ── Google OAuth ──────────────────────────────────────
#         with tab_google:
#             st.markdown("<br>", unsafe_allow_html=True)
#             st.markdown("""
#             <div class="alert-box alert-info">
#                 <div class="icon">ℹ️</div>
#                 <div class="body">
#                     <div class="title">Google Login</div>
#                     Click below to authenticate with your Google / Gmail account.
#                     Only pre-approved email addresses can access the system.
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)

#             if st.button("🔵  Continue with Google", use_container_width=True, key="btn_google"):
#                 try:
#                     url = login_with_google()
#                     if url:
#                         st.markdown(
#                             f'<meta http-equiv="refresh" content="0; url={url}">',
#                             unsafe_allow_html=True,
#                         )
#                     else:
#                         st.error("Google OAuth is not configured. "
#                                  "Enable the Google provider in Supabase → Authentication → Providers.")
#                 except Exception as e:
#                     st.error(f"OAuth error: {e}")

#         st.markdown('</div>', unsafe_allow_html=True)

#     # Security notice
#     st.markdown("""
#     <div style="text-align:center;margin-top:2rem;font-size:0.76rem;color:#8b949e;">
#         🔒 Secured by Supabase Auth · Internal use only
#     </div>
#     """, unsafe_allow_html=True)






# views/login.py
# ──────────────────────────────────────────────────────────────
#  Login gate — email + password only.
#  Google OAuth removed; re-add later once OAuth consent is
#  approved in Google Cloud Console.
# ──────────────────────────────────────────────────────────────

import streamlit as st
from db.auth import login_with_password


def render() -> None:
    st.markdown("""
    <div class="login-box">
        <div class="login-logo">🏏 CRICKET</div>
        <div class="login-sub">Availability &amp; Conflict Dashboard<br>
            <span style="font-size:0.78rem;color:#30363d;">— Internal Staff Access Only —</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        email    = st.text_input("Email address", placeholder="you@yourcompany.com", key="li_email")
        password = st.text_input("Password", type="password", key="li_pass")

        if st.button("Log In", use_container_width=True, key="btn_email_login"):
            if not email.strip() or not password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner("Verifying…"):
                    ok, msg = login_with_password(email.strip(), password)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(f"Login failed: {msg}")

        st.markdown("""
        <div style="font-size:0.78rem;color:#8b949e;margin-top:1rem;text-align:center;">
            Forgot password? Contact your admin to reset it via the Supabase dashboard.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:2rem;font-size:0.76rem;color:#8b949e;">
        🔒 Secured by Supabase Auth · Internal use only
    </div>
    """, unsafe_allow_html=True)