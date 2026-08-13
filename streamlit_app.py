#!/usr/bin/env python3
"""Auto Object Annotator — Streamlit front door mirroring the HF Space landing."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "templates" / "tagger.html"

st.set_page_config(
    page_title="Auto Object Annotator · Deborah Akuoko Minka",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

HF_URL = "https://huggingface.co/spaces/0001AMA/auto_object_annotator_0.0.4"
HF_EMBED = "https://0001AMA-auto-object-annotator-0.0.4.hf.space"
GH_URL = "https://github.com/2000pd3rvr/auto_object_annotator_0.0.4"
WP_URL = "https://deborahakuokominka.wordpress.com/"
ORCID = "https://orcid.org/0009-0008-6219-154X"

st.markdown(
    """
    <style>
      [data-testid="stHeader"] { display: none; }
      .block-container { padding-top: 1.25rem !important; max-width: 1100px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Auto Object Annotator")
st.subheader("Observe, label, and iterate on vision datasets")
st.caption("Deborah Akuoko Minka · Deborah Akuoko-Minka")

st.markdown(
    """
This Space is a practical loop for looking at images, proposing labels, and refining a
dataset without standing up a full labelling platform. The interactive tagger runs as a
Docker / Flask app on Hugging Face; open it below or in a new tab.
"""
)

c1, c2, c3 = st.columns(3)
c1.link_button("Open live tagger", HF_EMBED, use_container_width=True)
c2.link_button("Space page", HF_URL, use_container_width=True)
c3.link_button("Source on GitHub", GH_URL, use_container_width=True)

st.markdown("---")
st.markdown("### Live tagger")
components.iframe(HF_EMBED, height=780, scrolling=True)

with st.expander("About this project"):
    st.markdown(
        f"""
- **Live app (HF Docker):** [{HF_EMBED}]({HF_EMBED})
- **Source:** [{GH_URL}]({GH_URL})
- **Research site:** [{WP_URL}]({WP_URL})
- **ORCID:** [{ORCID}]({ORCID})

The Flask annotation API needs the Docker runtime on Hugging Face; this Streamlit page
is the public entry point with the same tagger embedded.
        """
    )

st.caption(f"Deborah Akuoko Minka · [research site]({WP_URL})")
