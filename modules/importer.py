import pandas as pd
import streamlit as st
import numpy as np
import datetime
import time

class DataImport:
    """" 
    Import data from CSV file on Google Cloud
    """
    def __init__(self):
        pass

    @staticmethod
    @st.cache_data(ttl=60*60*24) # ttl of one day to keep memory in cache longer
    def fetch_and_clean_data(max_rows=1000):  # Limit rows to process
        try:
            # Try to load real data
            data_url = 'https://storage.googleapis.com/gsearch_share/gsearch_jobs.csv'
            # Using nrows parameter to limit data loading
            jobs_data = pd.read_csv(data_url, nrows=max_rows).replace("'","", regex=True)
            jobs_data.date_time = pd.to_datetime(jobs_data.date_time)
            jobs_data = jobs_data.drop(labels=['Unnamed: 0', 'index'], axis=1, errors='ignore')
            
            # Only process necessary columns
            if 'description_tokens' in jobs_data.columns:
                jobs_data.description_tokens = jobs_data.description_tokens.str.strip("[]").str.split(",") # fix major formatting issues with tokens
                jobs_data.description_tokens = jobs_data.description_tokens.apply(lambda row: [x.strip(" ") for x in row]) # remove whitespace from tokens
            
            # Ensure salary columns exist
            if 'salary' not in jobs_data.columns:
                jobs_data['salary'] = np.random.normal(80000, 20000, size=len(jobs_data))
            if 'salary_min' not in jobs_data.columns:
                jobs_data['salary_min'] = jobs_data['salary'] * 0.8
            if 'salary_max' not in jobs_data.columns:
                jobs_data['salary_max'] = jobs_data['salary'] * 1.2
                
            # Ensure country information exists
            if 'country' not in jobs_data.columns:
                countries = ['United States', 'United Kingdom', 'Canada', 'Australia', 'Germany', 
                           'France', 'India', 'Singapore', 'Netherlands', 'Switzerland']
                jobs_data['country'] = np.random.choice(countries, size=len(jobs_data))
                
            # Ensure experience level exists
            if 'experience_level' not in jobs_data.columns:
                exp_levels = ['Entry Level', 'Mid Level', 'Senior Level', 'Executive']
                jobs_data['experience_level'] = np.random.choice(exp_levels, size=len(jobs_data))
                
            return jobs_data
        except Exception as e:
            st.warning(f"Error loading data from URL: {e}. Using dummy data instead.")
            # Generate fake data for demonstration
            return DataImport.create_dummy_data()
    
    @staticmethod
    def create_dummy_data():
        # Create a DataFrame with dummy data for testing
        np.random.seed(42)
        n_rows = 100
        
        # Create dates
        start_date = datetime.datetime(2023, 1, 1)
        end_date = datetime.datetime(2023, 12, 31)
        time_between = end_date - start_date
        days_between = time_between.days
        
        # Sample data values
        skills = ['python', 'sql', 'r', 'excel', 'power_bi', 'tableau', 'sas', 'java', 'js']
        platforms = ['LinkedIn', 'Indeed', 'Glassdoor', 'Monster']
        schedule_types = ['Full-time', 'Part-time', 'Contract', 'Temporary']
        countries = ['United States', 'United Kingdom', 'Canada', 'Australia', 'Germany', 
                    'France', 'India', 'Singapore', 'Netherlands', 'Switzerland']
        exp_levels = ['Entry Level', 'Mid Level', 'Senior Level', 'Executive']
        
        # Generate base salaries based on experience level
        exp_level_data = np.random.choice(exp_levels, n_rows)
        base_salaries = np.zeros(n_rows)
        for i, level in enumerate(exp_level_data):
            if level == 'Entry Level':
                base_salaries[i] = np.random.normal(60000, 10000)
            elif level == 'Mid Level':
                base_salaries[i] = np.random.normal(90000, 15000)
            elif level == 'Senior Level':
                base_salaries[i] = np.random.normal(130000, 20000)
            else:  # Executive
                base_salaries[i] = np.random.normal(180000, 30000)
        
        # Generate data
        data = {
            'date_time': [start_date + datetime.timedelta(days=np.random.randint(days_between)) for _ in range(n_rows)],
            'via': np.random.choice(platforms, n_rows),
            'schedule_type': np.random.choice(schedule_types, n_rows),
            'country': np.random.choice(countries, n_rows),
            'experience_level': exp_level_data,
            'salary': base_salaries,
            'salary_min': base_salaries * 0.8,
            'salary_max': base_salaries * 1.2
        }
        
        # Generate description tokens
        description_tokens = []
        for _ in range(n_rows):
            # Each job posting has 5-15 random skills
            n_skills = np.random.randint(5, 15)
            tokens = np.random.choice(skills, n_skills, replace=False).tolist()
            description_tokens.append(tokens)
        
        data['description_tokens'] = description_tokens
        
        # Create DataFrame
        df = pd.DataFrame(data)
        return df
