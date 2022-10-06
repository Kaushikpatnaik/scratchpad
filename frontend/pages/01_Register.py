import yaml
import utils

import streamlit as st
import streamlit_authenticator as stauth

st.set_page_config(
    page_title="Scratchpad: Personalized Co-Pilot",
    page_icon="frontend/asset/images/svg-1@2x.png",
    layout="wide",
    initial_sidebar_state="collapsed"
    )

if "logged_in" not in st.session_state:

    utils.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
    utils.set_bg_hack('frontend/asset/images/background-svg@1x.png')

    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)

    with open('/home/user/frontend/config.yaml') as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)

    authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['preauthorized'])

    if authenticator.register_user('Register user', preauthorization=False):
        st.success('User registered successfully')
        with open('/home/user/frontend/config.yaml', 'w') as file:
            doc = yaml.dump(config, file)
        utils.switch_page("login")
