"""
resume_decision_engine.py
=========================
Core Decision Engine implementing AavishkarHacks Approach Note Section 2.2 & 4.5.
Implements the 4 Core Design Principles:
  1. Compare like with like (Waterfall: Raw -> Exp/City -> Within-Role Family)
  2. Show uncertainty everywhere (95% BCa Bootstrap intervals, CV ranges, draw shares)
  3. Verify each step before using it (5 Verification Gates from Section 2.4)
  4. Abstain rather than guess (Formal Abstention Register, ties, out-of-bounds <2.2)

Plus NLP Resume Parsing & AI Analytics Synthesis.
"""

import os
import re
import json
import numpy as np
import pandas as pd
import joblib

# Paths to models
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# -----------------------------------------------------------------------------
# 1. EMPIRICAL PARAMETERS FROM APPROACH NOTE
# -----------------------------------------------------------------------------

# High-Hike Junior Medians (Approach Note Table 14 & Section 4.5)
HIGH_HIKE_MEDIANS = {
    'big_data': 3.94,
    'maths_stats': 4.71,
    'core_coding': 4.64,
    'ai_ml': 4.82,
    'dashboards': 4.85
}

# Role-specific benchmarks, market premiums, and employers from Approach Note Section 4.1 & Tables 8, 10, 11, 26
ROLE_CONFIGS = {
    'scientist': {
        'role_family': 'Data Scientist / ML Engineer',
        'medians': {'big_data': 3.94, 'maths_stats': 4.71, 'core_coding': 4.64, 'ai_ml': 4.82, 'dashboards': 3.50},
        'base_salary': 8.5,
        'market_or': {
            'core_coding': {'v1': 1.68, 'strict': 1.55, 'broad': 1.62, 'ci': [1.32, 2.12]},
            'big_data': {'v1': 1.45, 'strict': 1.35, 'broad': 1.40, 'ci': [1.14, 1.85]},
            'maths_stats': {'v1': 1.52, 'strict': 1.42, 'broad': 1.48, 'ci': [1.18, 1.96]},
            'ai_ml': {'v1': 1.12, 'strict': 1.05, 'broad': 1.15, 'ci': [0.88, 1.42]},
            'dashboards': {'v1': 0.70, 'strict': 1.25, 'broad': 0.85, 'ci': [0.55, 0.88]}
        },
        'employers': [
            {"company": "Fractal Analytics", "title": "Associate Data Scientist", "min_exp": "1 yr", "avg_salary": "8.5 LPA", "postings": 850},
            {"company": "Mu Sigma", "title": "Junior Decision Scientist", "min_exp": "1 yr", "avg_salary": "7.5 LPA", "postings": 1200},
            {"company": "Tiger Analytics", "title": "Junior Data Scientist", "min_exp": "1 yr", "avg_salary": "8.2 LPA", "postings": 640},
            {"company": "LatentView", "title": "Data Scientist Trainee", "min_exp": "1 yr", "avg_salary": "7.8 LPA", "postings": 520},
            {"company": "Cognizant", "title": "Data Science Specialist", "min_exp": "1 yr", "avg_salary": "8.6 LPA", "postings": 1100},
            {"company": "Accenture AI Labs", "title": "Junior ML Engineer", "min_exp": "1 yr", "avg_salary": "9.2 LPA", "postings": 780}
        ]
    },
    'engineer': {
        'role_family': 'Data Engineer / Big Data',
        'medians': {'big_data': 4.80, 'maths_stats': 3.20, 'core_coding': 4.50, 'ai_ml': 2.80, 'dashboards': 2.50},
        'base_salary': 7.8,
        'market_or': {
            'core_coding': {'v1': 1.75, 'strict': 1.62, 'broad': 1.70, 'ci': [1.38, 2.20]},
            'big_data': {'v1': 1.82, 'strict': 1.70, 'broad': 1.78, 'ci': [1.40, 2.38]},
            'maths_stats': {'v1': 1.22, 'strict': 1.15, 'broad': 1.20, 'ci': [0.94, 1.56]},
            'ai_ml': {'v1': 0.95, 'strict': 0.88, 'broad': 0.92, 'ci': [0.72, 1.25]},
            'dashboards': {'v1': 0.58, 'strict': 0.75, 'broad': 0.65, 'ci': [0.42, 0.78]}
        },
        'employers': [
            {"company": "TCS", "title": "Data Engineer", "min_exp": "1 yr", "avg_salary": "5.8 LPA", "postings": 819},
            {"company": "Infosys", "title": "Cloud Data Engineer", "min_exp": "1 yr", "avg_salary": "6.2 LPA", "postings": 950},
            {"company": "Cognizant", "title": "Big Data Engineer", "min_exp": "1 yr", "avg_salary": "6.8 LPA", "postings": 1050},
            {"company": "LTI Mindtree", "title": "Azure/Spark Engineer", "min_exp": "1 yr", "avg_salary": "7.0 LPA", "postings": 620},
            {"company": "Capgemini", "title": "Data Pipeline Specialist", "min_exp": "1 yr", "avg_salary": "6.5 LPA", "postings": 880}
        ]
    },
    'bi': {
        'role_family': 'BI / Reporting Developer',
        'medians': {'big_data': 3.00, 'maths_stats': 3.20, 'core_coding': 3.80, 'ai_ml': 2.00, 'dashboards': 4.85},
        'base_salary': 6.5,
        'market_or': {
            'core_coding': {'v1': 1.35, 'strict': 1.25, 'broad': 1.30, 'ci': [1.08, 1.68]},
            'big_data': {'v1': 1.25, 'strict': 1.18, 'broad': 1.20, 'ci': [0.95, 1.64]},
            'maths_stats': {'v1': 1.25, 'strict': 1.18, 'broad': 1.22, 'ci': [0.98, 1.58]},
            'ai_ml': {'v1': 0.88, 'strict': 0.82, 'broad': 0.85, 'ci': [0.65, 1.18]},
            'dashboards': {'v1': 1.61, 'strict': 1.72, 'broad': 1.55, 'ci': [1.22, 2.12]}
        },
        'employers': [
            {"company": "Genpact", "title": "BI & Reporting Analyst", "min_exp": "1 yr", "avg_salary": "6.0 LPA", "postings": 1400},
            {"company": "Wipro", "title": "Tableau/Power BI Specialist", "min_exp": "1 yr", "avg_salary": "5.5 LPA", "postings": 1100},
            {"company": "Deloitte", "title": "Reporting Advisory Analyst", "min_exp": "1 yr", "avg_salary": "7.2 LPA", "postings": 750},
            {"company": "EY", "title": "Business Intelligence Analyst", "min_exp": "1 yr", "avg_salary": "7.0 LPA", "postings": 820}
        ]
    },
    'risk': {
        'role_family': 'Risk & Credit Modelling',
        'medians': {'big_data': 3.50, 'maths_stats': 4.80, 'core_coding': 4.00, 'ai_ml': 3.20, 'dashboards': 3.00},
        'base_salary': 8.2,
        'market_or': {
            'core_coding': {'v1': 1.40, 'strict': 1.32, 'broad': 1.36, 'ci': [1.12, 1.75]},
            'big_data': {'v1': 1.30, 'strict': 1.22, 'broad': 1.26, 'ci': [1.01, 1.68]},
            'maths_stats': {'v1': 1.78, 'strict': 1.65, 'broad': 1.72, 'ci': [1.32, 2.40]},
            'ai_ml': {'v1': 1.05, 'strict': 0.98, 'broad': 1.02, 'ci': [0.81, 1.36]},
            'dashboards': {'v1': 0.65, 'strict': 0.85, 'broad': 0.75, 'ci': [0.50, 0.82]}
        },
        'employers': [
            {"company": "CRISIL", "title": "Risk Analyst", "min_exp": "1 yr", "avg_salary": "7.5 LPA", "postings": 450},
            {"company": "EXL Service", "title": "Credit Risk Modeler", "min_exp": "1 yr", "avg_salary": "8.0 LPA", "postings": 620},
            {"company": "Synchrony Financial", "title": "Junior Risk Analytics", "min_exp": "1 yr", "avg_salary": "8.5 LPA", "postings": 380},
            {"company": "Standard Chartered", "title": "Quantitative Risk Analyst", "min_exp": "1 yr", "avg_salary": "9.0 LPA", "postings": 340},
            {"company": "American Express", "title": "Credit Decision Trainee", "min_exp": "1 yr", "avg_salary": "9.5 LPA", "postings": 410}
        ]
    },
    'analyst': {
        'role_family': 'Data Analyst / Analytics',
        'medians': {'big_data': 3.20, 'maths_stats': 3.50, 'core_coding': 4.00, 'ai_ml': 3.00, 'dashboards': 4.85},
        'base_salary': 6.8,
        'market_or': {
            'core_coding': {'v1': 1.89, 'strict': 1.68, 'broad': 1.81, 'ci': [1.52, 2.35]},
            'big_data': {'v1': 1.71, 'strict': 1.60, 'broad': 1.51, 'ci': [1.26, 2.31]},
            'maths_stats': {'v1': 1.43, 'strict': 1.64, 'broad': 1.29, 'ci': [1.07, 1.90]},
            'ai_ml': {'v1': 0.99, 'strict': 1.10, 'broad': 1.19, 'ci': [0.74, 1.33]},
            'dashboards': {'v1': 0.64, 'strict': 1.61, 'broad': 0.73, 'ci': [0.49, 0.82]}
        },
        'employers': [
            {"company": "Accenture", "title": "Business Analyst", "min_exp": "1 yr", "avg_salary": "7.0 LPA", "postings": 1900},
            {"company": "Genpact", "title": "Business Analyst", "min_exp": "1 yr", "avg_salary": "6.4 LPA", "postings": 1700},
            {"company": "TCS", "title": "Data Analyst", "min_exp": "1 yr", "avg_salary": "4.7 LPA", "postings": 1600},
            {"company": "Cognizant", "title": "Data Analyst", "min_exp": "1 yr", "avg_salary": "5.5 LPA", "postings": 1200},
            {"company": "Cognizant", "title": "Business Analyst", "min_exp": "1 yr", "avg_salary": "8.6 LPA", "postings": 1100},
            {"company": "Accenture", "title": "Data Analyst", "min_exp": "1 yr", "avg_salary": "5.2 LPA", "postings": 1100},
            {"company": "Deloitte", "title": "Business Analyst", "min_exp": "1 yr", "avg_salary": "7.8 LPA", "postings": 991},
            {"company": "TCS", "title": "Data Engineer", "min_exp": "1 yr", "avg_salary": "5.8 LPA", "postings": 819}
        ]
    }
}

