import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random

def get_job_data(query, location="United States", limit=100):
    """
    Get job data directly from Google Jobs search
    
    Args:
        query (str): Job search query (e.g., "data scientist")
        location (str): Location to search in
        limit (int): Number of results to return
    
    Returns:
        pd.DataFrame: DataFrame containing job data
    """
    # Format the search URL for Google Jobs
    base_url = "https://www.google.com/search"
    params = {
        "q": f"{query} jobs in {location}",
        "ibp": "1",  # Enable job search
        "num": min(limit, 100),
        "source": "hp",
        "tbm": "jobs"  # Specifically request job results
    }
    
    # Add headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }
    
    try:
        # Add random delay to avoid rate limiting
        time.sleep(random.uniform(2, 4))
        
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find job listings - updated selectors for Google Jobs
        job_cards = soup.find_all('div', {'class': ['iFjolb', 'gws-plugins-horizon-jobs__job-card']})
        
        job_data = []
        for card in job_cards:
            try:
                # Extract job details with updated selectors
                title_elem = card.find(['h2', 'h3'], {'class': ['BjJfJf', 'job-title']})
                company_elem = card.find(['div', 'span'], {'class': ['vNEEBe', 'company-name']})
                location_elem = card.find(['div', 'span'], {'class': ['Qk80Jf', 'location']})
                description_elem = card.find(['div', 'span'], {'class': ['HBvzbc', 'job-description']})
                
                if title_elem:
                    job_info = {
                        "title": title_elem.text.strip(),
                        "company_name": company_elem.text.strip() if company_elem else "",
                        "location": location_elem.text.strip() if location_elem else "",
                        "description": description_elem.text.strip() if description_elem else "",
                        "posted_at": "",
                        "schedule_type": "",
                        "work_from_home": "remote" in (description_elem.text.lower() if description_elem else ""),
                        "salary": extract_salary(description_elem.text if description_elem else ""),
                        "description_tokens": extract_skills(description_elem.text if description_elem else "")
                    }
                    job_data.append(job_info)
            except Exception as e:
                print(f"Error processing job card: {str(e)}")
                continue
        
        # If no jobs found with primary selectors, try alternative selectors
        if not job_data:
            # Try finding job cards by data attributes
            job_cards = soup.find_all('div', {'data-hveid': True})
            for card in job_cards:
                try:
                    # Try alternative selectors
                    title_elem = card.find(['h2', 'h3', 'div'], {'class': ['job-title', 'title', 'heading']})
                    company_elem = card.find(['div', 'span'], {'class': ['company-name', 'employer', 'company']})
                    location_elem = card.find(['div', 'span'], {'class': ['location', 'job-location', 'address']})
                    description_elem = card.find(['div', 'p'], {'class': ['description', 'job-description', 'summary']})
                    
                    if title_elem:
                        job_info = {
                            "title": title_elem.text.strip(),
                            "company_name": company_elem.text.strip() if company_elem else "",
                            "location": location_elem.text.strip() if location_elem else "",
                            "description": description_elem.text.strip() if description_elem else "",
                            "posted_at": "",
                            "schedule_type": "",
                            "work_from_home": "remote" in (description_elem.text.lower() if description_elem else ""),
                            "salary": extract_salary(description_elem.text if description_elem else ""),
                            "description_tokens": extract_skills(description_elem.text if description_elem else "")
                        }
                        job_data.append(job_info)
                except Exception as e:
                    print(f"Error processing alternative job card: {str(e)}")
                    continue
        
        # Convert to DataFrame
        df = pd.DataFrame(job_data)
        
        # Add timestamp
        df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Print debug information
        print(f"Found {len(job_data)} job listings")
        if len(job_data) == 0:
            print("HTML content preview:")
            print(soup.prettify()[:500])  # Print first 500 characters of HTML for debugging
            
            # Try to find any job-related elements
            job_elements = soup.find_all(['div', 'span'], string=lambda text: text and any(keyword in text.lower() for keyword in ['job', 'career', 'position', 'role']))
            if job_elements:
                print("\nFound potential job elements:")
                for elem in job_elements[:5]:
                    print(f"- {elem.text.strip()}")
        
        return df
    
    except Exception as e:
        print(f"Error fetching job data: {str(e)}")
        return pd.DataFrame()

