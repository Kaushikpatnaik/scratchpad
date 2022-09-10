import base64
from io import BytesIO
from PIL import Image
import requests

import streamlit as st

C1_HEADER_INFO = """""".strip()
C2_HEADER_INFO = """
<div class="sidebar-div">
<h2 class="font-title text-bold" style='text-align: center'>Add to your knowledge base</h2>
</div>
""".strip()
C1_SEARCH_BOX_INFO = """
<div class="homepage-search-div">
<h2 class="font-title" style='text-align: center'><i>Scratchpad</i></h2>
</div>
""".strip()
C1_INSTRUCTIONS_INFO = """
<div class="instructions-div">
<br>
<h2 class="font-title" style='text-align: center'><i>Welcome to Scratchpad</i></h2>
<h3 class="font-title" style='text-align: center'><i>Personalized search engine for your private data</i></h3>
<br>
<h3 class="font-title" style='text-align: left'>
&emsp; About
</h3>
<ol>
  <li>Helps you search across all services (twitter, youtube, websites) and documents your interact with</li>
  <li>Search within the documents and text to fetch relevant information</li>
  <li>Use natural language queries for search, in addition to keywords</li>
  <li>Search that is completely personalized for your data</li>
  <li>Improves with time based on interaction</li>
</ol>
<h3 class="font-title" style='text-align: left'>
&emsp; How to use
</h3>
<ol>
  <li>Navigate to homepage</li>
  <li>Add your documents, websites, youtube urls on the left</li>
  <li>Perform search within your data</li>
</ol>
</div>
"""


def load_image_from_local(image_path, image_resize=None):
    image = Image.open(image_path)

    if isinstance(image_resize, tuple):
        image = image.resize(image_resize)
    return image


def load_image_from_url(image_url, rgba_mode=False, image_resize=None, default_image=None):
    try:
        image = Image.open(requests.get(image_url, stream=True).raw)

        if rgba_mode:
            image = image.convert("RGBA")

        if isinstance(image_resize, tuple):
            image = image.resize(image_resize)

    except Exception as e:
        image = None
        if default_image:
            image = load_image_from_local(default_image, image_resize=image_resize)

    return image


def image_to_base64(image_array):
    buffered = BytesIO()
    image_array.save(buffered, format="PNG")
    image_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64, {image_b64}"


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    


def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
 
    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "png"
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: 100% 60%;
             background-repeat: no-repeat;
             background-position: bottom;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )


def unset_bg_hack():
    # set bg name
    main_bg_ext = "png"
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background:none;
             background-repeat: no-repeat;
             background-position: bottom;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )