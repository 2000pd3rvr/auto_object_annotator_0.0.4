#!/usr/bin/env python3
"""Auto Object Annotator — Streamlit Community Cloud app (GitHub-connected)."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Auto Object Annotator · Deborah Akuoko Minka",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded",
)

HF_URL = "https://huggingface.co/spaces/0001AMA/auto_object_annotator_0.0.4"
HF_EMBED = "https://0001AMA-auto-object-annotator-0.0.4.hf.space"
GH_URL = "https://github.com/2000pd3rvr/auto_object_annotator_0.0.4"
WP_URL = "https://deborahakuokominka.wordpress.com/"
ORCID = "https://orcid.org/0009-0008-6219-154X"
SCHOLAR = "https://scholar.google.co.uk/citations?hl=en&user=ab0EyjYAAAAJ"

st.title("Auto Object Annotator")
st.subheader("Observe, label, and iterate on vision datasets")
st.caption("Deborah Akuoko Minka · Deborah Akuoko-Minka")

b1, b2, b3, b4 = st.columns(4)
b1.link_button("Live demo", HF_URL, use_container_width=True)
b2.link_button("Source on GitHub", GH_URL, use_container_width=True)
b3.link_button("Research site", WP_URL, use_container_width=True)
b4.link_button("ORCID", ORCID, use_container_width=True)

st.markdown("---")
left, right = st.columns([1.25, 1])

with left:
    st.header("What it is")
    st.write(
        "Auto Object Annotator is a small vision tooling Space for exploring automatic "
        "object annotation. It is aimed at people who need a practical loop between "
        "looking at images, proposing labels, and refining a dataset without standing "
        "up a full labelling platform."
    )

    st.header("What you can do")
    st.markdown(
        """
- Run annotation passes against sample or uploaded image sets
- Inspect proposed labels before committing them
- Export results for downstream training or review
- Compare the approach with heavier annotation stacks
        """
    )

    st.header("Who it is for")
    st.write(
        "Computer vision researchers, data engineers, and practitioners preparing "
        "labelled sets for detection or recognition work."
    )

    st.header("How it is built")
    st.markdown(
        f"""
- **Live app:** [Hugging Face Space — 0001AMA/auto_object_annotator_0.0.4]({HF_URL})
- **Source:** [{GH_URL}]({GH_URL})
- **Stack:** Docker Space with a Python annotation front end
- **Author:** Deborah Akuoko Minka (also written Deborah Akuoko-Minka)
        """
    )

    st.header("Related links")
    st.markdown(
        f"""
- [WordPress research site]({WP_URL})
- [ORCID]({ORCID})
- [Google Scholar]({SCHOLAR})
        """
    )

with right:
    st.header("Preview")
    st.write("Embedded view of the live Space. If the frame is empty, open the live demo link above.")
    components.iframe(HF_EMBED, height=720, scrolling=True)

st.markdown("---")
st.caption(
    "Deborah Akuoko Minka · machine intelligence and vision tooling · "
    f"[deborahakuokominka.wordpress.com]({WP_URL})"
)