def get_technology_trends(query="technology trends", limit=20):
    """
    Get technology trend data from Google News
    
    Args:
        query (str): Technology trend search query
        limit (int): Number of results to return
    
    Returns:
        pd.DataFrame: DataFrame containing trend data
    """
    base_url = "https://www.google.com/search"
    params = {
        "q": query,
        "tbm": "nws",  # News search
        "num": min(limit, 100)
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        time.sleep(random.uniform(1, 3))
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_cards = soup.find_all('div', {'class': 'g'})
        
        trend_data = []
        for card in news_cards:
            try:
                title_elem = card.find('h3')
                link_elem = card.find('a')
                source_elem = card.find('div', {'class': 'UPmit'})
                date_elem = card.find('div', {'class': 'LfVVr'})
                snippet_elem = card.find('div', {'class': 'GI74Re'})
                
                if title_elem and link_elem:
                    trend_info = {
                        "title": title_elem.text.strip(),
                        "link": link_elem['href'],
                        "source": source_elem.text.strip() if source_elem else "",
                        "date": date_elem.text.strip() if date_elem else "",
                        "snippet": snippet_elem.text.strip() if snippet_elem else "",
                        "thumbnail": ""  # Google News doesn't always show thumbnails
                    }
                    trend_data.append(trend_info)
            except Exception as e:
                print(f"Error processing news card: {str(e)}")
                continue
        
        df = pd.DataFrame(trend_data)
        df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return df
    
    except Exception as e:
        print(f"Error fetching technology trend data: {str(e)}")
        return pd.DataFrame()

def get_skill_salary_data(skills=None, location="United States"):
    """
    Get salary data for specific skills from Google search
    
    Args:
        skills (list): List of skills to search for
        location (str): Location to search in
    
    Returns:
        pd.DataFrame: DataFrame containing salary data per skill
    """
    if skills is None:
        skills = ["python", "java", "javascript", "sql", "aws", "docker", "kubernetes", "machine learning"]
    
    skill_data = []
    
    for skill in skills:
        query = f"{skill} salary {location}"
        base_url = "https://www.google.com/search"
        params = {"q": query}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            time.sleep(random.uniform(1, 3))
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            snippets = soup.find_all('div', {'class': 'VwiC3b'})
            
            salary_info = {
                "Skill": skill,
                "Average Salary": extract_salary_from_results(snippets),
                "Currency": "USD",
                "Location": location,
                "Description": f"Average salary for professionals with {skill} skills"
            }
            
            skill_data.append(salary_info)
            
        except Exception as e:
            print(f"Error fetching salary data for {skill}: {str(e)}")
    
    return pd.DataFrame(skill_data)

def build_composite_dataset(tech_roles=None, locations=None, save_to_csv=True):
    """
    Build a composite dataset from multiple queries and save to CSV
    
    Args:
        tech_roles (list): List of tech roles to query
        locations (list): List of locations to query
        save_to_csv (bool): Whether to save results to CSV
    
    Returns:
        pd.DataFrame: Combined dataset
    """
    if tech_roles is None:
        tech_roles = [
            "Data Scientist", "Software Engineer", "Data Engineer",
            "Machine Learning Engineer", "Frontend Developer", "Backend Developer",
            "DevOps Engineer", "Data Analyst", "Product Manager",
            "UI/UX Designer", "QA Engineer", "System Architect",
            "Network Engineer", "Digital Marketing Specialist", "IT Support"
        ]
    
    if locations is None:
        locations = [
            "United States", "Remote", "New York", "San Francisco",
            "Seattle", "Austin", "Boston", "Chicago", "London"
        ]
    
    all_data = []
    
    for role in tech_roles:
        for location in locations:
            print(f"Fetching data for {role} in {location}...")
            job_df = get_job_data(role, location, limit=20)
            
            if not job_df.empty:
                job_df["search_role"] = role
                job_df["search_location"] = location
                all_data.append(job_df)
            
            time.sleep(random.uniform(2, 4))
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        if save_to_csv:
            os.makedirs("data", exist_ok=True)
            output_file = os.path.join("data", "google_jobs_data.csv")
            combined_df.to_csv(output_file, index=False)
            print(f"Saved combined data to {output_file}")
        
        return combined_df
    else:
        print("No data collected")
        return pd.DataFrame()

def extract_salary(text):
    """
    Extract salary information from text
    
    Args:
        text (str): Text containing salary information
        
    Returns:
        dict: Extracted salary information
    """
    try:
        if not text:
            return None
            
        text = text.lower()
        
        if 'year' in text or 'annual' in text:
            period = 'yearly'
        elif 'month' in text or 'monthly' in text:
            period = 'monthly'
        elif 'hour' in text or 'hourly' in text:
            period = 'hourly'
        else:
            period = 'unknown'
        
        currency = 'USD'
        if '£' in text:
            currency = 'GBP'
        elif '€' in text:
            currency = 'EUR'
        elif '¥' in text:
            currency = 'JPY'
        
        import re
        numbers = re.findall(r'[\$£€¥]?\d+(?:,\d+)*(?:\.\d+)?k?', text)
        
        if len(numbers) >= 2:
            min_salary = float(numbers[0].replace('$', '').replace('£', '').replace('€', '').replace('¥', '').replace(',', ''))
            max_salary = float(numbers[1].replace('$', '').replace('£', '').replace('€', '').replace('¥', '').replace(',', ''))
            
            if 'k' in numbers[0].lower():
                min_salary *= 1000
            if 'k' in numbers[1].lower():
                max_salary *= 1000
                
            if period == 'hourly':
                min_salary = min_salary * 40 * 52
                max_salary = max_salary * 40 * 52
                period = 'yearly'
            elif period == 'monthly':
                min_salary = min_salary * 12
                max_salary = max_salary * 12
                period = 'yearly'
                
        elif len(numbers) == 1:
            min_salary = max_salary = float(numbers[0].replace('$', '').replace('£', '').replace('€', '').replace('¥', '').replace(',', ''))
            if 'k' in numbers[0].lower():
                min_salary = max_salary = min_salary * 1000
        else:
            return None
        
        return {
            'min': min_salary,
            'max': max_salary,
            'period': period,
            'currency': currency
        }
    
    except Exception as e:
        print(f"Error extracting salary: {str(e)}")
        return None

def extract_skills(description):
    """
    Extract skills from job description using keyword matching
    
    Args:
        description (str): Job description text
        
    Returns:
        list: List of extracted skills
    """
    tech_skills = {
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "swift", "kotlin", "go", "rust",
        "r", "matlab", "scala", "perl", "shell", "bash",
        "html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask", "spring", "asp.net",
        "jquery", "bootstrap", "sass", "less", "webpack", "next.js", "nuxt.js",
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "oracle", "sqlite",
        "dynamodb", "neo4j", "firebase", "bigquery", "snowflake",
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "ansible", "circleci", "git",
        "prometheus", "grafana", "elk stack", "splunk", "new relic", "datadog",
        "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
        "data analysis", "statistics", "spss", "tableau", "power bi", "looker", "d3.js", "matplotlib",
        "seaborn", "jupyter", "hadoop", "spark", "kafka", "airflow", "dbt",
        "react native", "flutter", "ios", "android", "xcode", "android studio",
        "security", "penetration testing", "ethical hacking", "firewall", "vpn", "ssl", "encryption",
        "agile", "scrum", "jira", "confluence", "trello", "asana", "project management",
        "rest api", "graphql", "microservices", "ci/cd", "blockchain", "web3", "solidity",
        "unity", "unreal engine", "game development", "ar", "vr", "iot", "edge computing",
        "communication", "leadership", "problem solving", "teamwork", "office"
    }
    
    if not description:
        return []
    
    desc_lower = description.lower()
    found_skills = []
    
    for skill in tech_skills:
        if skill in desc_lower:
            if skill == 'r':
                if not any(x in desc_lower for x in ['ruby', 'rust', 'react']):
                    found_skills.append(skill)
            else:
                found_skills.append(skill)
    
    return sorted(found_skills)

def extract_salary_from_results(snippets):
    """
    Extract salary information from search result snippets
    
    Args:
        snippets (list): List of BeautifulSoup elements containing snippets
        
    Returns:
        float: Average salary or None if not found
    """
    try:
        salary_sum = 0
        salary_count = 0
        
        for snippet in snippets:
            text = snippet.text.lower()
            if "salary" in text:
                import re
                numbers = re.findall(r'\$?\d+(?:,\d+)*(?:\.\d+)?k?', text)
                for num in numbers:
                    try:
                        num = num.replace('$', '').replace(',', '')
                        if num.endswith('k'):
                            num = float(num[:-1]) * 1000
                        else:
                            num = float(num)
                        
                        if 10000 <= num <= 500000:
                            salary_sum += num
                            salary_count += 1
                    except ValueError:
                        continue
        
        return round(salary_sum / salary_count, 2) if salary_count > 0 else None
    
    except Exception as e:
        print(f"Error extracting salary from results: {str(e)}")
        return None
