from pandas import read_sql_query
import streamlit as st
import streamlit_authenticator as stauth
import random
import string
import requests
import os
import yaml

import utils
from streamlit_extras.switch_page_button import switch_page

API_ENDPOINT=os.environ.get('API_ENDPOINT', 'http://localhost:8000')
os.environ["HAYSTACK_TELEMETRY_ENABLED"] = "False"


def main():
    st.set_page_config(
            page_title="Scratchpad: About",
            page_icon="frontend/asset/images/svg-1@2x.png",
            layout="wide",
            initial_sidebar_state="collapsed"
        )

    utils.local_css("frontend/asset/css/style.css")
    utils.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
    utils.set_bg_hack('frontend/asset/images/background-svg@1x.png')

    st.markdown(""" <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style> """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([4,0.5,1,1])

    with col1:

        st.markdown(utils.C1_LANDING_HEADING, unsafe_allow_html=True)

        st.markdown(utils.C1_INSTRUCTIONS_INFO, unsafe_allow_html=True)

        st.video("https://youtu.be/I43YETWiqzg")

    with col3:

        st.text("")
        st.text("")
        st.text("")
        st.text("")
        if st.button("Signup"):
            switch_page("register")
            

    with col4:

        st.text("")
        st.text("")
        st.text("")
        st.text("")
        if st.button("Login"):
            switch_page("login")
            


if __name__ == "__main__":
    main()
