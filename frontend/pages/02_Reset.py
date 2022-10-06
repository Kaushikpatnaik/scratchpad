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

try:
    username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Forgot password')
    if username_forgot_pw:
        st.success('New password sent securely')
        # Random password to be transferred to user securely
        st.write(random_password)
        st.write("Please keep new password safe")
    elif username_forgot_pw == False:
        st.error('Username not found')
except Exception as e:
    st.error(e)