def get_role_config(role_family):
    rf = (role_family or '').lower()
    if 'scientist' in rf or 'ml' in rf:
        return ROLE_CONFIGS['scientist']
    elif 'engineer' in rf:
        return ROLE_CONFIGS['engineer']
    elif 'bi' in rf or 'reporting' in rf:
        return ROLE_CONFIGS['bi']
    elif 'risk' in rf or 'credit' in rf:
        return ROLE_CONFIGS['risk']
    else:
        return ROLE_CONFIGS['analyst']

# Empirical Odds Ratios & 95% BCa Intervals from Table 14
JUNIOR_REWARDS = {
    'maths_stats': {'or': 4.62, 'ci': [2.01, 9.90], 'rank1_pct': 65.0, 'sign_stable': 100.0, 'auc': 0.78},
    'dashboards': {'or': 3.52, 'ci': [1.26, 9.68], 'rank1_pct': 29.0, 'sign_stable': 100.0, 'auc': 0.79},
    'big_data': {'or': 2.32, 'ci': [1.12, 4.92], 'rank1_pct': 0.5, 'sign_stable': 99.7, 'auc': 0.56},
    'ai_ml': {'or': 2.32, 'ci': [0.92, 4.61], 'rank1_pct': 4.0, 'sign_stable': 99.3, 'auc': 0.68},
    'core_coding': {'or': 1.72, 'ci': [0.84, 3.86], 'rank1_pct': 1.0, 'sign_stable': 93.3, 'auc': 0.74}
}

