import streamlit as st
import requests
from streamlit_lottie import st_lottie

# Custom CSS styling similar to 01_🖥️_Dashboard.py
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #6eb52f;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #262730;
        margin-bottom: 2rem;
    }
    .card {
        background-color: #e0e0ef;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .emoji {
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)
#00000---------sidebar-----------------
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# All sidebar content is defined inside this block.
with st.sidebar:
    # Navigation widget for your top pages

    # Animation section: mountain-themed animation for "on top"
    st.markdown("### Connects with Neural Net Ninjas")
    # Replace the URL below with any mountain top or summit-themed Lottie animation.
    lottie_animation = load_lottie_url("https://lottie.host/e3ebc585-ff11-467d-b7df-06c8159aabe8/2EotAwBySN.json")
    if lottie_animation:
        st_lottie(lottie_animation, height=200, key="mountain_anim")
    else:
        st.error("Animation could not be loaded.")

#9------------end here ----------------

def main():
    # Title styled similarly to the main dashboard
    st.markdown('<p class="main-header">About N3DN.Tech</p>', unsafe_allow_html=True)
    
    # Sub-header with an emoji for extra flair
    st.markdown('<p class="sub-header">Empowering Tech Careers 🚀</p>', unsafe_allow_html=True)
    
    # Credits Section
    st.markdown("## Credits & Acknowledgments")
    st.markdown("""
    This project leverages state-of-the-art tools and APIs to deliver exceptional data-driven insights:
    
    - <span class="emoji">🔍</span> **Serp API**: Providing reliable search data integration.
    - <span class="emoji">🤖</span> **Gemini**: Powering advanced AI features.
    - <span class="emoji">🚀</span> **Streamlit**: Enabling the creation of interactive and user-friendly dashboards.
    """, unsafe_allow_html=True)
    
    # Mission Section
    st.markdown("## Our Mission")
    st.markdown("""
    At **N3DN.Tech**, our goal is to empower technology professionals with comprehensive analytics to make informed career decisions. 
    We bring together job market trends, skill analytics, and salary insights to give you the competitive edge in today's dynamic tech landscape.
    """)
    
    st.markdown("---")
    st.markdown("""
    For more details, visit our [GitHub repository](https://github.com/Shwetanlondhe24/HM0043_Team-Neural-Net-Ninjas) or connect with us on social media.
    """)
    
if __name__ == "__main__":
    main()
