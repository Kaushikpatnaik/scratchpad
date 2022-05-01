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