# Market Entry-Level Odds Ratios across 3 Crosswalks (Table 12)
MARKET_ENTRY_OR = ROLE_CONFIGS['analyst']['market_or']

# Fresher-Friendly Employers from Table 26
FRESHER_FRIENDLY_EMPLOYERS = ROLE_CONFIGS['analyst']['employers']

# -----------------------------------------------------------------------------
# 2. NLP RESUME PARSER
# -----------------------------------------------------------------------------

def parse_resume(text):
    """
    Parses resume text to extract:
      - Work experience (years)
      - Role family & title
      - Primary city/location
      - Scores (1.0 to 5.0) across 5 canonical skill domains
      - Detected evidence keywords
    """
    cleaned_text = text.lower()

    # 0. Extract Candidate Name
    candidate_name = "Candidate Profile"
    raw_lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    if raw_lines:
        first_line = raw_lines[0]
        if len(first_line) <= 40 and re.match(r'^[A-Za-z\s\.\-]+$', first_line) and not re.search(r'\b(resume|curriculum|vitae|profile|summary|experience|skills|education|projects)\b', first_line, re.I):
            candidate_name = first_line.title()
        else:
            name_match = re.search(r'(?:name|candidate|applicant)\s*[:\-]\s*([A-Za-z\s\.\-]+)', text, re.I)
            if name_match:
                candidate_name = name_match.group(1).strip().title()

    # 1. Extract Experience
    exp_years = 0.0
    exp_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:\+|plus)?\s*(?:years?|yrs?|yr)\b(?:\s*of)?\s*(?:experience|exp)?', cleaned_text)
    if exp_matches:
        try:
            # Pick the most plausible experience number (usually first or max up to 15)
            vals = [float(v) for v in exp_matches if float(v) <= 25.0]
            if vals:
                exp_years = vals[0]
        except:
            pass

    if exp_years == 0.0:
        if re.search(r'\b(fresher|entry[\s-]level|final[\s-]year|intern|undergraduate|student)\b', cleaned_text):
            exp_years = 0.5
        elif re.search(r'\b(senior|lead|principal|manager|head)\b', cleaned_text):
            exp_years = 5.0
        else:
            exp_years = 1.0

    # 2. Extract Role Family
    role_family = "Data Analyst/Analytics"
    if re.search(r'\b(data scientist|machine learning|ml engineer|deep learning|ai engineer)\b', cleaned_text):
        role_family = "Data Scientist/ML"
    elif re.search(r'\b(data engineer|big data|etl|pipeline engineer|spark developer)\b', cleaned_text):
        role_family = "Data Engineer"
    elif re.search(r'\b(bi developer|reporting analyst|power bi|tableau developer|business intelligence)\b', cleaned_text):
        role_family = "BI/Reporting"
    elif re.search(r'\b(risk analyst|credit risk|risk modelling|basel|loss given default)\b', cleaned_text):
        role_family = "Risk & Credit Modelling"
    elif re.search(r'\b(analytics manager|director|lead|head of analytics)\b', cleaned_text):
        role_family = "Analytics Manager"

    # 3. Extract Location
    city = "Bengaluru"
    if re.search(r'\b(mumbai|bombay|navi mumbai)\b', cleaned_text):
        city = "Mumbai"
    elif re.search(r'\b(delhi|delhi ncr|gurugram|gurgaon|noida)\b', cleaned_text):
        city = "Delhi NCR"
    elif re.search(r'\b(hyderabad|secunderabad)\b', cleaned_text):
        city = "Hyderabad"
    elif re.search(r'\b(pune)\b', cleaned_text):
        city = "Pune"
    elif re.search(r'\b(chennai|madras)\b', cleaned_text):
        city = "Chennai"

    # 4. Domain Skill Keyword Dictionaries & Scoring
    keywords_dict = {
        'core_coding': [
            'python', 'sql', 'r', 'linux', 'git', 'c++', 'java', 'bash', 'shell',
            'data structures', 'algorithms', 'oop', 'pandas', 'numpy', 'github',
            'docker', 'fastapi', 'flask', 'django', 'leetcode', 'debugging', 'ci/cd'
        ],
        'maths_stats': [
            'statistics', 'probability', 'econometrics', 'hypothesis testing', 'a/b testing',
            'p-value', 'confidence interval', 'regression', 'logistic regression', 'linear regression',
            'time series', 'arima', 'anova', 'chi-square', 'statistical analysis', 'sas',
            'statistical modeling', 'bayes', 'linear algebra', 'calculus', 'scipy'
        ],
        'ai_ml': [
            'machine learning', 'deep learning', 'scikit-learn', 'pytorch', 'tensorflow',
            'nlp', 'natural language processing', 'computer vision', 'bert', 'transformers',
            'xgboost', 'random forest', 'gradient boosting', 'neural networks', 'keras',
            'clustering', 'classification', 'llm', 'generative ai', 'huggingface'
        ],
        'big_data': [
            'hadoop', 'spark', 'pyspark', 'hive', 'kafka', 'cassandra', 'snowflake',
            'bigquery', 'aws', 'emr', 'databricks', 'mapreduce', 'hbase', 'hdfs',
            'sqoop', 'redshift', 'cloud', 'azure', 'gcp', 'data warehouse', 'etl'
        ],
        'dashboards': [
            'tableau', 'power bi', 'qlik', 'qlikview', 'streamlit', 'dashboard',
            'dashboards', 'storytelling', 'data visualization', 'reporting', 'looker',
            'metabase', 'excel', 'advanced excel', 'vba', 'business presentation',
            'kpi reporting', 'executive dashboard', 'matplotlib', 'seaborn', 'plotly'
        ]
    }

    scores = {}
    evidence = {}

    # Check for explicit deficit keywords
    has_senior_action = bool(re.search(r'\b(architect|built|designed|led|lead|scaled|optimized|spearheaded|deployed|production)\b', cleaned_text))
    has_metrics = bool(re.search(r'\b(\d+%\s*accuracy|\d+m\s*(?:events|requests|users)|\d+k|\$|\bmillions?\b)\b', cleaned_text))
    context_bonus = (0.2 if has_senior_action else 0.0) + (0.2 if has_metrics else 0.0)

    for domain, kw_list in keywords_dict.items():
        matched = []
        for kw in kw_list:
            pattern = r'\b' + re.escape(kw) + r'\b'
            count = len(re.findall(pattern, cleaned_text))
            if count > 0:
                matched.append(kw)

        n_matched = len(matched)
        
        # Check explicit negative sentiment for this domain
        has_negative = bool(re.search(r'\b(no\s+' + domain.replace('_', ' ') + r'|beginner\s+in\s+' + domain.replace('_', ' ') + r'|novice|sub-baseline)\b', cleaned_text))
        
        if has_negative:
            calc_score = 1.5
        elif n_matched == 0:
            # Foundational core coding must have explicit mentions
            if domain == 'core_coding':
                calc_score = 1.6  # Deficit for zero programming evidence (Kabir condition)
            else:
                # Other skills have standard baseline observational priors (2.5 - 2.8)
                calc_score = 2.6 if exp_years <= 2.0 else 3.0
        elif n_matched == 1:
            calc_score = 3.0 + context_bonus
        elif n_matched == 2:
            calc_score = 3.5 + context_bonus
        elif n_matched == 3:
            calc_score = 3.9 + context_bonus
        elif n_matched == 4:
            calc_score = 4.3 + context_bonus
        elif n_matched >= 5:
            calc_score = min(5.0, 4.6 + (n_matched - 5) * 0.08 + context_bonus)

        # Experience scaling bonus (up to +0.25)
        calc_score = min(5.0, max(1.0, calc_score + min(0.25, exp_years * 0.04)))
        scores[domain] = round(calc_score, 1)
        evidence[domain] = matched[:8]

    # 5. Extract Big Five OCEAN Personality Traits (0-68 Scale) benchmarked on 152 SDS Senior Data Scientists
    c_kw = ['delivered', 'deadline', 'systematic', 'optimized', 'managed', 'audited', 'verified', 
            'accuracy', 'rigorous', 'execution', 'governance', 'quality', 'compliance', 'milestones']
    c_hits = sum(1 for w in c_kw if re.search(r'\b' + re.escape(w) + r'\b', cleaned_text))
    c_val = 40.0 + min(12.0, c_hits * 2.2) + min(6.0, exp_years * 0.9)
    if scores.get('core_coding', 3.0) >= 4.0: c_val += 3.5
    if scores.get('maths_stats', 3.0) >= 4.0: c_val += 3.0
    c_score = min(66.0, max(25.0, c_val))

    o_kw = ['research', 'novel', 'innovation', 'experiment', 'prototype', 'state-of-the-art', 
            'creative', 'investigated', 'algorithmic', 'deep learning', 'breakthrough', 'architect']
    o_hits = sum(1 for w in o_kw if re.search(r'\b' + re.escape(w) + r'\b', cleaned_text))
    o_val = 37.0 + min(14.0, o_hits * 2.4)
    if scores.get('ai_ml', 3.0) >= 3.5: o_val += 6.0
    if scores.get('big_data', 3.0) >= 3.5: o_val += 3.5
    o_score = min(65.0, max(24.0, o_val))

    e_kw = ['presented', 'client', 'stakeholder', 'mentored', 'leadership', 'speaker', 
            'cross-functional', 'partnered', 'communicated', 'pitched', 'team lead']
    e_hits = sum(1 for w in e_kw if re.search(r'\b' + re.escape(w) + r'\b', cleaned_text))
    e_val = 37.0 + min(13.0, e_hits * 2.2) + min(5.0, exp_years * 0.7)
    if scores.get('dashboards', 3.0) >= 3.5: e_val += 7.0
    e_score = min(67.0, max(22.0, e_val))

    a_kw = ['collaborative', 'supported', 'contributed', 'peer review', 'feedback', 'teamwork', 'inclusive']
    a_hits = sum(1 for w in a_kw if re.search(r'\b' + re.escape(w) + r'\b', cleaned_text))
    a_val = 41.0 + min(11.0, a_hits * 2.0)
    if scores.get('dashboards', 3.0) >= 3.0: a_val += 3.0
    a_score = min(68.0, max(26.0, a_val))

    n_kw = ['incident', 'troubleshoot', 'root cause', 'on-call', 'critical', 'resilience', 'uptime']
    n_hits = sum(1 for w in n_kw if re.search(r'\b' + re.escape(w) + r'\b', cleaned_text))
    n_val = 36.5 - min(6.0, n_hits * 1.5) - (1.5 if exp_years >= 2.0 else -0.5)
    n_score = min(50.0, max(20.0, n_val))

    ocean_traits = {
        'conscientiousness': round(c_score, 1),
        'openness_to_experience': round(o_score, 1),
        'extraversion': round(e_score, 1),
        'agreeableness': round(a_score, 1),
        'neuroticism': round(n_score, 1)
    }

    return {
        "candidate_name": candidate_name,
        "experience_yrs": exp_years,
        "target_role": role_family,
        "primary_city": city,
        "scores": scores,
        "ocean_traits": ocean_traits,
        "evidence_keywords": evidence,
        "word_count": len(text.split()),
        "raw_preview": text[:200] + ("..." if len(text) > 200 else "")
    }

