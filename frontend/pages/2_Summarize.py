from pandas import read_sql_query
import streamlit as st
import random
import string
import requests
import os

import utils


API_ENDPOINT=os.environ.get('API_ENDPOINT', 'http://localhost:8000')
os.environ["HAYSTACK_TELEMETRY_ENABLED"] = "False"

def parse_search_results(request_json):
    result_documents = request_json['documents']
    num_results = len(result_documents)
    results_dict = {}
    for idx, result in enumerate(result_documents):
        # result['meta']['src_type']
        results_dict[idx] = {'title': result['meta'].get('file_name', "No file name"), 'src_type': result['meta'].get(
        'src_type', 'yt'), 'content': result['content'], 'score': result['score']}

    return results_dict, num_results


def main():
    st.set_page_config(
        page_title="Scratchpad: Your personalized assistant",
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
    col1, col2, col3 = st.columns([3,4,3])
    with col2:
        selected = st.text_input("")
        button_clicked = st.button("Summarize")
        
    # if search is pressed need to add containers with search results
    # Add code that pressing enter also launches search
    if button_clicked or selected != "":
        search_endpoint = API_ENDPOINT + "/retrieval_and_summarize"
        response = requests.get(search_endpoint, params={'query': selected, 'user': user_name})
        if response.status_code == 200:
            response_json = response.json()
            st.markdown(
                "<hr />",
                unsafe_allow_html=True
            )
            utils.unset_bg_hack()
            with st.container():
                st.header("Summary from Scratchpad")

                results_dict, num_results = parse_search_results(response_json)

                # dedup based on title
                # going to hurt no title data
                # since ranker outputs data based on score, selecting highest scoring will be better
                uniq_titles = {}
                for i in range(num_results):
                    title_src = results_dict[i]['title'] + results_dict[i]['src_type']
                    if title_src not in uniq_titles:
                        uniq_titles[title_src] = i

                for _, i in uniq_titles.items():
                    title = results_dict[i]['title']
                    str_i = str(i)
                    content = results_dict[i]['content']
                    thumbnail_image = thumbnail_images[results_dict[i]['src_type']]

                    st.markdown(
                        " ".join([
                            "<div class='results-{str_i} text-wrapper'>",
                            f"<img src='{thumbnail_image}' align='left' class='img-wrapper'>",
                            f"<p class='font-body'><b>{title}</b></p>",
                            f"<p class='font-body'>{content}</p>",
                            "</div>",
                        ]),
                        unsafe_allow_html=True
                        )
        else:
            st.markdown(
                "<hr />",
                unsafe_allow_html=True
            )
            utils.unset_bg_hack()
            with st.container():
                st.header("Backend Error!!! :(")


if __name__ == "__main__":
    main()

