# db/auth.py
# ──────────────────────────────────────────────────────────────
#  Authentication & Role Management
#
#  Login options
#  ─────────────
#  1. Email + Password  (works immediately, no extra setup)
#  2. Google OAuth      (requires Google OAuth app in Supabase
#                        dashboard — see schema.sql for steps)
#
#  Roles
#  ─────
#  admin  → full CRUD + manage user roles
#  editor → add & edit events / squads
#  viewer → read-only (calendar, search, availability)
# ──────────────────────────────────────────────────────────────

from __future__ import annotations
import streamlit as st
from db.supabase_client import get_client


# ── Session helpers ───────────────────────────────────────────

def _set_session(session) -> None:
    st.session_state["auth_session"] = session
    st.session_state["auth_user"]    = session.user if session else None


def _clear_session() -> None:
    for k in ["auth_session", "auth_user", "auth_role"]:
        st.session_state.pop(k, None)


# ── Public API ────────────────────────────────────────────────

def current_user():
    """Return the currently logged-in Supabase user object, or None."""
    return st.session_state.get("auth_user")


def current_email() -> str:
    u = current_user()
    return u.email if u else ""


def is_logged_in() -> bool:
    return current_user() is not None


def get_role() -> str:
    """
    Return the role for the current user.
    Result is cached in session_state for the session.
    Falls back to 'viewer' if no record found.
    """
    if "auth_role" in st.session_state:
        return st.session_state["auth_role"]

    u = current_user()
    if not u:
        return "viewer"

    sb   = get_client()
    resp = sb.table("user_roles").select("role").eq("user_id", u.id).single().execute()
    role = resp.data.get("role", "viewer") if resp.data else "viewer"
    st.session_state["auth_role"] = role
    return role


def can_edit() -> bool:
    return get_role() in ("admin", "editor")


def is_admin() -> bool:
    return get_role() == "admin"


# ── Login ─────────────────────────────────────────────────────

def login_with_password(email: str, password: str) -> tuple[bool, str]:
    sb = get_client()
    try:
        resp = sb.auth.sign_in_with_password({"email": email, "password": password})
        if resp.session:
            _set_session(resp.session)
            st.session_state.pop("auth_role", None)   # re-fetch role
            return True, "Logged in successfully."
        return False, "Invalid credentials."
    except Exception as e:
        return False, str(e)


def login_with_google() -> str:
    """
    Return the Google OAuth URL.
    The user must be redirected to this URL.
    After auth, Supabase redirects back to the app URL with a token.
    """
    sb = get_client()
    resp = sb.auth.sign_in_with_oauth({
        "provider": "google",
        "options":  {"redirect_to": st.secrets["supabase"].get("redirect_url", "")},
    })
    return resp.url if resp else ""


def handle_oauth_callback() -> bool:
    """
    If Supabase redirected back with a token in the URL query params,
    exchange it for a session and store it.
    """
    params = st.query_params
    access_token  = params.get("access_token")
    refresh_token = params.get("refresh_token")

    if not access_token:
        return False

    sb = get_client()
    try:
        resp = sb.auth.set_session(access_token, refresh_token)
        if resp.session:
            _set_session(resp.session)
            st.session_state.pop("auth_role", None)
            # Clean URL
            st.query_params.clear()
            return True
    except Exception:
        pass
    return False


def logout() -> None:
    sb = get_client()
    try:
        sb.auth.sign_out()
    except Exception:
        pass
    _clear_session()


# ── User management (admin only) ──────────────────────────────

def list_users() -> list[dict]:
    """Return all rows from user_roles."""
    sb   = get_client()
    resp = sb.table("user_roles").select("*").order("email").execute()
    return resp.data or []


def set_user_role(user_id: str, email: str, role: str) -> tuple[bool, str]:
    sb = get_client()
    try:
        sb.table("user_roles").upsert({
            "user_id": user_id,
            "email":   email,
            "role":    role,
        }).execute()
        return True, f"Role updated to '{role}' for {email}."
    except Exception as e:
        return False, str(e)


def invite_user_by_email(email: str, role: str = "viewer") -> tuple[bool, str]:
    """
    Admin invites a new user. Supabase sends them a magic-link email.
    Their role row is pre-created so when they log in they get the right role.
    NOTE: Requires service_role key for admin.invite_user_by_email —
          for simplicity we use the sign-up flow and pre-insert the role.
    """
    sb = get_client()
    try:
        # Ask Supabase to create the user (magic link)
        resp = sb.auth.admin.invite_user_by_email(email)
        user_id = resp.user.id
        sb.table("user_roles").upsert({
            "user_id": user_id,
            "email":   email,
            "role":    role,
        }).execute()
        return True, f"Invitation sent to {email} with role '{role}'."
    except Exception as e:
        return False, f"Could not invite: {e}"