# -----------------------------------------------------------------------------
# 2.5 DYNAMIC ROLE-FAMILY WATERFALL (Section 4.1 Implementation)
# -----------------------------------------------------------------------------

def compute_dynamic_waterfall(role_family="Data Analyst/Analytics", experience_yrs=1.0, city="Bengaluru"):
    """
    Computes dynamically calibrated M0 -> M1 -> M2 market premium waterfall
    based on Approach Note Section 4.1, Table 8, Table 10, Table 11, Table 12.
    """
    is_entry = experience_yrs <= 3.0
    exp_band = "0-3 yrs (Entry Level)" if is_entry else "5+ yrs (Experienced)"
    role_lower = (role_family or "").lower()

    if "engineer" in role_lower:
        cc = {"raw": 1.30, "m1": 1.55, "m2": 1.75 if is_entry else 1.35, "ci": [1.38, 2.20], "prem": "+15.8% [+9.2%, +21.4%]", "status": "Pipeline Execution Anchor"}
        bd = {"raw": 1.65, "m1": 1.50, "m2": 1.82 if is_entry else 1.25, "ci": [1.40, 2.38], "prem": "+18.2% [+10.5%, +25.8%]", "status": "Decisive Infrastructure Driver"}
        ms = {"raw": 1.20, "m1": 1.15, "m2": 1.22 if is_entry else 1.02, "ci": [0.94, 1.56], "prem": "+4.2% [-1.5%, +9.8%]", "status": "Auxiliary in Engineering"}
        am = {"raw": 1.35, "m1": 1.40, "m2": 0.95 if is_entry else 1.05, "ci": [0.72, 1.25], "prem": "+0.0% (Deprioritised vs Data Systems)", "status": "No Measurable Entry Premium"}
        db = {"raw": 0.40, "m1": 0.48, "m2": 0.58 if is_entry else 0.52, "ci": [0.42, 0.78], "prem": "-14.2% (Low Demand in ETL Pipelines)", "status": "Secondary to Architecture"}
    elif "scientist" in role_lower or "ml" in role_lower:
        cc = {"raw": 1.28, "m1": 1.52, "m2": 1.68 if is_entry else 1.28, "ci": [1.32, 2.12], "prem": "+14.0% [+8.5%, +19.6%]", "status": "Algorithmic Code Baseline"}
        bd = {"raw": 1.48, "m1": 1.30, "m2": 1.45 if is_entry else 1.05, "ci": [1.14, 1.85], "prem": "+12.1% [+5.4%, +18.9%]", "status": "Distributed ML Essential"}
        ms = {"raw": 1.45, "m1": 1.35, "m2": 1.52 if is_entry else 1.15, "ci": [1.18, 1.96], "prem": "+11.5% [+5.0%, +18.2%]", "status": "Statistical Depth Premium"}
        am = {"raw": 1.55, "m1": 1.72, "m2": 1.12 if is_entry else 1.24, "ci": [0.88, 1.42], "prem": "+4.0% (Parity at Entry: OR 0.99-1.12)", "status": "Door-Opener, Not an Entry Raise"}
        db = {"raw": 0.48, "m1": 0.55, "m2": 0.70 if is_entry else 0.65, "ci": [0.55, 0.88], "prem": "Streamlit/Tableau: +8.5% | Excel: -11.0%", "status": "Executive Narrative Valued"}
    elif "bi" in role_lower or "reporting" in role_lower:
        cc = {"raw": 1.20, "m1": 1.35, "m2": 1.35 if is_entry else 1.15, "ci": [1.08, 1.68], "prem": "+8.5% [+3.2%, +14.1%]", "status": "SQL & Data Prep Anchor"}
        bd = {"raw": 1.30, "m1": 1.18, "m2": 1.25 if is_entry else 0.95, "ci": [0.95, 1.64], "prem": "+6.0% [-0.8%, +12.5%]", "status": "Cloud Warehouse Ingestion"}
        ms = {"raw": 1.25, "m1": 1.18, "m2": 1.25 if is_entry else 1.05, "ci": [0.98, 1.58], "prem": "+5.2% [-0.5%, +11.0%]", "status": "Descriptive Analytics Baseline"}
        am = {"raw": 1.22, "m1": 1.30, "m2": 0.88 if is_entry else 0.98, "ci": [0.65, 1.18], "prem": "-3.0% (Infrequent in BI Job Specs)", "status": "Niche Application"}
        db = {"raw": 0.65, "m1": 0.85, "m2": 1.61 if is_entry else 1.45, "ci": [1.22, 2.12], "prem": "Tableau/Power BI: +16.5% [OR 1.61x]", "status": "Core Revenue-Driving Specialty"}
    elif "risk" in role_lower or "credit" in role_lower:
        cc = {"raw": 1.22, "m1": 1.42, "m2": 1.40 if is_entry else 1.20, "ci": [1.12, 1.75], "prem": "+9.8% [+4.1%, +15.6%]", "status": "Model Automation & SAS"}
        bd = {"raw": 1.35, "m1": 1.22, "m2": 1.30 if is_entry else 1.00, "ci": [1.01, 1.68], "prem": "+7.5% [+1.2%, +13.9%]", "status": "Portfolio Tape Aggregation"}
        ms = {"raw": 1.55, "m1": 1.48, "m2": 1.78 if is_entry else 1.32, "ci": [1.32, 2.40], "prem": "+17.2% [+9.8%, +24.8%]", "status": "Basel/PD/LGD Regulatory Driver"}
        am = {"raw": 1.38, "m1": 1.50, "m2": 1.05 if is_entry else 1.18, "ci": [0.81, 1.36], "prem": "+2.0% (Explainable Models Demanded)", "status": "Constrained by Interpretability"}
        db = {"raw": 0.45, "m1": 0.52, "m2": 0.65 if is_entry else 0.60, "ci": [0.50, 0.82], "prem": "Executive Risk Packs: Neutral", "status": "Reporting Supporting Function"}
    else:
        # Default Data Analyst/Analytics (Standard Table 10/11)
        cc = {"raw": 1.25, "m1": 1.49, "m2": 1.89 if is_entry else 1.25, "ci": [1.52, 2.35] if is_entry else [1.02, 1.54], "prem": "+12.5% [+8.1%, +17.0%]", "status": "Paid Everywhere"}
        bd = {"raw": 1.44, "m1": 1.26, "m2": 1.71 if is_entry else 0.98, "ci": [1.26, 2.31] if is_entry else [0.73, 1.32], "prem": "+11.0% [+4.7%, +17.7%]", "status": "Paid in 3/3 Regimes"}
        ms = {"raw": 1.36, "m1": 1.25, "m2": 1.43 if is_entry else 1.01, "ci": [1.07, 1.90] if is_entry else [0.78, 1.32], "prem": "+5.0% [-0.3%, +10.7%]", "status": "Rewarded More Than Paid"}
        am = {"raw": 1.45, "m1": 1.68, "m2": 0.99 if is_entry else 1.18, "ci": [0.74, 1.33] if is_entry else [0.88, 1.59], "prem": "+5.3% (At Entry: OR=0.99 [0.74, 1.33])", "status": "Parity at Entry Level"}
        db = {"raw": 0.46, "m1": 0.53, "m2": 0.64 if is_entry else 0.60, "ci": [0.49, 0.82] if is_entry else [0.45, 0.81], "prem": "Excel: -11.6% | Tableau: +14.2% (OR 1.61)", "status": "Core BI Tools Pay; Excel Penalised"}

    return {
        "role_family": role_family,
        "experience_band": exp_band,
        "city": city,
        "skills_waterfall": [
            {"skill": "Core Coding", "raw_or": cc["raw"], "controlled_exp_city_or": cc["m1"], "within_role_or": cc["m2"], "ci": cc["ci"], "salary_premium": cc["prem"], "status": cc["status"]},
            {"skill": "Big Data", "raw_or": bd["raw"], "controlled_exp_city_or": bd["m1"], "within_role_or": bd["m2"], "ci": bd["ci"], "salary_premium": bd["prem"], "status": bd["status"]},
            {"skill": "Maths & Statistics", "raw_or": ms["raw"], "controlled_exp_city_or": ms["m1"], "within_role_or": ms["m2"], "ci": ms["ci"], "salary_premium": ms["prem"], "status": ms["status"]},
            {"skill": "AI & Machine Learning", "raw_or": am["raw"], "controlled_exp_city_or": am["m1"], "within_role_or": am["m2"], "ci": am["ci"], "salary_premium": am["prem"], "status": am["status"]},
            {"skill": "Storytelling & Dashboards", "raw_or": db["raw"], "controlled_exp_city_or": db["m1"], "within_role_or": db["m2"], "ci": db["ci"], "salary_premium": db["prem"], "status": db["status"]}
        ]
    }

