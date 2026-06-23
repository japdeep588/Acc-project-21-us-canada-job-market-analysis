import pandas as pd
import os

# =============================================
# PATHS SETUP
# =============================================
base_path = "Datasets"
output_path = "Cleaned_Data"
os.makedirs(output_path, exist_ok=True)

# =============================================
# LOAD ALL DATASETS
# =============================================
print("Loading datasets...")
df1 = pd.read_csv(f"{base_path}/gsearch_jobs.csv")
df2 = pd.read_csv(f"{base_path}/salaries.csv")
df3a = pd.read_csv(f"{base_path}/linkedin_job_postings.csv")
df3b = pd.read_csv(f"{base_path}/job_skills.csv")

print(f"Dataset 1 loaded: {len(df1)} rows")
print(f"Dataset 2 loaded: {len(df2)} rows")
print(f"Dataset 3A loaded: {len(df3a)} rows")
print(f"Dataset 3B loaded: {len(df3b)} rows")
print("All datasets loaded successfully!")





# =============================================
# DATASET 1 - CLEANING (gsearch_jobs.csv)
# =============================================
print("\n--- Cleaning Dataset 1 ---")

# Step 1: Drop useless columns
cols_to_drop = [
    'Unnamed: 0', 'index', 'thumbnail', 'commute_time',
    'via', 'extensions', 'description', 'salary_pay',
    'salary_rate', 'job_id'
]
df1.drop(columns=[c for c in cols_to_drop if c in df1.columns], inplace=True)
print("Useless columns dropped")

# Step 2: Filter only US Data Analyst & AI related jobs
keywords = ['data analyst', 'data scientist', 'ai analyst', 'machine learning',
            'business intelligence', 'bi analyst', 'data engineer', 
            'ai engineer', 'analytics']
pattern = '|'.join(keywords)
df1 = df1[df1['title'].str.lower().str.contains(pattern, na=False)]
print(f"After filtering relevant jobs: {len(df1)} rows")

# Step 3: Fix work_from_home column
df1['work_from_home'] = df1['work_from_home'].fillna(False)
df1['work_type'] = df1['work_from_home'].map({True: 'Remote', False: 'Onsite'})
df1.drop(columns=['work_from_home'], inplace=True)
print("Work type column fixed")

# Step 4: Fix schedule_type nulls
df1['schedule_type'] = df1['schedule_type'].fillna('Unknown')
print("Schedule type nulls fixed")

# Step 5: Drop rows where location is null
df1.dropna(subset=['location'], inplace=True)
print(f"After dropping null locations: {len(df1)} rows")

# Step 6: Extract year and month from date_time
df1['date_time'] = pd.to_datetime(df1['date_time'], errors='coerce')
df1['year'] = df1['date_time'].dt.year
df1['month'] = df1['date_time'].dt.month
df1['month_name'] = df1['date_time'].dt.strftime('%B')
print("Year and month extracted")

# Step 7: Add job_category column
def categorize_job(title):
    title = str(title).lower()
    if 'machine learning' in title or 'ml engineer' in title:
        return 'Machine Learning Engineer'
    elif 'ai engineer' in title or 'ai analyst' in title or 'artificial intelligence' in title:
        return 'AI Engineer'
    elif 'data scientist' in title:
        return 'Data Scientist'
    elif 'data engineer' in title:
        return 'Data Engineer'
    elif 'business intelligence' in title or 'bi analyst' in title or 'bi developer' in title:
        return 'BI Analyst'
    elif 'data analyst' in title:
        return 'Data Analyst'
    else:
        return 'Analytics'

df1['job_category'] = df1['title'].apply(categorize_job)
print("Job category column added")
print("Job categories:\n", df1['job_category'].value_counts())

# Step 8: Clean salary - keep only salary_standardized
df1['salary_standardized'] = pd.to_numeric(df1['salary_standardized'], errors='coerce')
salary_cols_drop = ['salary_min', 'salary_max', 'salary_avg', 
                    'salary_hourly', 'salary_yearly']
df1.drop(columns=[c for c in salary_cols_drop if c in df1.columns], inplace=True)
print("Salary columns cleaned")

# Step 9: Remove duplicates
df1.drop_duplicates(inplace=True)
print(f"After removing duplicates: {len(df1)} rows")

