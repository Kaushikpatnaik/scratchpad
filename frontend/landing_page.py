from pandas import read_sql_query
import streamlit as st
import random
import string
import requests
import os

import utils


API_ENDPOINT=os.environ.get('API_ENDPOINT', 'http://localhost:8000')


def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True


def get_thumnail_images():
    pdf_thumb = utils.image_to_base64(utils.load_image_from_local("frontend/asset/images/pdf-icon_100.png"))
    docx_thumb = utils.image_to_base64(utils.load_image_from_local("frontend/asset/images/word_100.png"))
    txt_thumb = utils.image_to_base64(utils.load_image_from_local("frontend/asset/images/csv_100.png"))
    url_thumb = utils.image_to_base64(utils.load_image_from_local("frontend/asset/images/website@2x_100.png"))
    yt_thumb = utils.image_to_base64(utils.load_image_from_local("frontend/asset/images/youtube_100.png"))
    twt_thumb = utils.image_to_base64(utils.load_image_from_local("frontend/asset/images/twitter_logo_100x100.png"))

    return {'pdf': pdf_thumb, 'docx': docx_thumb, 'txt': txt_thumb, 'url': url_thumb, 'yt': yt_thumb, 'twt': twt_thumb}


def main():
    if check_password():

        st.set_page_config(
            page_title="Scratchpad: About",
            page_icon="frontend/asset/images/svg-1@2x.png",
            layout="wide",
            initial_sidebar_state="auto"
        )

        utils.local_css("frontend/asset/css/style.css")
        utils.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
        utils.set_bg_hack('frontend/asset/images/background-svg@1x.png')

        st.markdown(""" <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style> """, unsafe_allow_html=True)

        st.markdown(utils.C1_INSTRUCTIONS_INFO, unsafe_allow_html=True)    


if __name__ == "__main__":
    main()
