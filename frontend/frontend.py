from pandas import read_sql_query
import streamlit as st
import random
import string
import requests
import os

import utils


API_ENDPOINT=os.environ.get('API_ENDPOINT', 'http://localhost:8000')


def main():
    st.set_page_config(
        page_title="Scratchpad: Your personalized search engine",
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

    with st.sidebar:
        st.markdown(utils.C2_HEADER_INFO, unsafe_allow_html=True)
        file = st.file_uploader("Upload a pdf, csv or docx file")
        file_added = st.button('Upload File')
        link = st.text_input("Add youtube video")
        link_added = st.button('Upload Video')
        url = st.text_input("Parse Website Text")
        url_added = st.button('Parse Website')

        if file_added:
            file_endpoint = API_ENDPOINT + "/parse/document"
            response = requests.post(file_endpoint, files=[("files", file)]).json()
            print(response)
            st.write(str(file.name) + " Uploaded")
        if link_added:
            yt_endpoint = API_ENDPOINT + "/parse/youtube/"
            response = requests.post(yt_endpoint, data={'url': link})
            print(response)
            st.write(str(link) + " Uploaded. Youtube videos take time to parse. Please wait for some time to search within youtube videos")
        if url_added:
            url_endpoint = API_ENDPOINT + "/parse/url/"
            response = requests.post(url_endpoint, data={'url': url})
            print(response)
            st.write(str(url) + " Parsed website text")

    st.markdown(utils.C1_SEARCH_BOX_INFO, unsafe_allow_html=True)
    
    # need to do column hacking to place search box and buttom at center
    col1, col2, col3 = st.columns([3,4,3])
    with col2:
        selected = st.text_input("")
        button_clicked = st.button("Search")

    # if search is pressed need to add containers with search results
    if button_clicked:
        search_endpoint = API_ENDPOINT + "/comb_search"
        response = requests.get(search_endpoint, params={'query': selected})
        st.markdown(
            "<hr />",
            unsafe_allow_html=True
        )
        utils.unset_bg_hack()
        with st.container():
            st.header("Search results from Scratchpad")

            letters = string.ascii_lowercase
            image_temp = utils.image_to_base64(utils.load_image_from_local("./asset/images/svg-1@2x.png"))

            for i in range(20):
                title = ''.join(random.choice(letters) for i in range(10))
                str_i = str(i)
                st.markdown(
                    " ".join([
                        "<div class='results-{str_i} text-wrapper'>",
                        f"<img src='{image_temp}' align='left' class='img-wrapper'>",
                        "<p class='font-body'><b>Result Text with hyperlink</b></p>",
                        "<p class='font-body'>Details of text</p>",
                        "</div>",
                    ]),
                    unsafe_allow_html=True
                    )


if __name__ == "__main__":
    main()
