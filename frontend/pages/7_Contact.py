import streamlit as st

import utils

st.set_page_config(
        page_title="Scratchpad: Personalized Co-Pilot",
        page_icon="frontend/asset/images/svg-1@2x.png",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

utils.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
utils.set_bg_hack('frontend/asset/images/background-svg@1x.png')

st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)

st.header("Please reach out to scratchpad.copilot@gmail.com for any issues or questions")