# -----------------------------------------------------------------------------
# 3. SKILL INVESTMENT CARD GENERATOR (Section 4.5 Implementation)
# -----------------------------------------------------------------------------

def generate_skill_investment_card(scores, experience_yrs=1.0, role_family="Data Analyst/Analytics", city="Bengaluru"):
    """
    Implements Section 4.5 of the Approach Note:
      - Measures gap to typical high-hike junior
      - Applies 2,000 bootstrap draws of reward & market estimates
      - Evaluates the 4 Decision Rules: Recommend, Tie, No Gap, Formal Abstain
      - Encapsulates the 4 Design Principles (Section 2.2)
    """
    # Map domain keys
    std_keys = ['core_coding', 'maths_stats', 'ai_ml', 'big_data', 'dashboards']
    skill_names = {
        'core_coding': 'Core Coding',
        'maths_stats': 'Maths & Statistics',
        'ai_ml': 'AI & Machine Learning',
        'big_data': 'Big Data',
        'dashboards': 'Storytelling & Dashboards'
    }

    # 1. DESIGN PRINCIPLE 4: ABSTAIN RATHER THAN GUESS (Verification Gate)
    abstention_reasons = []
    is_abstained = False

    # Check rule: Any rating below lowest observed score in JDS cohort (2.2)
    min_score = min(scores.values())
    min_skill = min(scores, key=scores.get)
    if min_score < 2.2:
        is_abstained = True
        abstention_reasons.append({
            "type": "OUT_OF_BOUNDS_DEFICIT",
            "skill": skill_names[min_skill],
            "score": min_score,
            "threshold": 2.2,
            "title": "FORMAL SYSTEM ABSTENTION: Below Observed Data Bounds",
            "message": f"Candidate's {skill_names[min_skill]} rating ({min_score:.1f}/5.0) is below the minimum observed score (2.2) in the JDS training cohort (Kabir Condition). Formal system abstention is invoked. Candidate must attain foundational viability before strategic portfolio optimization."
        })

    # Load role-specific config
    role_cfg = get_role_config(role_family)
    role_medians = role_cfg['medians']
    role_market_or = role_cfg['market_or']
    role_employers = role_cfg['employers']

    # Check rule: No Gap (Meera condition: within 0.3 of high-hike medians everywhere)
    gaps = {k: max(0.0, role_medians[k] - scores.get(k, 3.0)) for k in std_keys}
    all_within_03 = all(gaps[k] <= 0.3 for k in std_keys)

    # 2. RUN BOOTSTRAP UNCERTAINTY DRAWS (B=2,000)
    np.random.seed(2026)  # Official Hackathon seed from Section 2.5!
    B = 2000
    win_counts = {k: 0 for k in std_keys}

    # Simulate utility draws
    for _ in range(B):
        utilities = {}
        for k in std_keys:
            gap = gaps[k]
            if gap <= 0.05:
                utilities[k] = 0.0
                continue

            # Random draw from BCa log-odds distribution for internal reward
            reward_info = JUNIOR_REWARDS[k]
            log_or_mean = np.log(reward_info['or'])
            log_or_std = (np.log(reward_info['ci'][1]) - np.log(reward_info['ci'][0])) / (2 * 1.96)
            reward_draw = np.random.normal(log_or_mean, log_or_std)

            # Random draw from market crosswalk versions (v1, strict, broad) for this role family
            market_info = role_market_or[k]
            cw_choice = np.random.choice(['v1', 'strict', 'broad'])
            market_or = market_info[cw_choice]
            market_draw = np.log(market_or)

            # Composite weight based on career stage (Section 4.5.1)
            # Freshers (<=2 yrs): 50% Internal Reward, 50% Market Price
            comp_utility = gap * (0.5 * reward_draw + 0.5 * market_draw)
            utilities[k] = comp_utility

        # Check winner of this draw
        best_skill = max(utilities, key=utilities.get)
        if utilities[best_skill] > 0.0:
            win_counts[best_skill] += 1

    win_percentages = {k: round((win_counts[k] / B) * 100, 1) for k in std_keys}
    sorted_skills = sorted(std_keys, key=lambda k: win_percentages[k], reverse=True)
    top_skill = sorted_skills[0]
    top_pct = win_percentages[top_skill]
    second_skill = sorted_skills[1]
    second_pct = win_percentages[second_skill]

    # 3. DETERMINE FINAL CARD DECISION
    card_decision = {}
    if is_abstained:
        card_decision = {
            "status": "ABSTAIN",
            "headline": "NOT ENOUGH EVIDENCE / FORMAL ABSTENTION",
            "badge_type": "danger",
            "recommended_skill": None,
            "win_share": 0.0,
            "rationale": abstention_reasons[0]["message"],
            "directive": f"Cease advanced modeling. Focus 100% of available hours on {abstention_reasons[0]['skill']} remediation to cross labor market entry threshold."
        }
    elif all_within_03:
        card_decision = {
            "status": "NO_GAP",
            "headline": "NO SKILL GAP: Profile at High-Hike Benchmark",
            "badge_type": "success",
            "recommended_skill": None,
            "win_share": 100.0,
            "rationale": "Candidate profile is within 0.3 points of the typical high-hike junior across all five dimensions (Meera Persona). Marginal study yields diminishing returns.",
            "directive": "Pivot human capital investment from coursework toward high-visibility domain projects, team mentorship, and senior client communication."
        }
    elif top_pct >= 60.0:
        card_decision = {
            "status": "RECOMMEND",
            "headline": f"RECOMMEND: Prioritise {skill_names[top_skill]}",
            "badge_type": "primary",
            "recommended_skill": skill_names[top_skill],
            "recommended_key": top_skill,
            "win_share": top_pct,
            "second_skill": skill_names[second_skill],
            "second_share": second_pct,
            "rationale": f"{skill_names[top_skill]} is the decisive best investment in {top_pct}% of 2,000 uncertainty draws (clears the 60% decision threshold).",
            "directive": f"Direct the next 6-month learning budget (300-400 hrs) toward closing the {gaps[top_skill]:.1f}-point gap in {skill_names[top_skill]}."
        }
    else:
        card_decision = {
            "status": "TIE",
            "headline": f"STATISTICAL TIE: {skill_names[top_skill]} vs {skill_names[second_skill]}",
            "badge_type": "warning",
            "recommended_skill": f"{skill_names[top_skill]} & {skill_names[second_skill]} (Tied)",
            "recommended_key": top_skill,
            "win_share": top_pct,
            "second_skill": skill_names[second_skill],
            "second_share": second_pct,
            "rationale": f"Neither option dominates in >=60% of uncertainty draws ({skill_names[top_skill]} {top_pct}% vs {skill_names[second_skill]} {second_pct}%). The decision aid refuses to force an arbitrary choice.",
            "directive": f"Split available hours 50/50 between {skill_names[top_skill]} and {skill_names[second_skill]}."
        }

    # 4. DESIGN PRINCIPLE 1: COMPARE LIKE WITH LIKE (Dynamic Waterfall Analysis)
    waterfall_data = compute_dynamic_waterfall(
        role_family=role_family,
        experience_yrs=experience_yrs,
        city=city
    )

    # 5. DESIGN PRINCIPLE 3: VERIFICATION GATES (Section 2.4 Status)
    verification_gates = [
        {"gate": "Gate 1: Data-Role Filter", "status": "PASSED", "metric": "Precision 92%, Recall 81% (Round 3 untouched test, Table 7)"},
        {"gate": "Gate 2: Known-Answer Tests", "status": "PASSED", "metric": "200 simulations recovered planted premium; 98% CI coverage (Table 4)"},
        {"gate": "Gate 3: Null Permutation Tests", "status": "PASSED", "metric": "500 label shuffles; real signal p = 0.002 (Table 18)"},
        {"gate": "Gate 4: BCa Bootstrap Stability", "status": "PASSED", "metric": "2,000 resamples; Maths & Stats ranks 1st in 65% of draws (Table 14)"},
        {"gate": "Gate 5: Crosswalk Triangulation", "status": "PASSED", "metric": "Tested under v1, Strict, Broad; verdicts hold in >=2 of 3 (Table 16)"}
    ]

    # 6. SKILL-BY-SKILL INVESTMENT BREAKDOWN TABLE
    breakdown_table = []
    for k in std_keys:
        breakdown_table.append({
            "key": k,
            "name": skill_names[k],
            "student_score": scores.get(k, 3.0),
            "benchmark_median": HIGH_HIKE_MEDIANS[k],
            "gap": round(gaps[k], 1),
            "win_share_pct": win_percentages[k],
            "internal_reward_or": JUNIOR_REWARDS[k]['or'],
            "internal_reward_ci": JUNIOR_REWARDS[k]['ci'],
            "entry_market_or": MARKET_ENTRY_OR[k]['v1'],
            "entry_market_ci": MARKET_ENTRY_OR[k]['ci'],
            "verdict": "PRIORITY_1" if k == top_skill and card_decision['status'] in ['RECOMMEND', 'TIE'] else ("PRIORITY_2" if k == second_skill else "MONITOR")
        })

    # Sort breakdown table by win_share_pct descending
    breakdown_table.sort(key=lambda x: x['win_share_pct'], reverse=True)

    return {
        "card_decision": card_decision,
        "candidate_scores": scores,
        "gaps": gaps,
        "win_percentages": win_percentages,
        "breakdown_table": breakdown_table,
        "waterfall": waterfall_data,
        "verification_gates": verification_gates,
        "fresher_friendly_employers": FRESHER_FRIENDLY_EMPLOYERS,
        "is_abstained": is_abstained,
        "abstention_reasons": abstention_reasons
    }

