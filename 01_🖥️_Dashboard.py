import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import folium
from streamlit_folium import st_folium
from streamlit_lottie import st_lottie
import requests

# Updated imports – using our modules for formatting and data import
from modules import importer
from modules import formater

# Set page configuration using formater module
title_obj = formater.Title()
title_obj.page_config("N3DN.Tech - Home")

# Custom CSS for basic styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
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
    .filter-container {
        background: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)
# ---------------- Sidebar Section ----------------
# Existing top navigation (Do Not Modify)
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# All sidebar content is defined within this block.
with st.sidebar:
    # Navigation widget
    # Version information
    st.markdown("### N3DN Version: 1.0.2")

    st.markdown("---")

    # Animation section
    st.markdown("### Your Career Hub: Explore Opportunities, Skills & Insights!")
    lottie_animation = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_jcikwtux.json")
    if lottie_animation:
        st_lottie(lottie_animation, height=200, key="sidebar_anim")
    else:
        st.error("Animation could not be loaded.")

# ---------- Sidebar Enhancements End ----------
# Main page content continues here.


# Create a session state to store our data
if 'jobs_data' not in st.session_state:
    st.session_state.jobs_data = None

# Load job data from local CSV using importer
data_file = os.path.join("data", "google_jobs.csv")
if os.path.exists(data_file) and st.session_state.jobs_data is None:
    st.session_state.jobs_data = importer.DataImport.fetch_and_clean_data(max_rows=1000)
else:
    st.session_state.jobs_data = importer.DataImport.fetch_and_clean_data(max_rows=1000)

# Header Section
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p style="font-size: 3.0rem; font-weight: bold; color: #6eb52f;">Welcome to N3DN.Tech</p>', unsafe_allow_html=True)

    st.markdown('<p class="sub-header">Data-Driven Insights for Technology Professionals</p>', unsafe_allow_html=True)
with col2:
    st.markdown(f"<h3>Data Updated: {datetime.now().year}</h3>", unsafe_allow_html=True)

# App Overview Section
st.title("N3DN.Tech - Tech Career Analytics Platform")
st.write("""
N3DN.Tech helps technology professionals make data-driven career decisions by providing comprehensive 
analytics on the job market, in-demand skills, and salary trends.
""")
st.subheader("Key Features")
st.markdown("""
<table>
    <tr>
        <th>Feature</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>📊 Job Data Insights</td>
        <td>Analyze job market trends using pre-fetched data from our trusted source.</td>
    </tr>
    <tr>
        <td>🔍 Skills Analysis</td>
        <td>Identify the most in-demand skills for tech professionals.</td>
    </tr>
    <tr>
        <td>💰 Salary Insights</td>
        <td>Track compensation trends across various roles and experience levels.</td>
    </tr>
    <tr>
        <td>🤖 Career Advisor</td>
        <td>Receive recommendations based on your profile and job market data.</td>
    </tr>
    <tr>
        <td>📈 Interactive Visualizations</td>
        <td>Explore trends and patterns through intuitive charts and maps.</td>
    </tr>
</table>
""", unsafe_allow_html=True)
st.info("""
**How to Get Started:**

- Begin with the **Top Skills** page to discover which technologies are most in demand.
- Next, explore **Skill Trends** to see how these demands are evolving over time.
- Then check **Skills vs Pay** to understand which skills lead to higher compensation.
- Finally, use the **Career Advisor** for personalized guidance based on your goals.
""")

# Key Metrics Section
st.markdown("### Key Insights")
col1_metric, col2_metric, col3_metric, col4_metric = st.columns(4)

trending_topic_display = "Data Analysis"
avg_salary_display = "$145K"
top_skill_display = "Python"
yoy_growth_display = "+24%"


