from pandas import read_sql_query
import streamlit as st
import random
import string
import requests
import os

import utils


API_ENDPOINT=os.environ.get('API_ENDPOINT', 'http://localhost:8000')
os.environ["HAYSTACK_TELEMETRY_ENABLED"] = "False"


def parse_summarize_results(request_json):
    result_documents = request_json['documents']
    return result_documents


def main():
    st.set_page_config(
        page_title="Scratchpad: Personalized Co-Pilot",
        page_icon="frontend/asset/images/svg-1@2x.png",
        initial_sidebar_state="auto"
    )

    if st.session_state.get("logged_in", False):

        #utils.local_css("frontend/asset/css/style.css")
        utils.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
        utils.set_bg_hack('frontend/asset/images/background-svg@1x.png')

        st.markdown(""" <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style> """, unsafe_allow_html=True)

        user_name = st.session_state["user_name"]

        with st.sidebar:
            st.markdown(utils.C2_HEADER_INFO, unsafe_allow_html=True)
            file = st.file_uploader("Upload a pdf, csv or docx file")
            file_added = st.button('Upload File')

            if file_added:
                file_endpoint = API_ENDPOINT + "/parse/document"
                response = requests.post(file_endpoint, files={'docs': file, 'user': user_name})
                st.write(str(file.name) + " Uploaded")

            link = st.text_input("Add youtube video")
            link_added = st.button('Upload Video')

            if link_added:
                yt_endpoint = API_ENDPOINT + "/parse/youtube/"
                response = requests.post(yt_endpoint, json={'url': link, 'user': user_name})
                st.write(str(link) + " Uploaded. Youtube videos take time to parse. Please wait for some time to search within youtube videos")
            
            url = st.text_input("Parse Website Text")
            url_added = st.button('Parse Website')
            
            if url_added:
                url_endpoint = API_ENDPOINT + "/parse/url"
                response = requests.post(url_endpoint, json={'url': url, 'user': user_name})

        st.markdown(utils.C1_SEARCH_BOX_INFO, unsafe_allow_html=True)
        
        # need to do column hacking to place search box and buttom at center
        col1, col2, col3 = st.columns([2,5,2])
        with col2:
            selected = st.text_input("")
            button_clicked = st.button("Summarize")
            st.markdown(utils.C1_SUMMARIZE_INFO, unsafe_allow_html=True)
            
        # if search is pressed need to add containers with search results
        # Add code that pressing enter also launches search
        if button_clicked or selected != "":
            search_endpoint = API_ENDPOINT + "/summarize"
            response = requests.get(search_endpoint, params={'query': selected, 'user': user_name})
            if response.status_code == 200:
                response_json = response.json()
                content = parse_summarize_results(response_json)
                st.markdown(
                    "<hr />",
                    unsafe_allow_html=True
                )
                utils.unset_bg_hack()
                with st.container():
                    st.header("Summarizing results from Scratchpad")
                    st.markdown(
                            " ".join([
                                "<div class='results-{str_i} text-wrapper'>",
                                f"<p class='font-body'>{content}</p>",
                                "</div>",
                            ]),
                            unsafe_allow_html=True
                            )
            else:
                with st.container():
                    utils.error_frontend("Request failed due to backend error")
    else:
        utils.error_frontend("Cookie Expired. Please Log in again from the sidebar")


if __name__ == "__main__":
    main()

