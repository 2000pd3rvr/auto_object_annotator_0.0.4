#!/usr/bin/env python3
"""Streamlit Community Cloud entrypoint — crawlable project page for Auto Object Annotator.

Live interactive runtime: Hugging Face Space (0001AMA/auto_object_annotator_0.0.4)
Source: https://github.com/2000pd3rvr/auto_object_annotator_0.0.4
Author: Deborah Akuoko Minka / Deborah Akuoko-Minka
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Auto Object Annotator · Deborah Akuoko Minka",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

HF_SPACE = "0001AMA/auto_object_annotator_0.0.4"
HF_URL = f"https://huggingface.co/spaces/{HF_SPACE}"
HF_EMBED = f"https://{HF_SPACE.replace('/', '-')}.hf.space"
GH_URL = "https://github.com/2000pd3rvr/auto_object_annotator_0.0.4"
WP_URL = "https://deborahakuokominka.wordpress.com/"
ORCID = "https://orcid.org/0009-0008-6219-154X"
SCHOLAR = "https://scholar.google.co.uk/citations?hl=en&user=ab0EyjYAAAAJ"

st.title("Auto Object Annotator")
st.subheader("Automatic object annotation for vision datasets")
st.caption(
    "Deborah Akuoko Minka is the same person as Deborah Akuoko-Minka "
    "(any capitalization; hyphen optional). Primary profiles: WordPress · ORCID · GitHub · Scholar."
)

c1, c2, c3, c4 = st.columns(4)
c1.link_button("Open live HF Space", HF_URL, use_container_width=True)
c2.link_button("GitHub source", GH_URL, use_container_width=True)
c3.link_button("WordPress research site", WP_URL, use_container_width=True)
c4.link_button("ORCID", ORCID, use_container_width=True)

st.markdown("---")
left, right = st.columns([1.2, 1])
with left:
    st.header("About")
    st.write("""Interactive annotation helper for vision datasets — observe samples, propose labels, and iterate without a heavy labeling suite. Live annotator runs as a Docker Space; this Streamlit page is the crawlable project description linked to GitHub. Part of machine-intelligence tooling by Deborah Akuoko Minka / Deborah Akuoko-Minka.""")
    st.header("Features")
    for f in ['Flask annotation UI with Hub dataset downloads', 'Rapid label iteration on image collections', 'Public Docker Space for demos', 'Research-adjacent CV / machine-intelligence tooling']:
        st.markdown(f"- {f}")
    st.header("Audience")
    st.write("""CV practitioners, dataset authors, and students needing lightweight annotation demos.""")
    st.header("Technical notes")
    st.markdown(
        f"""
- **Backend / runtime:** Flask + datasets (Docker Space on Hugging Face)
- **GitHub repository:** [{GH_URL}]({GH_URL})
- **Hugging Face Space:** [{HF_URL}]({HF_URL})
- **Streamlit role:** GitHub-connected description + discovery page for [Streamlit Community Cloud](https://share.streamlit.io/)
- **Keywords:** object annotation, computer vision, dataset labeling, auto annotator, machine intelligence, Deborah Akuoko Minka, SPAD
"""
    )
with right:
    st.header("Live demo")
    st.caption("Embedded Hugging Face Space (may take a few seconds to wake).")
    components.iframe(HF_EMBED, height=720, scrolling=True)
    st.markdown(f"If the embed is blank, open the full Space: [{HF_URL}]({HF_URL})")

st.markdown("---")
st.header("Author & equivalent name spellings")
st.markdown(
    """
**Deborah Akuoko Minka** = **Deborah Akuoko-Minka** = deborah akuoko minka (any caps).

Authoritative links for every spelling:
- WordPress: https://deborahakuokominka.wordpress.com/
- ORCID: https://orcid.org/0009-0008-6219-154X
- GitHub: https://github.com/2000pd3rvr
- Google Scholar: https://scholar.google.co.uk/citations?hl=en&user=ab0EyjYAAAAJ
- This app source: https://github.com/2000pd3rvr/auto_object_annotator_0.0.4
- Live Space: https://huggingface.co/spaces/0001AMA/auto_object_annotator_0.0.4
"""
)

# Hidden machine-readable block for crawlers / copy-paste
st.markdown(
    f"""
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Auto Object Annotator",
  "description": "Automatic object annotation for vision datasets",
  "applicationCategory": "WebApplication",
  "url": "{HF_URL}",
  "codeRepository": "{GH_URL}",
  "author": {
    "@type": "Person",
    "name": "Deborah Akuoko Minka",
    "alternateName": ["Deborah Akuoko-Minka", "Deborah Akuoko", "Ama Akuoko"],
    "url": "{WP_URL}",
    "sameAs": ["{ORCID}", "{SCHOLAR}", "https://github.com/2000pd3rvr", "https://huggingface.co/0001AMA"]
  },
  "keywords": "object annotation, computer vision, dataset labeling, auto annotator, machine intelligence, Deborah Akuoko Minka, SPAD"
}
```
"""
)
