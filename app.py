"""Streamlit UI for Dream11 Genie.

Run:  streamlit run app.py
Needs GROQ_API_KEY in your environment / .env (free Groq key).
"""
import os

import streamlit as st
from groq import AuthenticationError, PermissionDeniedError
from streamlit.errors import StreamlitSecretNotFoundError

from agent import pick_team
from data import SQUADS

st.set_page_config(page_title="Dream11 Genie", page_icon="🏏", layout="centered")

# Streamlit Cloud stores credentials in app secrets, rather than a local .env.
try:
    for name in ("LLM_PROVIDER", "LLM_MODEL", "GROQ_MODEL", "GROQ_API_KEY"):
        if name in st.secrets:
            os.environ[name] = str(st.secrets[name])
except StreamlitSecretNotFoundError:
    pass

st.title("🏏 Dream11 Genie")
st.caption("An AI agent that reasons over live-style data to pick your fantasy XI.")

match = st.selectbox("Pick a fixture", list(SQUADS.keys()))

if st.button("Generate my XI", type="primary"):
    with st.spinner("The agent is calling tools and reasoning…"):
        try:
            team = pick_team(match)
        except PermissionDeniedError:
            st.error(
                "Groq denied access (403). Check that the selected model is allowed "
                "in both organization and project settings at "
                "https://console.groq.com/settings/limits and "
                "https://console.groq.com/settings/project/limits. "
                "If it is already allowed, check the Groq account status or contact Groq support."
            )
            st.stop()
        except AuthenticationError:
            st.error("Groq rejected the API key. Set a valid replacement GROQ_API_KEY in app secrets.")
            st.stop()
        except ValueError as exc:
            # Only expose our configuration errors; model validation errors can contain data.
            if str(exc).startswith(("Set GROQ_API_KEY", "This app supports LLM_PROVIDER")):
                st.error(str(exc))
                st.stop()
            raise

    st.subheader(f"Your XI — {team.match}")
    c1, c2 = st.columns(2)
    c1.metric("Captain (2x)", team.captain)
    c2.metric("Vice-captain (1.5x)", team.vice_captain)

    st.table(
        [
            {
                "": "⭐" if p.player == team.captain else ("🔸" if p.player == team.vice_captain else ""),
                "Player": p.player,
                "Role": p.role,
                "Team": p.team,
                "Why": p.reason,
            }
            for p in team.players
        ]
    )
    st.info(f"**Strategy:** {team.strategy}")
