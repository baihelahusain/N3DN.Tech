import streamlit as st

class Title(object):
    """"
    Update title and favicon of each page
    ⚠️ IMPORTANT: Must call page_config() as first function in script 
    """
    def __init__(self):
        # Using a default emoji as favicon instead of a local file
        self.img = "🛠️"
    
    def page_config(self, title):
        self.title = title
        st.set_page_config(page_title=self.title, page_icon=self.img)

class Footer:
    """"
    Creates a footer with a link
    Simplified version that doesn't rely on htbuilder
    """

    def __init__(self):
        self.url = "https://serpapi.com/"
        self.text = "Powered by SerpApi"

    def footer(self):
        footer_html = f"""
        <div style="position: fixed; bottom: 0; right: 0; margin: 0px 10px 10px 0px; text-align: center;">
            <a href="{self.url}" target="_blank">{self.text}</a>
        </div>
        <style>
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            .stApp {{ bottom: 0px; }}
        </style>
        """
        st.markdown(footer_html, unsafe_allow_html=True)