if st.session_state.jobs_data is not None:
    if 'salary_yearly' in st.session_state.jobs_data.columns:
        salary_data = st.session_state.jobs_data['salary_yearly'].dropna()
        if not salary_data.empty:
            avg_salary_display = f"${int(salary_data.mean() / 1000)}K"
    elif 'salary' in st.session_state.jobs_data.columns:
        salary_data = st.session_state.jobs_data['salary'].dropna()
        if not salary_data.empty:
            avg_salary_display = f"${int(salary_data.mean() / 1000)}K"
    if 'description_tokens' in st.session_state.jobs_data.columns:
        all_skills = []
        for tokens in st.session_state.jobs_data['description_tokens'].dropna():
            if isinstance(tokens, str):
                skills = tokens.strip("[]").replace("'", "").split(", ")
                all_skills.extend(skills)
        skill_counts = pd.Series(all_skills).value_counts()
        if not skill_counts.empty:
            top_skill_display = skill_counts.index[0]
            if 'posted_at' in st.session_state.jobs_data.columns:
                try:
                    st.session_state.jobs_data['posted_date'] = pd.to_datetime(
                        st.session_state.jobs_data['posted_at'], errors='coerce'
                    )
                    recent_date = st.session_state.jobs_data['posted_date'].max() - pd.Timedelta(days=90)
                    recent_jobs = st.session_state.jobs_data[st.session_state.jobs_data['posted_date'] >= recent_date]
                    if not recent_jobs.empty and 'description_tokens' in recent_jobs.columns:
                        recent_skills = []
                        for tokens in recent_jobs['description_tokens'].dropna():
                            if isinstance(tokens, str):
                                skills = tokens.strip("[]").replace("'", "").split(", ")
                                recent_skills.extend(skills)
                        recent_skill_counts = pd.Series(recent_skills).value_counts()
                        if not recent_skill_counts.empty:
                            trending_topic_display = recent_skill_counts.index[0]
                except Exception as e:
                    pass

with col1_metric:
    st.markdown(f'<div class="card"><p class="metric-value">{avg_salary_display}</p><p class="metric-label">Average Salary</p></div>', unsafe_allow_html=True)
with col2_metric:
    st.markdown(f'<div class="card"><p class="metric-value">{top_skill_display}</p><p class="metric-label">Top Skill</p></div>', unsafe_allow_html=True)
with col3_metric:
    st.markdown(f'<div class="card"><p class="metric-value">{yoy_growth_display}</p><p class="metric-label">YoY Growth</p></div>', unsafe_allow_html=True)
with col4_metric:
    st.markdown(f'<div class="card"><p class="metric-value">{trending_topic_display}</p><p class="metric-label">Trending Topic</p></div>', unsafe_allow_html=True)

# Main Content Description
st.markdown("### Explore Our Data")
st.markdown("""
This interactive dashboard provides comprehensive insights into the job market for technology professionals:

- **Top Skills**: Discover the most in-demand skills for tech professionals.
- **Skill Trends**: Track emerging technologies and skills in the tech space.
- **Skills vs. Pay**: Analyze which skills correlate with higher compensation.
- **Career Advisor**: Get personalized recommendations based on your profile and market trends.
- **About**: Learn more about our data collection methodology and mission.
""", unsafe_allow_html=True)

# -------- Customize Your Experience Section --------
# -------- Customize Your Experience Section --------
st.markdown("### Customize Your Experience")
with st.expander("🔍 Filter Options", expanded=False):
    with st.container():
        colA, colB = st.columns(2)
        with colA:
            # Fixed list of countries for a broader worldwide filter.
            all_countries = [
                'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany', 
                'France', 'India', 'Singapore', 'Netherlands', 'Switzerland', 'Brazil', 
                'China', 'Japan', 'South Korea', 'Russia'
            ]
            selected_countries = st.multiselect("Select Countries", options=all_countries, default=all_countries)
            filtered_data = st.session_state.jobs_data[st.session_state.jobs_data["country"].isin(selected_countries)]
        with colB:
            # Predefined list of diverse job domains.
            job_domains = [
                "All Titles", "Data Scientist", "Software Engineer", "Data Engineer", 
                "Machine Learning Engineer", "DevOps Engineer", "Product Manager", 
                "UI/UX Designer", "Cybersecurity Specialist", "Cloud Architect", 
                "Business Analyst"
            ]
            selected_job_role = st.selectbox("Select Job Role", options=job_domains, index=0)
    
    # Apply job role filter if a specific role is selected.
    if selected_job_role and selected_job_role != "All Titles":
        filtered_data = filtered_data[filtered_data['title'].str.contains(selected_job_role, case=False, na=False)]
    
    # Convert country names in filtered_data to English using pycountry.
    import pycountry
    def convert_country_to_english(name):
        try:
            country = pycountry.countries.lookup(name)
            return country.name
        except Exception:
            return name

    filtered_data['country_english'] = filtered_data['country'].apply(convert_country_to_english)
    
    # Updated Skill Usage by Country Map using GeoPandas and Matplotlib
    st.markdown("#### Skill Usage by Country Map (GeoPandas)")
    try:
        import geopandas as gpd
        import matplotlib.pyplot as plt

        # Extract all unique skills from the overall job data for the select box.
        all_skills = []
        for tokens in st.session_state.jobs_data['description_tokens'].dropna():
            if isinstance(tokens, list):
                all_skills.extend(tokens)
            elif isinstance(tokens, str):
                tokens_list = tokens.strip("[]").replace("'", "").split(",")
                all_skills.extend([x.strip() for x in tokens_list])
        unique_skills = sorted(set(all_skills))
        
        # Skill selection dropdown.
        selected_skill = st.selectbox("Select Skill for Map Filter", options=unique_skills)
        
        # Helper function to count occurrences of the selected skill.
        def count_skill(tokens, skill):
            if isinstance(tokens, list):
                return tokens.count(skill)
            elif isinstance(tokens, str):
                tokens_list = tokens.strip("[]").replace("'", "").split(",")
                tokens_list = [x.strip() for x in tokens_list]
                return tokens_list.count(skill)
            return 0

        # Aggregate skill usage by country (using the English country names).
        filtered_data['skill_count'] = filtered_data['description_tokens'].apply(lambda tokens: count_skill(tokens, selected_skill))
        skill_usage = filtered_data.groupby("country_english")['skill_count'].sum().reset_index()

        # Load world dataset from an external GeoJSON source.
        geojson_url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
        world = gpd.read_file(geojson_url)

        # Merge aggregated data with the world GeoDataFrame.
        world_skill = world.merge(skill_usage, how="left", left_on="ADMIN", right_on="country_english")
        world_skill['skill_count'] = world_skill['skill_count'].fillna(0)

        # Create the plot.
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        world_skill.plot(column='skill_count', ax=ax, cmap='YlOrRd', legend=True,
                         legend_kwds={'label': f"Usage of '{selected_skill}'", 'orientation': "horizontal"})
        ax.set_title(f"Skill Usage by Country for '{selected_skill}'", fontsize=16)
        ax.set_axis_off()

        # Display the plot in Streamlit.
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"Error rendering GeoPandas map: {e}")



# -------- End Customize Your Experience Section --------

# Interactive element - Quick Poll
st.markdown("### Quick Poll")
st.markdown('<div class="card">', unsafe_allow_html=True)
poll_question = "What are your areas of interest in technology? (Select all that apply)"
options = [
    "Data Analysis & Business Intelligence",
    "Machine Learning & AI",
    "Web Development",
    "Cloud Computing & DevOps",
    "Cybersecurity",
    "Mobile Development",
    "Blockchain & Web3",
    "Game Development",
    "UI/UX Design",
    "Quality Assurance",
    "System Architecture",
    "Network Engineering",
    "Digital Marketing",
    "Project Management",
    "IT Support & Operations"
]
col1_poll, col2_poll, col3_poll = st.columns(3)
if 'selected_domains' not in st.session_state:
    st.session_state.selected_domains = []