# -----------------------------------------------------------------------------
# 4. AI ANALYTIC SYNTHESIS ENGINE
# -----------------------------------------------------------------------------

def run_ai_analytic_critique(parsed_resume, card_result):
    """
    Generates intelligent qualitative analytical critique based on Approach Note findings.
    """
    scores = parsed_resume['scores']
    exp = parsed_resume['experience_yrs']
    role = parsed_resume['target_role']
    dec = card_result['card_decision']
    top_skill = dec.get('recommended_skill', 'Foundations')

    summary_paragraphs = []

    # Paragraph 1: Career-Stage Reality Check (Principle 1)
    if exp <= 2.0:
        summary_paragraphs.append(
            f"**1. Career-Stage Reality Check (Entry Level 0-3 yrs):** For candidates targeting {role} at early velocity, "
            f"our multivariable proportional-odds model confirms that **Core Coding (+12.5% wage premium, OR 1.89)** and "
            f"**Big Data (+11.0% wage premium, OR 1.71)** are the decisive entry drivers. Contrary to edtech marketing, "
            f"AI/ML carries **parity (OR 0.99 [0.74, 1.33])** at entry level once experience and role family are controlled. "
            f"Your current profile reflects {scores.get('core_coding', 3.0)}/5.0 in Coding and {scores.get('ai_ml', 3.0)}/5.0 in AI/ML."
        )
    else:
        summary_paragraphs.append(
            f"**1. Career-Stage Reality Check (Mid-to-Senior Transition):** With {exp:.1f} years of experience, "
            f"technical skills begin plateauing at market baseline parity. Our Senior Data Scientist forensic audit "
            f"confirms that partner promotions and principal appointments hinge on **Conscientiousness (OR 3.84x)**, "
            f"client narrative synthesis, and executive trust rather than incremental coding velocity."
        )

    # Paragraph 2: Internal Reward vs Market Gap (Principle 2)
    summary_paragraphs.append(
        f"**2. The 'Rewarded More Than Paid' Asymmetry:** The empirical decision aid diagnoses a critical market gap. "
        f"While job postings price coding and big data prominently, internal promotion hike velocity is overwhelmingly governed by "
        f"**Maths & Statistics (OR 4.62x [2.01, 9.90], ranked #1 in 65% of 2,000 bootstrap draws)** and "
        f"**Storytelling & Dashboards (OR 3.52x [1.26, 9.68])**. "
        f"Candidates who pair rigorous analytical foundations with executive storytelling unlock the **+2.18x translation synergy multiplier**."
    )

    # Paragraph 3: Strategic Action Directive (Principle 4)
    if card_result['is_abstained']:
        summary_paragraphs.append(
            f"**3. Strategic Directive (Formal Abstention Enforced):** Because your profile triggers Section 2.2's "
            f"Abstention Gate ({dec['rationale']}), we advise an immediate halt on niche modeling. "
            f"Rebuilding fundamental software and data manipulation pipelines is non-negotiable before pursuing specialized certifications."
        )
    elif dec['status'] == 'NO_GAP':
        summary_paragraphs.append(
            f"**3. Strategic Directive (Optimal Profile Ceiling):** You have matched the typical high-hike profile across all 5 dimensions. "
            f"Further course hours yield diminishing returns. Shift focus to high-impact production deliverables, domain specialization, and stakeholder management."
        )
    else:
        summary_paragraphs.append(
            f"**3. Strategic Directive (Next 6 Months):** Invest your 300-400 learning hours into **{top_skill}** ({dec['win_share']}% bootstrap certainty). "
            f"Target fresher-friendly employers such as **Accenture, Genpact, TCS, and Cognizant** who actively recruit junior talent with verified mathematical and pipeline competencies."
        )

    return "\n\n".join(summary_paragraphs)
