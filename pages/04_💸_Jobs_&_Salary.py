# pages/03_skill_pay.py

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import os
import sys
from collections import Counter
import random
import re
from streamlit_lottie import st_lottie
import requests


# Use serp_api for real-time data fetching
import serp_api

# Load environment variables and Google API key for Gemini
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Attempt to import Gemini library; if unavailable, set gemini to None.
try:
    import gemini
except ImportError:
    gemini = None

# Set page configuration
st.set_page_config(
    page_title="Skills vs Pay | N3DN.Tech",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .page-title {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #6eb52f !important;
        margin-bottom: 1rem !important;
    }
    .section-header {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        color: #262730 !important;
    }
    .filter-container {
        background: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .insight-card {
        background-color: #e0e0ef;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #6eb52f !important;
    }
    .metric-label {
        font-size: 1rem !important;
        color: #262730 !important;
    }
</style>
""", unsafe_allow_html=True)

#000--------------Sidebar------------------------
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# All sidebar content is defined inside this block.
with st.sidebar:
    # Navigation widget for your top pages

    # Animation section: mountain-themed animation for "on top"
    st.markdown("### Explore Jobs & Salaries: Find the Right Opportunity for You!")
    # Replace the URL below with any mountain top or summit-themed Lottie animation.
    lottie_animation = load_lottie_url("https://lottie.host/3152497e-ca08-4b25-87ed-7029d7b6c4f6/fmUfViickm.json")
    if lottie_animation:
        st_lottie(lottie_animation, height=200, key="mountain_anim")
    else:
        st.error("Animation could not be loaded.")
#-------------------End here-----------------------------------------------

#------------------ends here-------------------

def extract_skills_vs_pay(jobs_data):
    """Extract skills vs pay data from the jobs dataframe"""
    if jobs_data is None or jobs_data.empty:
        return pd.DataFrame()
    
    has_skills = 'description_tokens' in jobs_data.columns
    has_salary = any(col in jobs_data.columns for col in ['salary_yearly', 'salary'])
    
    if not has_skills or not has_salary:
        return pd.DataFrame()
    
    try:
        salary_col = 'salary_yearly' if 'salary_yearly' in jobs_data.columns else 'salary'
        valid_jobs = jobs_data.dropna(subset=[salary_col, 'description_tokens'])
        if valid_jobs.empty:
            return pd.DataFrame()
        
        all_skills = []
        for tokens in valid_jobs['description_tokens']:
            if isinstance(tokens, str):
                skills = tokens.strip("[]").replace("'", "").split(", ")
                all_skills.extend([s for s in skills if s])
        
        skill_counts = Counter(all_skills)
        top_skills = [skill for skill, count in skill_counts.most_common(200)]
        
        skills_data = []
        for skill in top_skills:
            skill_jobs = valid_jobs[valid_jobs['description_tokens'].apply(
                lambda x: isinstance(x, str) and skill in x
            )]
            if len(skill_jobs) >= 10:
                avg_salary = skill_jobs[salary_col].mean()
                median_salary = skill_jobs[salary_col].median()
                job_count = len(skill_jobs)
                category = "Unknown"
                if any(tech in skill.lower() for tech in ["python", "r", "java", "c++", "javascript"]):
                    category = "Programming"
                elif any(tech in skill.lower() for tech in ["sql", "database", "postgresql"]):
                    category = "Data"
                elif any(tech in skill.lower() for tech in ["aws", "azure", "gcp", "cloud"]):
                    category = "Cloud"
                elif any(tech in skill.lower() for tech in ["ml", "ai", "machine learning", "tensorflow", "pytorch"]):
                    category = "AI"
                elif any(tech in skill.lower() for tech in ["react", "angular", "vue", "html", "css"]):
                    category = "Web Development"
                elif any(tech in skill.lower() for tech in ["docker", "kubernetes", "devops", "ci/cd"]):
                    category = "DevOps"
                elif any(tech in skill.lower() for tech in ["excel", "word", "powerpoint", "office"]):
                    category = "Office"
                elif any(tech in skill.lower() for tech in ["tableau", "power bi", "looker", "visualization"]):
                    category = "Visualization"
                
                avg_overall_salary = valid_jobs[salary_col].mean()
                salary_premium_pct = ((avg_salary / avg_overall_salary) - 1) * 100
                
                skills_data.append({
                    "Skill": skill,
                    "Category": category,
                    "Average Salary": avg_salary,
                    "Median Salary": median_salary,
                    "Salary Premium (%)": salary_premium_pct,
                    "Job Count": job_count
                })
        
        return pd.DataFrame(skills_data)
    
    except Exception as e:
        st.error(f"Error extracting skills vs pay data: {str(e)}")
        return pd.DataFrame()

def create_synthetic_skills_vs_pay():
    """Create synthetic skills vs pay data for demonstration purposes"""
    skills = [
        "Python", "SQL", "Java", "JavaScript", "AWS", "Azure", "Machine Learning",
        "Docker", "Kubernetes", "Excel", "Tableau", "Power BI", "Go", "C++", "Scala",
        "R", "Hadoop", "Spark", "Kafka", "Airflow", "TensorFlow", "PyTorch", "React",
        "Angular", "Vue.js", "Node.js", "Git", "Linux", "NoSQL", "MongoDB"
    ]
    
    categories = {
        "Python": "Programming", "SQL": "Data", "Java": "Programming",
        "JavaScript": "Programming", "AWS": "Cloud", "Azure": "Cloud",
        "Machine Learning": "AI", "Docker": "DevOps", "Kubernetes": "DevOps",
        "Excel": "Office", "Tableau": "Visualization", "Power BI": "Visualization",
        "Go": "Programming", "C++": "Programming", "Scala": "Programming",
        "R": "Programming", "Hadoop": "Data", "Spark": "Data",
        "Kafka": "Data", "Airflow": "DevOps", "TensorFlow": "AI",
        "PyTorch": "AI", "React": "Web Development", "Angular": "Web Development",
        "Vue.js": "Web Development", "Node.js": "Programming",
        "Git": "DevOps", "Linux": "DevOps", "NoSQL": "Data", "MongoDB": "Data"
    }
    
    category_base_salary = {
        "Programming": 120000,
        "Data": 125000,
        "Cloud": 130000,
        "AI": 150000,
        "Web Development": 115000,
        "DevOps": 135000,
        "Office": 95000,
        "Visualization": 110000,
        "Unknown": 100000
    }
    
    np.random.seed(42)
    skills_data = []
    
    for skill in skills:
        category = categories.get(skill, "Unknown")
        base_salary = category_base_salary[category]
        avg_salary = base_salary + np.random.normal(0, 15000)
        median_salary = avg_salary + np.random.normal(0, 5000)
        job_count = np.random.randint(50, 1000)
        avg_overall_salary = 110000
        salary_premium_pct = ((avg_salary / avg_overall_salary) - 1) * 100
        
        skills_data.append({
            "Skill": skill,
            "Category": category,
            "Average Salary": avg_salary,
            "Median Salary": median_salary,
            "Salary Premium (%)": salary_premium_pct,
            "Job Count": job_count
        })
    
    return pd.DataFrame(skills_data)

def load_jobs_data():
    """Fetch real-time job data using serp_api and return a combined dataframe."""
    if 'jobs_data' in st.session_state and st.session_state.jobs_data is not None:
        return st.session_state.jobs_data
    
    st.info("Fetching real-time job data. This may take a few minutes...")
    job_roles = ["Data Scientist", "Software Engineer", "Data Engineer"]
    locations = ["United States", "Remote"]
    all_data = []
    
    for role in job_roles:
        for location in locations:
            try:
                job_df = serp_api.get_job_data(query=role.lower(), location=location, limit=20)
                if not job_df.empty:
                    job_df["search_role"] = role
                    job_df["search_location"] = location
                    all_data.append(job_df)
            except Exception as e:
                st.error(f"Error fetching data for {role} in {location}: {str(e)}")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        st.session_state.jobs_data = combined_df
        return combined_df
    else:
        st.error("No real-time job data could be fetched. Please check your network or API settings.")
        return pd.DataFrame()

def generate_insight_recommendation(skill, salary):
    """
    Generate an insight recommendation using the Gemini API.
    Uses the Google API key loaded from the .env file.
    """
    prompt = (
        f"The trending skill is '{skill}' with an average salary of ${salary:,.0f} per year. "
        "Provide an insight recommendation discussing career prospects, market demand, "
        "and salary expectations for professionals with this skill."
    )
    
    # If the Gemini library is available and a Google API key is set, use it.
    if gemini and GOOGLE_API_KEY:
        try:
            # The exact call may vary based on the Gemini library’s documentation.
            response = gemini.generate_text(prompt, api_key=GOOGLE_API_KEY)
            return response.text
        except Exception as e:
            return f"Error generating insight: {e}"
    else:
        # Fallback: return a default recommendation.
        return (
            f"Based on current trends, '{skill}' appears to be in high demand with a competitive salary of ${salary:,.0f} per year. "
            "Investing in this skill could enhance your career prospects and market value."
        )

def main():
    st.markdown('<p class="page-title">Skills vs. Pay Analysis (Real-Time)</p>', unsafe_allow_html=True)
    
    if st.button("Fetch Real-Time Data"):
        st.session_state.jobs_data = None
        st.experimental_rerun()
    
    jobs_data = load_jobs_data()
    if jobs_data is None or jobs_data.empty:
        st.markdown(
            '<div class="empty-state">'
            '<h3>No Jobs Data Available</h3>'
            '<p>Please click "Fetch Real-Time Data" and ensure your API is working.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        return
    
    # -------- Filters Section --------
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">Filters</p>', unsafe_allow_html=True)
    
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        if "country" in jobs_data.columns:
            countries = sorted(jobs_data["country"].dropna().unique().tolist())
            selected_countries = st.multiselect("Select Countries", options=countries, default=countries)
            jobs_data = jobs_data[jobs_data["country"].isin(selected_countries)]
        else:
            selected_countries = []
    
    with col_filter2:
        st.write("")
    
    col_filter3, col_filter4 = st.columns(2)
    with col_filter3:
        df = extract_skills_vs_pay(jobs_data)
        if df.empty:
            df = create_synthetic_skills_vs_pay()
        categories = df["Category"].unique().tolist()
        selected_categories = st.multiselect(
            "Skill Categories",
            options=categories,
            default=categories
        )
    with col_filter4:
        sort_by = st.selectbox(
            "Sort By",
            options=["Average Salary", "Median Salary", "Salary Premium (%)", "Job Count"]
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    filtered_df = df[df["Category"].isin(selected_categories)]
    filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)
    
    if filtered_df.empty:
        st.warning("No skills match your filter criteria. Please adjust your filters.")
        return
    
    # Top Paying Skills Metrics
    st.markdown('<p class="section-header">Top Paying Skills</p>', unsafe_allow_html=True)
    avg_overall = filtered_df["Average Salary"].mean()
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Highest Paying Skill</p>', unsafe_allow_html=True)
        top_skill = filtered_df.iloc[0]["Skill"]
        top_salary = filtered_df.iloc[0]["Average Salary"]
        st.markdown(f'<p class="metric-value">{top_skill}</p>', unsafe_allow_html=True)
        st.markdown(f'<p>${top_salary:,.0f}/year</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with metric_cols[1]:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Highest Premium Skill</p>', unsafe_allow_html=True)
        premium_idx = filtered_df["Salary Premium (%)"].idxmax()
        premium_skill = filtered_df.loc[premium_idx, "Skill"]
        premium_pct = filtered_df.loc[premium_idx, "Salary Premium (%)"]
        st.markdown(f'<p class="metric-value">{premium_skill}</p>', unsafe_allow_html=True)
        st.markdown(f'<p>+{premium_pct:.1f}% above average</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with metric_cols[2]:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Top Category</p>', unsafe_allow_html=True)
        category_avg = filtered_df.groupby("Category")["Average Salary"].mean().reset_index()
        top_category = category_avg.sort_values(by="Average Salary", ascending=False).iloc[0]["Category"]
        top_category_salary = category_avg.sort_values(by="Average Salary", ascending=False).iloc[0]["Average Salary"]
        st.markdown(f'<p class="metric-value">{top_category}</p>', unsafe_allow_html=True)
        st.markdown(f'<p>${top_category_salary:,.0f}/year avg</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with metric_cols[3]:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Overall Average</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">${avg_overall:,.0f}</p>', unsafe_allow_html=True)
        st.markdown('<p>Across all skills</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Salary Comparison Section with Radio Option to toggle between Average Salary and Job Count
    st.markdown('<p class="section-header">Salary Comparison</p>', unsafe_allow_html=True)
    metric_option = st.radio(
        "Select Metric for Bar Chart",
        options=["Average Salary", "Job Count"],
        horizontal=True
    )
    
    chart_data = filtered_df.head(20).copy()
    if metric_option == "Average Salary":
        chart_data["Formatted Metric"] = chart_data["Average Salary"].apply(lambda x: f"${x:,.0f}")
        x_field = alt.X("Average Salary:Q", title="Average Salary ($)")
    else:
        chart_data["Formatted Metric"] = chart_data["Job Count"].apply(lambda x: f"{x}")
        x_field = alt.X("Job Count:Q", title="Job Count")
    
    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=x_field,
            y=alt.Y("Skill:N", sort="-x", title=None),
            color=alt.Color("Category:N", scale=alt.Scale(scheme='category10'), legend=alt.Legend(title="Category")),
            tooltip=[
                alt.Tooltip("Skill:N", title="Skill"),
                alt.Tooltip("Formatted Metric:N", title=metric_option),
                alt.Tooltip("Salary Premium (%):Q", title="Salary Premium (%)"),
                alt.Tooltip("Job Count:Q", title="Job Count")
            ]
        )
        .properties(height=min(500, len(chart_data) * 30))
        .interactive()
    )
    
    avg_line = (
        alt.Chart(pd.DataFrame({"Average": [avg_overall]}))
        .mark_rule(color="red", strokeDash=[3, 3])
        .encode(x="Average:Q")
    ) if metric_option == "Average Salary" else None
    
    if avg_line:
        st.altair_chart(chart + avg_line, use_container_width=True)
    else:
        st.altair_chart(chart, use_container_width=True)
    
    # Category Comparison Chart
    st.markdown('<p class="section-header">Category Comparison</p>', unsafe_allow_html=True)
    category_data = filtered_df.groupby("Category").agg({
        "Average Salary": "mean",
        "Job Count": "sum"
    }).reset_index()
    category_data["Formatted Salary"] = category_data["Average Salary"].apply(lambda x: f"${x:,.0f}")
    
    category_chart = (
        alt.Chart(category_data)
        .mark_bar()
        .encode(
            x=alt.X("Average Salary:Q", title="Average Salary ($)"),
            y=alt.Y("Category:N", sort="-x", title=None),
            color=alt.Color("Category:N", scale=alt.Scale(scheme='category10'), legend=None),
            tooltip=[
                alt.Tooltip("Category:N", title="Category"),
                alt.Tooltip("Formatted Salary:N", title="Average Salary"),
                alt.Tooltip("Job Count:Q", title="Total Jobs")
            ]
        )
        .properties(height=min(300, len(category_data) * 50))
        .interactive()
    )
    
    st.altair_chart(category_chart, use_container_width=True)
    
    # Insight Recommendation Section using Gemini
    # Determine the trending skill as the one with the highest job count.
    trending_row = filtered_df.sort_values(by="Job Count", ascending=False).iloc[0]
    trending_skill = trending_row["Skill"]
    trending_salary = trending_row["Average Salary"]
    insight = generate_insight_recommendation(trending_skill, trending_salary)
    
    st.markdown('<p class="section-header">Insight Recommendation</p>', unsafe_allow_html=True)
    st.info(insight)

if __name__ == '__main__':
    main()
