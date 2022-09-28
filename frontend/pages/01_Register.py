import yaml
import utils

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    page_title="Scratchpad: Your personalized assistant",
    page_icon="frontend/asset/images/svg-1@2x.png",
    layout="wide",
    initial_sidebar_state="collapsed"
    )

if not st.session_state["logged_in"]:

    utils.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
    utils.set_bg_hack('frontend/asset/images/background-svg@1x.png')

    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)

    with open('/home/dexter89_kp/Desktop/scratchpad/frontend/config.yaml') as file:
            config = yaml.load(file, Loader=yaml.SafeLoader)

    authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['preauthorized'])

    if authenticator.register_user('Register user', preauthorization=False):
            st.success('User registered successfully')
            switch_page("search")