print(f"\nDataset 1 Final Shape: {df1.shape}")
print("Columns remaining:", list(df1.columns))
print("--- Dataset 1 Cleaning DONE ✅ ---")







# =============================================
# DATASET 2 - CLEANING (salaries.csv)
# =============================================
print("\n--- Cleaning Dataset 2 ---")

# Step 1: Filter only US and Canada
df2 = df2[df2['company_location'].isin(['US', 'CA'])]
print(f"After filtering US & Canada: {len(df2)} rows")

# Step 2: Filter only relevant job titles
df2 = df2[df2['job_title'].str.lower().str.contains(pattern, na=False)]
print(f"After filtering relevant jobs: {len(df2)} rows")

# Step 3: Map experience level codes to full names
exp_map = {
    'EN': 'Entry Level',
    'MI': 'Mid Level', 
    'SE': 'Senior Level',
    'EX': 'Executive Level'
}
df2['experience_level'] = df2['experience_level'].map(exp_map)
print("Experience level mapped")

# Step 4: Map employment type codes to full names
emp_map = {
    'FT': 'Full Time',
    'PT': 'Part Time',
    'CT': 'Contract',
    'FL': 'Freelance'
}
df2['employment_type'] = df2['employment_type'].map(emp_map)
print("Employment type mapped")

# Step 5: Map remote ratio to readable format
def map_remote(val):
    if val == 100:
        return 'Remote'
    elif val == 50:
        return 'Hybrid'
    else:
        return 'Onsite'

df2['work_type'] = df2['remote_ratio'].apply(map_remote)
df2.drop(columns=['remote_ratio'], inplace=True)
print("Remote ratio converted to work type")

# Step 6: Map company size
size_map = {
    'S': 'Small',
    'M': 'Medium',
    'L': 'Large'
}
df2['company_size'] = df2['company_size'].map(size_map)
print("Company size mapped")

# Step 7: Map company location
df2['country'] = df2['company_location'].map({'US': 'United States', 'CA': 'Canada'})
df2.drop(columns=['company_location'], inplace=True)
print("Country column added")

# Step 8: Add job_category column
df2['job_category'] = df2['job_title'].apply(categorize_job)
print("Job category added")

# Step 9: Remove duplicates
df2.drop_duplicates(inplace=True)
print(f"After removing duplicates: {len(df2)} rows")

print(f"\nDataset 2 Final Shape: {df2.shape}")
print("Columns remaining:", list(df2.columns))
print("--- Dataset 2 Cleaning DONE ✅ ---")








# =============================================
# DATASET 3 - CLEANING (LinkedIn Canada)
# =============================================
print("\n--- Cleaning Dataset 3 ---")

# Step 1: Filter only Canada from linkedin_job_postings
df3a = df3a[df3a['search_country'] == 'Canada']
print(f"Canada rows only: {len(df3a)} rows")

# Step 2: Filter only Data/AI related jobs
df3a = df3a[df3a['job_title'].str.lower().str.contains(pattern, na=False)]
print(f"After filtering relevant jobs: {len(df3a)} rows")

# Step 3: Keep only useful columns
cols_to_keep_3a = [
    'job_link', 'job_title', 'company', 
    'job_location', 'job_type', 'job_level',
    'first_seen', 'last_processed_time'
]
df3a = df3a[[c for c in cols_to_keep_3a if c in df3a.columns]]
print("Useless columns dropped")

# Step 4: Rename columns for clarity
df3a.rename(columns={
    'company': 'company_name',
    'job_location': 'location',
    'job_type': 'work_type',
    'job_level': 'experience_level',
    'first_seen': 'date_posted'
}, inplace=True)
print("Columns renamed")

# Step 5: Fix date column
df3a['date_posted'] = pd.to_datetime(df3a['date_posted'], errors='coerce')
df3a['year'] = df3a['date_posted'].dt.year
df3a['month'] = df3a['date_posted'].dt.month
df3a['month_name'] = df3a['date_posted'].dt.strftime('%B')
print("Date columns extracted")

# Step 6: Add country column
df3a['country'] = 'Canada'

# Step 7: Add job_category
df3a['job_category'] = df3a['job_title'].apply(categorize_job)
print("Job category added")

# Step 8: Join with job_skills (df3b)
df3b_clean = df3b[df3b['job_link'].isin(df3a['job_link'])]
df3 = df3a.merge(df3b_clean, on='job_link', how='left')
print(f"After joining with skills: {len(df3)} rows")

# Step 9: Clean skills column
df3['job_skills'] = df3['job_skills'].fillna('Not Specified')
print("Skills nulls filled")

# Step 10: Remove duplicates
df3.drop_duplicates(inplace=True)
print(f"After removing duplicates: {len(df3)} rows")

print(f"\nDataset 3 Final Shape: {df3.shape}")
print("Columns remaining:", list(df3.columns))
print("--- Dataset 3 Cleaning DONE ✅ ---")










# =============================================
# ADDITIONAL FIXES BEFORE SAVING
# =============================================
print("\n--- Applying Final Fixes ---")

# Fix 1: Dataset 1 - Clean location column (remove extra spaces)
df1['location'] = df1['location'].str.strip()
df1['location'] = df1['location'].replace({
    'Anywhere': 'Remote/Anywhere',
    'United States': 'US - Multiple Locations'
})
print("Dataset 1 location cleaned")

# Fix 2: Dataset 1 - Extract skills from description_tokens
import ast

def extract_skills(token_str):
    try:
        skills = ast.literal_eval(token_str)
        return ', '.join([s.upper() for s in skills]) if skills else 'Not Specified'
    except:
        return 'Not Specified'

df1['skills'] = df1['description_tokens'].apply(extract_skills)
df1.drop(columns=['description_tokens'], inplace=True)
print("Dataset 1 skills extracted from tokens")

# Fix 3: Dataset 1 - Drop raw salary column, keep only standardized
df1.drop(columns=['salary'], inplace=True)
df1.rename(columns={'salary_standardized': 'salary_usd'}, inplace=True)
print("Dataset 1 salary column cleaned")

# Fix 4: Dataset 2 - Drop raw salary & currency columns
df2.drop(columns=['salary', 'salary_currency'], inplace=True)
print("Dataset 2 raw salary columns dropped")

# Fix 5: Dataset 3 - Drop job_link and last_processed_time (not needed in Power BI)
df3.drop(columns=['job_link', 'last_processed_time'], inplace=True)
print("Dataset 3 unnecessary columns dropped")

print("--- All Fixes Applied ✅ ---")








# =============================================
# FINAL FIXES BEFORE SAVING
# =============================================

# Dataset 2 - Remove remaining 11 duplicates
df2.drop_duplicates(inplace=True)
print(f"Dataset 2 after final dedup: {len(df2)} rows")

# Dataset 1 - Drop posted_at (relative time like '15 hours ago' - useless)
# Dataset 1 - Drop search_term (only 1 value 'data analyst' - useless)
# Dataset 1 - Drop search_location (only 1 value 'United States' - useless)
# Dataset 1 - Drop salary_usd (84.3% nulls - salary analysis from Dataset 2)
df1.drop(columns=['posted_at', 'search_term', 'search_location', 'salary_usd'], inplace=True)
print(f"Dataset 1 final columns: {list(df1.columns)}")
print(f"Dataset 1 final shape: {df1.shape}")

# Dataset 2 - Drop employee_residence (redundant - country column already exists)
df2.drop(columns=['employee_residence'], inplace=True)
print(f"Dataset 2 final columns: {list(df2.columns)}")
print(f"Dataset 2 final shape: {df2.shape}")

print("Final fixes done ✅")




# Remove last remaining duplicate in Dataset 2
df2.drop_duplicates(inplace=True)
print(f"Dataset 2 final rows after dedup: {len(df2)}")








# =============================================
# SKILLS EXPANDED TABLE - US Jobs
# =============================================
print("\n--- Creating Skills Expanded Table ---")

# Split skills column into individual rows
skills_expanded = df1.assign(
    skill=df1['skills'].str.split(',')
).explode('skill')

# Clean skill names
skills_expanded['skill'] = skills_expanded['skill'].str.strip()

# Remove "Not Specified"
skills_expanded = skills_expanded[skills_expanded['skill'] != 'Not Specified']

# Keep only relevant columns
skills_expanded = skills_expanded[['title', 'company_name', 'location', 
                                    'job_category', 'work_type', 
                                    'year', 'skill']]

# Remove duplicates
skills_expanded.drop_duplicates(inplace=True)

print(f"Skills expanded table shape: {skills_expanded.shape}")
print(f"Top 10 skills:\n{skills_expanded['skill'].value_counts().head(10)}")

# Save
skills_expanded.to_csv(f"{output_path}/cleaned_skills_expanded.csv", index=False)
print("✅ cleaned_skills_expanded.csv saved")







# Canada Skills Expanded
canada_skills_expanded = df3.assign(
    skill=df3['job_skills'].str.split(',')
).explode('skill')

# Step 1: Basic cleaning - strip spaces
canada_skills_expanded['skill'] = canada_skills_expanded['skill'].str.strip()

# Step 2: Remove "Not Specified"
canada_skills_expanded = canada_skills_expanded[canada_skills_expanded['skill'] != 'Not Specified']

# Step 3: Standardize known skills - fix capitalization properly
skill_mapping = {
    'sql': 'SQL',
    'power bi': 'Power BI',
    'powerbi': 'Power BI',
    'power_bi': 'Power BI',
    'python': 'Python',
    'tableau': 'Tableau',
    'r': 'R',
    'aws': 'AWS',
    'excel': 'Excel',
    'etl': 'ETL',
    'ml': 'Machine Learning',
    'ai': 'AI',
    'data visualization': 'Data Visualization',
    'data analysis': 'Data Analysis',
    'data analytics': 'Data Analytics',
    'data science': 'Data Science',
    'data engineering': 'Data Engineering',
    'data management': 'Data Management',
    'machine learning': 'Machine Learning',
    'business intelligence': 'Business Intelligence',
    'hypothesis testing': 'Hypothesis Testing',
    'statistical modeling': 'Statistical Modeling',
    'a/b testing': 'A/B Testing',
    'communication': 'Communication',
    'collaboration': 'Collaboration',
    'data mining': 'Data Mining',
    'statistics': 'Statistics',
    'reporting': 'Reporting',
    'pytorch': 'PyTorch',
    'tensorflow': 'TensorFlow',
    'spark': 'Spark',
    'hadoop': 'Hadoop',
    'snowflake': 'Snowflake',
    'looker': 'Looker',
    'sas': 'SAS',
    'spss': 'SPSS',
    'azure': 'Azure',
    'gcp': 'GCP',
}

canada_skills_expanded['skill'] = canada_skills_expanded['skill'].apply(
    lambda x: skill_mapping.get(x.lower().strip(), x)
)

# Step 4: Keep only relevant columns
canada_skills_expanded = canada_skills_expanded[['job_title', 'company_name',
                                                   'location', 'job_category', 'skill']]

# Step 5: Remove duplicates
canada_skills_expanded.drop_duplicates(inplace=True)

# Step 6: Save
canada_skills_expanded.to_csv(f"{output_path}/cleaned_canada_skills.csv", index=False)
print(f"✅ cleaned_canada_skills.csv saved: {canada_skills_expanded.shape}")





# =============================================
# SAVE ALL CLEANED DATASETS
# =============================================
print("\n--- Saving Cleaned Datasets ---")

df1.to_csv(f"{output_path}/cleaned_us_jobs.csv", index=False)
print("✅ cleaned_us_jobs.csv saved")

df2.to_csv(f"{output_path}/cleaned_salaries.csv", index=False)
print("✅ cleaned_salaries.csv saved")

df3.to_csv(f"{output_path}/cleaned_canada_jobs.csv", index=False)
print("✅ cleaned_canada_jobs.csv saved")

print("\n🎉 ALL DATASETS CLEANED AND SAVED SUCCESSFULLY!")
print(f"\nFinal Summary:")
print(f"  Dataset 1 (US Jobs):      {len(df1):,} rows, {df1.shape[1]} columns")
print(f"  Dataset 2 (Salaries):     {len(df2):,} rows, {df2.shape[1]} columns")
print(f"  Dataset 3 (Canada Jobs):  {len(df3):,} rows, {df3.shape[1]} columns")