selected_options = []
items_per_col = len(options) // 3
if len(options) % 3 != 0:
    items_per_col += 1
col1_options = options[:items_per_col]
col2_options = options[items_per_col:items_per_col*2]
col3_options = options[items_per_col*2:]
with col1_poll:
    for option in col1_options:
        if st.checkbox(option, key=f"cb1_{option}"):
            selected_options.append(option)
with col2_poll:
    for option in col2_options:
        if st.checkbox(option, key=f"cb2_{option}"):
            selected_options.append(option)
with col3_poll:
    for option in col3_options:
        if st.checkbox(option, key=f"cb3_{option}"):
            selected_options.append(option)
if st.button("Submit Response"):
    if selected_options:
        st.success(f"Thanks for sharing! You selected: {', '.join(selected_options)}")
        st.session_state.selected_domains = selected_options
    else:
        st.warning("Please select at least one area of interest.")
st.markdown('</div>', unsafe_allow_html=True)

# Personalized Recommendations (if a specific job role is selected)
if selected_job_role != "All Titles":
    st.markdown("### Personalized Recommendations")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    filtered_jobs = st.session_state.jobs_data[st.session_state.jobs_data['title'] == selected_job_role]
    
    top_skills = []
    if not filtered_jobs.empty and 'description_tokens' in filtered_jobs.columns:
        all_skills = []
        for tokens in filtered_jobs['description_tokens'].dropna():
            if isinstance(tokens, str):
                skills = tokens.strip("[]").replace("'", "").split(", ")
                all_skills.extend(skills)
        skill_counts = pd.Series(all_skills).value_counts().head(5)
        top_skills = skill_counts.index.tolist()
    
    selected_interest = selected_options[0] if selected_options else "technology"
    st.markdown(f"### Based on your profile as a {selected_interest} specialist")
    st.markdown(f"""
    Here are your personalized recommendations:
    
    1. **Skills to focus on**: {', '.join(top_skills) if top_skills else 'Data analysis, Python, SQL'}
    2. **Learning path**: Consider specializing in {selected_interest} applications.
    """)
    
    if not filtered_jobs.empty:
        salary_col = next((col for col in ['salary_yearly', 'salary'] if col in filtered_jobs.columns), None)
        if salary_col:
            salary_data = filtered_jobs[salary_col].dropna()
            if not salary_data.empty:
                exp_multiplier = 0.8  # Default multiplier; adjust as needed or use additional filters
                median_salary = salary_data.median()
                estimated_salary = int(median_salary * exp_multiplier)
                st.markdown(f"""
                **Your estimated market value**: ${estimated_salary:,} per year
                
                *This estimate is based on current market trends for {selected_job_role} roles.*
                """)
    st.markdown('</div>', unsafe_allow_html=True)

# Call to action
st.markdown("### Stay Updated")
st.markdown('<div class="card">', unsafe_allow_html=True)
col1_cta, col2_cta = st.columns([2, 1])
with col1_cta:
    email = st.text_input("Enter your email for monthly insights:")
    if st.button("Subscribe"):
        if "@" in email and "." in email:
            st.success("Thanks for subscribing! Check your email for confirmation.")
        else:
            st.error("Please enter a valid email address.")
with col2_cta:
    st.markdown("### Connect With Us")
    st.markdown("""
    [YouTube](https://www.youtube.com/watch?si=gOpctWkfOWA8f9v_&v=43PzmabhZL0&feature=youtu.be) | 
    [GitHub](https://github.com/Shwetanlondhe24/HM0043_Team-Neural-Net-Ninjas)
    """)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">© 2025 N3DN.Tech. All data is for demonstration purposes only.</div>', unsafe_allow_html=True)
