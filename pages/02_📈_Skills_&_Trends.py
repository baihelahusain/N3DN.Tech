# pages/02_skill_trend.py

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import os
import sys
from collections import Counter
import re
from datetime import datetime, timedelta
import requests
from streamlit_lottie import st_lottie

# Remove the utils import since we now rely on the static data via importer
from modules import importer

# Set page configuration
st.set_page_config(
    page_title="Skill Trends | N3DN.Tech",
    page_icon="📈",
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
    .insight-card {
        background-color: #e0e0ef;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .trend-up {
        color: #28a745;
        font-weight: bold;
    }
    .trend-down {
        color: #dc3545;
        font-weight: bold;
    }
    .trend-stable {
        color: #ffc107;
        font-weight: bold;
    }

    .metric-big {
        font-size: 2rem; /* Reduced font size from 2.5rem to 2rem */
        font-weight: bold;
        color: #6eb52f;
        text-align: center;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
        text-align: center;
    }
    .empty-state {
        text-align: center;
        padding: 40px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)
#000 Side bar 0000-----------------------------------------------------------
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# All sidebar content is defined within this block.
with st.sidebar:
    # Navigation widget (assuming you want to keep your 5-page nav)

    st.markdown("### Trends on the Rise!")
    # This Lottie animation is related to upward growth; feel free to change the URL.
    lottie_animation = load_lottie_url("https://lottie.host/97f8c6bb-f8a3-47ec-ada3-a60055ff9136/VR5hJGMtaW.json")
    if lottie_animation:
        st_lottie(lottie_animation, height=200, key="trending_anim")
    else:
        st.error("Animation could not be loaded.")
#000000---------------------------end------------------------0000

def extract_skill_trends(jobs_data):
    """Extract skill trends data from the jobs dataframe"""
    if jobs_data is None or jobs_data.empty or 'description_tokens' not in jobs_data.columns:
        return pd.DataFrame()
    
    try:
        if 'posted_at' in jobs_data.columns:
            jobs_data['posted_date'] = pd.to_datetime(jobs_data['posted_at'], errors='coerce')
            valid_dates = jobs_data.dropna(subset=['posted_date'])
            if not valid_dates.empty:
                min_date = valid_dates['posted_date'].min()
                max_date = valid_dates['posted_date'].max()
                total_days = (max_date - min_date).days
                if total_days > 180:  # More than 6 months of data
                    periods = []
                    current_date = min_date
                    while current_date <= max_date:
                        next_date = current_date + timedelta(days=90)  # Approximately a quarter
                        period_name = current_date.strftime("%Y-Q%q").replace("%q", str((current_date.month-1)//3+1))
                        periods.append((period_name, current_date, next_date))
                        current_date = next_date
                    
                    skill_trends = []
                    for period_name, start_date, end_date in periods:
                        period_jobs = valid_dates[(valid_dates['posted_date'] >= start_date) & 
                                                  (valid_dates['posted_date'] < end_date)]
                        if not period_jobs.empty:
                            period_skills = []
                            for tokens in period_jobs['description_tokens'].dropna():
                                if isinstance(tokens, str):
                                    skills = tokens.strip("[]").replace("'", "").split(", ")
                                    period_skills.extend([s for s in skills if s])
                            skill_counts = Counter(period_skills)
                            total_jobs = len(period_jobs)
                            for skill, count in skill_counts.items():
                                popularity = (count / total_jobs) * 100
                                if popularity >= 1:
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
                                    
                                    skill_trends.append({
                                        "Skill": skill,
                                        "Category": category,
                                        "Period": period_name,
                                        "Popularity": popularity
                                    })
                    trend_df = pd.DataFrame(skill_trends)
                    if not trend_df.empty:
                        pivot_df = trend_df.pivot_table(
                            index=["Skill", "Category"],
                            columns="Period",
                            values="Popularity",
                            aggfunc='mean'
                        ).reset_index()
                        for period_name, _, _ in periods:
                            if period_name in pivot_df.columns:
                                pivot_df[period_name] = pivot_df[period_name].fillna(0)
                        all_periods = [p[0] for p in periods]
                        for i in range(1, len(all_periods)):
                            current = all_periods[i]
                            previous = all_periods[i-1]
                            if current in pivot_df.columns and previous in pivot_df.columns:
                                growth_col = f"{previous}_to_{current}_Growth"
                                pivot_df[growth_col] = ((pivot_df[current] - pivot_df[previous]) / 
                                                       pivot_df[previous].replace(0, 0.1)) * 100
                        return pivot_df
    except Exception as e:
        st.error(f"Error extracting skill trends: {str(e)}")
    return create_synthetic_trends()

def create_synthetic_trends():
    """Create synthetic trends data for demonstration purposes"""
    skills = ["Python", "SQL", "Excel", "Data Analysis", "Machine Learning", 
              "Tableau", "Power BI", "R", "AWS", "Azure", "JavaScript",
              "Java", "C++", "Project Management", "Communication"]
    categories = {
        "Python": "Programming", "SQL": "Data", "Excel": "Office",
        "Data Analysis": "Data", "Machine Learning": "AI",
        "Tableau": "Visualization", "Power BI": "Visualization", "R": "Programming",
        "AWS": "Cloud", "Azure": "Cloud", "JavaScript": "Programming",
        "Java": "Programming", "C++": "Programming",
        "Project Management": "Soft Skills", "Communication": "Soft Skills"
    }
    periods = ["2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4", "2023-Q1", "2023-Q2","2024-Q1","2024-Q2" "2025-Q1"]
    np.random.seed(42)
    data = []
    for skill in skills:
        base_value = np.random.uniform(10, 50)
        trend_type = np.random.choice(["rising", "stable", "falling"])
        row = {"Skill": skill, "Category": categories[skill]}
        for i, period in enumerate(periods):
            if trend_type == "rising":
                value = base_value + i * np.random.uniform(2, 5)
            elif trend_type == "stable":
                value = base_value + np.random.uniform(-3, 3)
            else:
                value = base_value - i * np.random.uniform(1, 3)
            value += np.random.uniform(-2, 2)
            value = max(0, value)
            row[period] = value
        data.append(row)
    df = pd.DataFrame(data)
    for i in range(1, len(periods)):
        current = periods[i]
        previous = periods[i-1]
        growth_col = f"{previous}_to_{current}_Growth"
        df[growth_col] = ((df[current] - df[previous]) / df[previous]) * 100
    return df

def load_jobs_data():
    """Load jobs data from session state or from CSV via importer"""
    if 'jobs_data' in st.session_state and st.session_state.jobs_data is not None:
        return st.session_state.jobs_data
    else:
        data = importer.DataImport.fetch_and_clean_data(max_rows=1000)
        st.session_state.jobs_data = data
        return data

def main():
    st.markdown('<p class="page-title">Skill Trends Analysis</p>', unsafe_allow_html=True)
    
    # Load jobs data
    jobs_data = load_jobs_data()
    if jobs_data is None or jobs_data.empty:
        st.markdown(
            '<div class="empty-state">'
            '<h3>No Jobs Data Available</h3>'
            '<p>Please load job data on the home page.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        return
    
    # Extract trend data
    df = extract_skill_trends(jobs_data)
    if df.empty:
        st.markdown(
            '<div class="empty-state">'
            '<h3>Could Not Extract Trend Data</h3>'
            '<p>Using synthetic data for demonstration.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        df = create_synthetic_trends()
    
    # Filters section
    st.markdown('<p class="section-header">Analyze Skill Trends</p>', unsafe_allow_html=True)
    categories = df["Category"].unique().tolist()
    periods = [col for col in df.columns if col not in ["Skill", "Category"] and not col.endswith("Growth")]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_categories = st.multiselect(
            "Skill Categories",
            options=categories,
            default=["Programming", "Data", "AI"] if all(cat in categories for cat in ["Programming", "Data", "AI"]) else categories[:3]
        )
    with col2:
        top_skills = df.sort_values(by=periods[-1] if periods else "Skill", ascending=False).head(10)["Skill"].tolist()
        selected_skills = st.multiselect(
            "Select Skills to Compare",
            options=df["Skill"].unique().tolist(),
            default=top_skills[:5]
        )
    with col3:
        trend_type = st.radio(
            "Trend Analysis Type",
            options=["Skills Growth", "Category Comparison", "Period-over-Period", "Both"],
            horizontal=True
        )
    
    filtered_df = df.copy()
    if selected_categories:
        filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]
    if selected_skills:
        filtered_df = filtered_df[filtered_df["Skill"].isin(selected_skills)]
    
    if filtered_df.empty:
        st.warning("No data matches your filter criteria. Please adjust your filters.")
        return
    
    # Trend Analysis Metrics (unchanged)
    st.markdown('<p class="section-header">Trend Highlights</p>', unsafe_allow_html=True)
    metric_cols = st.columns(4)
    growth_cols = [col for col in df.columns if col.endswith("Growth")]
    
    if growth_cols:
        latest_growth = growth_cols[-1]
        growth_df = filtered_df.sort_values(by=latest_growth, ascending=False)
        if not growth_df.empty:
            fastest_growing_skill = growth_df.iloc[0]["Skill"]
            max_growth_rate = growth_df.iloc[0][latest_growth]
            with metric_cols[0]:
                st.markdown('<div class="insight-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-big">{fastest_growing_skill}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-label">Fastest Growing Skill</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="trend-up">+{max_growth_rate:.1f}% growth</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        if len(growth_cols) >= 2:
            consistency_df = filtered_df.copy()
            consistency_df["Growth_StdDev"] = consistency_df[growth_cols].std(axis=1)
            valid_consistency = consistency_df.dropna(subset=["Growth_StdDev"])
            if not valid_consistency.empty:
                min_stddev_idx = valid_consistency["Growth_StdDev"].idxmin()
                most_consistent_skill = valid_consistency.loc[min_stddev_idx, "Skill"]
                consistency_value = valid_consistency.loc[min_stddev_idx, "Growth_StdDev"]
                with metric_cols[1]:
                    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-big">{most_consistent_skill}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-label">Most Consistent Skill</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="trend-stable">{consistency_value:.1f}% std dev</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        if periods:
            latest_period = periods[-1]
            latest_adoption_df = filtered_df.sort_values(by=latest_period, ascending=False)
            if not latest_adoption_df.empty:
                highest_adoption_skill = latest_adoption_df.iloc[0]["Skill"]
                adoption_rate = latest_adoption_df.iloc[0][latest_period]
                with metric_cols[2]:
                    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-big">{highest_adoption_skill}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-label">Highest Adoption</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="trend-up">{adoption_rate:.1f}% adoption</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        if growth_cols:
            declining_df = filtered_df[filtered_df[latest_growth] < 0].sort_values(by=latest_growth)
            if not declining_df.empty:
                most_declining_skill = declining_df.iloc[0]["Skill"]
                decline_rate = declining_df.iloc[0][latest_growth]
                with metric_cols[3]:
                    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-big">{most_declining_skill}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-label">Declining Skill</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="trend-down">{decline_rate:.1f}% decline</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
    
    # Trend Visualization Section
    st.markdown('<p class="section-header">Trend Visualization</p>', unsafe_allow_html=True)
    
    if trend_type == "Skills Growth":
        # Prepare data for line chart
        chart_data = []
        for _, row in filtered_df.iterrows():
            skill = row["Skill"]
            category = row["Category"]
            for period in periods:
                popularity = row[period]
                chart_data.append({
                    "Skill": skill,
                    "Category": category,
                    "Period": period,
                    "Adoption Rate": popularity
                })
        chart_df = pd.DataFrame(chart_data)
        if not chart_df.empty:
            skills_chart = (
                alt.Chart(chart_df)
                .mark_line(point=True)
                .encode(
                    x=alt.X("Period:O", title="Time Period"),
                    y=alt.Y("Adoption Rate:Q", title="Adoption Rate (%)"),
                    color=alt.Color("Skill:N", legend=alt.Legend(title="Skill")),
                    tooltip=["Skill", "Period", "Adoption Rate", "Category"]
                )
                .properties(height=500)
                .interactive()
            )
            st.altair_chart(skills_chart, use_container_width=True)
    elif trend_type == "Category Comparison":
        category_data = []
        for category in selected_categories:
            category_df = filtered_df[filtered_df["Category"] == category]
            if not category_df.empty:
                for period in periods:
                    avg_adoption = category_df[period].mean()
                    category_data.append({
                        "Category": category,
                        "Period": period,
                        "Average Adoption": avg_adoption
                    })
        category_chart_df = pd.DataFrame(category_data)
        if not category_chart_df.empty:
            category_chart = (
                alt.Chart(category_chart_df)
                .mark_line(point=True)
                .encode(
                    x=alt.X("Period:O", title="Time Period"),
                    y=alt.Y("Average Adoption:Q", title="Average Adoption Rate (%)"),
                    color=alt.Color("Category:N", legend=alt.Legend(title="Category")),
                    tooltip=["Category", "Period", "Average Adoption"]
                )
                .properties(height=500)
                .interactive()
            )
            st.altair_chart(category_chart, use_container_width=True)
        else:
            st.warning("Not enough data for category comparison.")
    elif trend_type == "Period-over-Period":
        if len(periods) >= 2 and growth_cols:
            pop_data = []
            for _, row in filtered_df.iterrows():
                skill = row["Skill"]
                category = row["Category"]
                for growth_col in growth_cols:
                    period = growth_col.replace("_Growth", "")
                    growth_rate = row[growth_col]
                    pop_data.append({
                        "Skill": skill,
                        "Category": category,
                        "Period": period,
                        "Growth Rate": growth_rate
                    })
            pop_chart_df = pd.DataFrame(pop_data)
            if not pop_chart_df.empty:
                # Create horizontal bar chart
                pop_chart = (
                    alt.Chart(pop_chart_df)
                    .mark_bar()
                    .encode(
                        y=alt.Y("Period:O", title="Period"),
                        x=alt.X("Growth Rate:Q", title="Growth Rate (%)"),
                        color=alt.Color("Skill:N", legend=alt.Legend(title="Skill")),
                        tooltip=["Skill", "Period", "Growth Rate", "Category"]
                    )
                    .properties(height=500)
                    .interactive()
                )
                st.altair_chart(pop_chart, use_container_width=True)
            else:
                st.warning("Not enough data for period-over-period analysis.")
        else:
            st.warning("Need at least two periods of data for period-over-period analysis.")
    elif trend_type == "Both":
        # Prepare data for line chart (Skills Growth)
        chart_data = []
        for _, row in filtered_df.iterrows():
            skill = row["Skill"]
            category = row["Category"]
            for period in periods:
                popularity = row[period]
                chart_data.append({
                    "Skill": skill,
                    "Category": category,
                    "Period": period,
                    "Adoption Rate": popularity
                })
        chart_df = pd.DataFrame(chart_data)
        
        # Prepare data for horizontal bar chart (Period-over-Period)
        pop_data = []
        if len(periods) >= 2 and growth_cols:
            for _, row in filtered_df.iterrows():
                skill = row["Skill"]
                category = row["Category"]
                for growth_col in growth_cols:
                    period = growth_col.replace("_Growth", "")
                    growth_rate = row[growth_col]
                    pop_data.append({
                        "Skill": skill,
                        "Category": category,
                        "Period": period,
                        "Growth Rate": growth_rate
                    })
            pop_chart_df = pd.DataFrame(pop_data)
        else:
            pop_chart_df = pd.DataFrame()
        
        # Display both visualizations side by side
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("<b>Line Chart: Skill Adoption Over Time</b>", unsafe_allow_html=True)
            if not chart_df.empty:
                skills_chart = (
                    alt.Chart(chart_df)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X("Period:O", title="Time Period"),
                        y=alt.Y("Adoption Rate:Q", title="Adoption Rate (%)"),
                        color=alt.Color("Skill:N", legend=alt.Legend(title="Skill")),
                        tooltip=["Skill", "Period", "Adoption Rate", "Category"]
                    )
                    .properties(height=500)
                    .interactive()
                )
                st.altair_chart(skills_chart, use_container_width=True)
            else:
                st.warning("No data available for line chart.")
        with col_right:
            st.markdown("<b>Horizontal Bar Chart: Period-over-Period Growth</b>", unsafe_allow_html=True)
            if not pop_chart_df.empty:
                pop_chart = (
                    alt.Chart(pop_chart_df)
                    .mark_bar()
                    .encode(
                        y=alt.Y("Period:O", title="Period"),
                        x=alt.X("Growth Rate:Q", title="Growth Rate (%)"),
                        color=alt.Color("Skill:N", legend=alt.Legend(title="Skill")),
                        tooltip=["Skill", "Period", "Growth Rate", "Category"]
                    )
                    .properties(height=500)
                    .interactive()
                )
                st.altair_chart(pop_chart, use_container_width=True)
            else:
                st.warning("No data available for bar chart.")
    
    # Detailed Skill Analysis (unchanged)
    st.markdown('<p class="section-header">Detailed Skill Analysis</p>', unsafe_allow_html=True)
    selected_skill = st.selectbox(
        "Select a Skill for Detailed Analysis",
        options=filtered_df["Skill"].unique().tolist()
    )
    if selected_skill:
        skill_df = filtered_df[filtered_df["Skill"] == selected_skill]
        if not skill_df.empty:
            st.markdown('<div class="insight-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([2, 1])
            with col1:
                skill_trend_data = []
                for period in periods:
                    popularity = skill_df[period].iloc[0]
                    skill_trend_data.append({
                        "Period": period,
                        "Adoption Rate": popularity
                    })
                skill_trend_df = pd.DataFrame(skill_trend_data)
                skill_trend_chart = (
                    alt.Chart(skill_trend_df)
                    .mark_line(point=True, color='#6eb52f')
                    .encode(
                        x=alt.X("Period:O", title="Period"),
                        y=alt.Y("Adoption Rate:Q", title="Adoption Rate (%)"),
                        tooltip=["Period", "Adoption Rate"]
                    )
                    .properties(height=300)
                    .interactive()
                )
                st.altair_chart(skill_trend_chart, use_container_width=True)
            with col2:
                if len(periods) >= 2:
                    first_period = periods[0]
                    last_period = periods[-1]
                    first_val = skill_df[first_period].iloc[0]
                    last_val = skill_df[last_period].iloc[0]
                    total_growth = ((last_val - first_val) / first_val) * 100 if first_val > 0 else 0
                    num_periods = len(periods)
                    cagr = ((last_val / first_val) ** (1 / num_periods)) - 1 if first_val > 0 else 0
                    cagr_percent = cagr * 100
                    st.markdown(f"### {selected_skill}")
                    st.markdown(f"**Category:** {skill_df['Category'].iloc[0]}")
                    st.markdown(f"**Current Adoption:** {last_val:.1f}%")
                    st.markdown(f"**Total Growth ({first_period} to {last_period}):** {total_growth:.1f}%")
                    st.markdown(f"**Average Period Growth Rate:** {cagr_percent:.1f}%")
                    trend_class = "trend-up" if cagr_percent > 5 else "trend-stable" if cagr_percent > 0 else "trend-down"
                    trend_label = "Strong Growth" if cagr_percent > 5 else "Stable" if cagr_percent > 0 else "Declining"
                    st.markdown(f"**Trend Classification:** <span class='{trend_class}'>{trend_label}</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Future trends prediction and download option (unchanged)
    st.markdown('<p class="section-header">Future Trends Prediction</p>', unsafe_allow_html=True)
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    emerging_techs = []
    saturating_techs = []
    if growth_cols and len(periods) >= 2:
        for _, row in filtered_df.iterrows():
            skill = row["Skill"]
            if len(growth_cols) >= 2:
                recent_growth_cols = growth_cols[-2:]
                recent_growth_rates = [row[col] for col in recent_growth_cols]
                if len(recent_growth_rates) > 1 and recent_growth_rates[-1] > recent_growth_rates[0] and recent_growth_rates[-1] > 10:
                    emerging_techs.append((skill, recent_growth_rates[-1]))
                latest_period = periods[-1]
                if len(recent_growth_rates) > 1 and recent_growth_rates[-1] < recent_growth_rates[0] and row[latest_period] > 25:
                    saturating_techs.append((skill, row[latest_period]))
    emerging_techs = sorted(emerging_techs, key=lambda x: x[1], reverse=True)[:5]
    saturating_techs = sorted(saturating_techs, key=lambda x: x[1], reverse=True)[:5]
    col_future1, col_future2 = st.columns(2)
    with col_future1:
        st.markdown("### Emerging Technologies")
        if emerging_techs:
            for skill, growth in emerging_techs:
                st.markdown(f"- **{skill}**: +{growth:.1f}% recent growth")
        else:
            st.markdown("No clear emerging technologies identified.")
    with col_future2:
        st.markdown("### Maturing Technologies")
        if saturating_techs:
            for skill, adoption in saturating_techs:
                st.markdown(f"- **{skill}**: {adoption:.1f}% adoption, growth slowing")
        else:
            st.markdown("No clear maturing technologies identified.")
    st.markdown("### Industry Forecast")
    top_categories = selected_categories if selected_categories else categories[:3]
    st.markdown(f"""
    Based on the trend analysis, we predict the following developments:
    
    1. **Short-term trends (next period)**: {', '.join([tech[0] for tech in emerging_techs[:3]]) if emerging_techs else "No clear emerging trends"} will see continued strong growth.
    2. **Skills reaching saturation**: {', '.join([tech[0] for tech in saturating_techs[:3]]) if saturating_techs else "No clear saturating trends"} are becoming standardized.
    3. **Key watch areas**: Pay attention to emerging applications in {', '.join(top_categories)} that combine multiple technologies.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        "Download Filtered Trend Data",
        csv,
        f"skill_trends.csv",
        "text/csv",
        key='download-csv'
    )

if __name__ == "__main__":
    main()
