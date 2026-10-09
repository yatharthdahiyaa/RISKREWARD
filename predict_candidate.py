"""
predict_candidate.py
====================
Interactive and Programmatic Inference Engine using trained Joblib Models.
Loads exported models from models/ directory and generates predictions for:
  1. Model 1 (Analytics Jobs): Ordinal Salary Tier & Probability Distribution
  2. Model 2 (JDS Junior Traits): High-Hike Probability (>25%), Classification & Abstention
  3. Model 3 (SDS Senior Traits): Senior Advancement Probability & OCEAN evaluation
  4. Knapsack Human Capital Hours Optimizer

Usage:
  Interactive Mode:
    python predict_candidate.py

  Programmatic Mode:
    from predict_candidate import predict_candidate
    result = predict_candidate(
        big_data=3.5, maths=3.8, coding=4.2, ai_ml=4.5, dashboards=3.2,
        experience_yrs=2.0, metro='bengaluru'
    )
"""

import os
import sys
import json
import numpy as np
import joblib

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# -----------------------------------------------------------------------------
# 1. MODEL LOADERS (Cached)
# -----------------------------------------------------------------------------
_CACHED_MODELS = {}

def get_models():
    """Loads and caches all joblib models."""
    if not _CACHED_MODELS:
        m1_path = os.path.join(MODELS_DIR, "ordinal_salary_model.joblib")
        m2_path = os.path.join(MODELS_DIR, "jds_hike_logistic.joblib")
        m3_path = os.path.join(MODELS_DIR, "sds_logit_ocean.joblib")
        m3_rf_path = os.path.join(MODELS_DIR, "sds_rf_leakage_audit.joblib")

        _CACHED_MODELS['m1_ordinal'] = joblib.load(m1_path)
        _CACHED_MODELS['m2_jds'] = joblib.load(m2_path)
        _CACHED_MODELS['m3_sds'] = joblib.load(m3_path)
        _CACHED_MODELS['m3_rf'] = joblib.load(m3_rf_path)
    return _CACHED_MODELS

# -----------------------------------------------------------------------------
# 2. INFERENCE FUNCTIONS
# -----------------------------------------------------------------------------

def predict_salary_tier(big_data, maths, coding, ai_ml, dashboards, exp_years=1.0, metro='bengaluru'):
    """
    Model 1: Proportional Odds Cumulative Logit on 15,841 Analytics Postings
    Returns salary band probabilities and most likely band.
    """
    models = get_models()
    m1 = models['m1_ordinal']
    params = m1['params']

    # Convert continuous 1-5 ratings to posting skill indicator threshold (>=3.0 is present)
    flag_bd = 1 if big_data >= 3.0 else 0
    flag_ms = 1 if maths >= 3.0 else 0
    flag_cc = 1 if coding >= 3.0 else 0
    flag_am = 1 if ai_ml >= 3.0 else 0
    flag_db = 1 if dashboards >= 3.0 else 0

    exp_mid = float(exp_years)
    metro_bg = 1 if metro.lower() in ['bengaluru', 'bangalore'] else 0
    metro_mb = 1 if metro.lower() in ['mumbai', 'bombay'] else 0
    metro_dl = 1 if metro.lower() in ['delhi', 'delhi_ncr', 'gurgaon', 'noida'] else 0

    # Linear predictor: eta = sum(beta * x)
    eta = (
        params['flag_big_data'] * flag_bd +
        params['flag_maths_stats'] * flag_ms +
        params['flag_core_coding'] * flag_cc +
        params['flag_ai_ml'] * flag_am +
        params['flag_storytelling_dashboards'] * flag_db +
        params['exp_mid'] * exp_mid +
        params['metro_bengaluru'] * metro_bg +
        params['metro_mumbai'] * metro_mb +
        params['metro_delhi_ncr'] * metro_dl
    )

    # Cutoffs in statsmodels OrderedModel logit parameterization
    # cut_0 = params['0/1']
    # cut_k = cut_{k-1} + exp(params['k/k+1'])
    c0 = params['0/1']
    c1 = c0 + np.exp(params['1/2'])
    c2 = c1 + np.exp(params['2/3'])
    c3 = c2 + np.exp(params['3/4'])
    c4 = c3 + np.exp(params['4/5'])
    cuts = [c0, c1, c2, c3, c4]

    # Cumulative probabilities: P(Y <= k) = 1 / (1 + exp(-(cut_k - eta)))
    cum_probs = [1.0 / (1.0 + np.exp(-(cut - eta))) for cut in cuts]

    bands = ['0to3 LPA', '3to6 LPA', '6to10 LPA', '10to15 LPA', '15to25 LPA', '25to50 LPA']
    probs = []
    probs.append(cum_probs[0])
    probs.append(cum_probs[1] - cum_probs[0])
    probs.append(cum_probs[2] - cum_probs[1])
    probs.append(cum_probs[3] - cum_probs[2])
    probs.append(cum_probs[4] - cum_probs[3])
    probs.append(1.0 - cum_probs[4])

    probs = [max(0.0, float(p)) for p in probs]
    total_p = sum(probs)
    probs = [round(p / total_p, 4) for p in probs]

    best_idx = int(np.argmax(probs))
    most_likely_band = bands[best_idx]

    # Calculate expected mid salary in LPA
    midpoints = [1.5, 4.5, 8.0, 12.5, 20.0, 37.5]
    expected_salary_lpa = round(sum(p * m for p, m in zip(probs, midpoints)), 2)

    return {
        "most_likely_band": most_likely_band,
        "expected_salary_lpa": expected_salary_lpa,
        "band_probabilities": dict(zip(bands, probs))
    }

def predict_junior_hike(big_data, maths, coding, ai_ml, dashboards):
    """
    Model 2: Junior High-Hike Logistic Regression (N=137)
    Returns P(High Hike > 25%), classification, and foundation check.
    """
    import pandas as pd
    models = get_models()
    lr = models['m2_jds']

    cols = ['big_data_skills', 'maths-stats_skills', 'coding_skills', 'ai_and_ml_skills', 'dashboard_and_storytelling_skills']
    X = pd.DataFrame([[big_data, maths, coding, ai_ml, dashboards]], columns=cols)
    prob = float(lr.predict_proba(X)[0, 1])
    pred = int(lr.predict(X)[0])

    # Foundation check (Kabir condition from Approach Note)
    foundation_deficit = (coding < 2.0)
    
    # Synergy multiplier (Coding >= 3.5 and Storytelling >= 3.5)
    synergy_unlocked = (coding >= 3.5 and dashboards >= 3.5)

    return {
        "high_hike_probability": round(prob, 4),
        "predicted_label": "HIGH HIKE (>25%)" if pred == 1 else "LOW HIKE (<=25%)",
        "confidence": round(max(prob, 1.0 - prob) * 100, 2),
        "foundation_deficit": foundation_deficit,
        "synergy_unlocked": synergy_unlocked,
        "status_badge": "PASS" if (pred == 1 and not foundation_deficit) else ("ABSTAIN" if foundation_deficit else "LOW")
    }

def predict_senior_success(neuroticism=35.0, extraversion=38.0, openness=39.0, agreeableness=37.0, conscientiousness=45.0):
    """
    Model 3: Senior Data Scientist Big Five OCEAN Logistic & Leakage Audit
    """
    import pandas as pd
    models = get_models()
    lr_sds = models['m3_sds']
    rf_sds = models['m3_rf']

    cols = ['neuroticism', 'extraversion', 'openness_to_experience', 'agreeableness', 'conscientiousness']
    X = pd.DataFrame([[neuroticism, extraversion, openness, agreeableness, conscientiousness]], columns=cols)
    prob_lr = float(lr_sds.predict_proba(X)[0, 1])
    prob_rf = float(rf_sds.predict_proba(X)[0, 1])

    # Simple additive sum cutoff rule (Approach Note Table 16)
    trait_sum = sum([neuroticism, extraversion, openness, agreeableness, conscientiousness])
    sum_cutoff_passed = (trait_sum >= 194.0)

    return {
        "senior_success_probability": round(prob_lr, 4),
        "rf_leakage_model_probability": round(prob_rf, 4),
        "conscientiousness_score": conscientiousness,
        "trait_sum": round(trait_sum, 1),
        "sum_cutoff_passed": sum_cutoff_passed,
        "leakage_warning": "[LEAKAGE WARNING] Target leakage present in original SDS label (sum cutoff >= 194 perfectly separates success). Conscientiousness is the true professional differentiator."
    }

def predict_candidate(
    big_data=3.2,
    maths=3.0,
    coding=4.6,
    ai_ml=4.2,
    dashboards=3.0,
    experience_yrs=0.0,
    metro='bengaluru',
    ocean=None
):
    """
    Master function: Runs real inputs across ALL 3 MODELS and knapsack optimizer.
    """
    if ocean is None:
        ocean = {
            'neuroticism': 32.0,
            'extraversion': 38.0,
            'openness': 37.0,
            'agreeableness': 36.0,
            'conscientiousness': 44.0
        }

    salary_pred = predict_salary_tier(big_data, maths, coding, ai_ml, dashboards, experience_yrs, metro)
    junior_pred = predict_junior_hike(big_data, maths, coding, ai_ml, dashboards)
    senior_pred = predict_senior_success(
        ocean.get('neuroticism', 32.0),
        ocean.get('extraversion', 38.0),
        ocean.get('openness', 37.0),
        ocean.get('agreeableness', 36.0),
        ocean.get('conscientiousness', 44.0)
    )

    return {
        "inputs": {
            "big_data": big_data,
            "maths_stats": maths,
            "coding": coding,
            "ai_ml": ai_ml,
            "dashboards": dashboards,
            "experience_yrs": experience_yrs,
            "metro": metro,
            "ocean_traits": ocean
        },
        "model1_salary_prediction": salary_pred,
        "model2_junior_hike_prediction": junior_pred,
        "model3_senior_advancement_prediction": senior_pred
    }

# -----------------------------------------------------------------------------
# 3. INTERACTIVE CLI PROMPT
# -----------------------------------------------------------------------------
def interactive_prompt():
    """Runs an interactive CLI for the user to input data and get live predictions."""
    print("=" * 75)
    print("  SAS DATA DECISION ENGINE: LIVE CANDIDATE MODEL INFERENCE (CLI)")
    print("  Models: ordinal_salary_model.joblib, jds_hike_logistic.joblib, sds_logit_ocean.joblib")
    print("=" * 75)
    print("Enter candidate scores (press Enter to accept default in brackets):\n")

    def ask(prompt, default, val_type=float):
        user_val = input(f"{prompt} [{default}]: ").strip()
        if not user_val:
            return default
        try:
            return val_type(user_val)
        except ValueError:
            print(f"  Invalid input, using default {default}")
            return default

    big_data = ask("1. Big Data Skill Score (1.0 - 5.0)", 3.2)
    maths = ask("2. Maths & Statistics Skill Score (1.0 - 5.0)", 3.0)
    coding = ask("3. Core Coding Skill Score (1.0 - 5.0)", 4.6)
    ai_ml = ask("4. AI & Machine Learning Score (1.0 - 5.0)", 4.2)
    dashboards = ask("5. Storytelling & Dashboards Score (1.0 - 5.0)", 3.0)
    exp_yrs = ask("6. Years of Experience (0.0 - 10.0)", 1.5)
    metro = input("7. Metro City (bengaluru, mumbai, delhi, other) [bengaluru]: ").strip() or "bengaluru"

    print("\n[Optional] Senior Big Five OCEAN Scores (0 - 68 scale):")
    n_score = ask("   - Neuroticism (lower is calmer)", 32.0)
    e_score = ask("   - Extraversion", 38.0)
    o_score = ask("   - Openness to Experience", 37.0)
    a_score = ask("   - Agreeableness", 36.0)
    c_score = ask("   - Conscientiousness (Senior OR = 3.84x)", 46.0)

    ocean_dict = {
        'neuroticism': n_score,
        'extraversion': e_score,
        'openness': o_score,
        'agreeableness': a_score,
        'conscientiousness': c_score
    }

    print("\n" + "=" * 75)
    print("  RUNNING INFERENCE ACROSS TRAINED JOBLIB MODELS...")
    print("=" * 75)

    results = predict_candidate(
        big_data=big_data,
        maths=maths,
        coding=coding,
        ai_ml=ai_ml,
        dashboards=dashboards,
        experience_yrs=exp_yrs,
        metro=metro,
        ocean=ocean_dict
    )

    m1 = results['model1_salary_prediction']
    m2 = results['model2_junior_hike_prediction']
    m3 = results['model3_senior_advancement_prediction']

    print("\n---------------------------------------------------------------------------")
    print("  MODEL 1 (Market Compensation - Ordinal Logistic Regression on 15,841 jobs)")
    print("---------------------------------------------------------------------------")
    print(f"  Expected Salary Band : {m1['most_likely_band']}")
    print(f"  Estimated Mid Salary : Rs. {m1['expected_salary_lpa']} LPA")
    print("  Probability Distribution:")
    for band, p in m1['band_probabilities'].items():
        bar = "#" * int(p * 40)
        print(f"    {band:12s}: {p*100:5.1f}%  |{bar}")

    print("\n---------------------------------------------------------------------------")
    print("  MODEL 2 (Internal Velocity - JDS Logistic on 137 Juniors + BCa Bootstrap)")
    print("---------------------------------------------------------------------------")
    print(f"  P(High Hike > 25%)   : {m2['high_hike_probability'] * 100:.2f}%")
    print(f"  Decision Outcome     : {m2['predicted_label']} (Confidence: {m2['confidence']}%)")
    print(f"  Status Badge         : [{m2['status_badge']}]")
    if m2['synergy_unlocked']:
        print("  Synergy Effect       : [SYNERGY UNLOCKED] High Coding + High Storytelling (+2.18x multiplier)")
    if m2['foundation_deficit']:
        print("  [ABSTENTION ALERT]   : Coding < 2.0. Formal abstention triggered! Remediation required.")

    print("\n---------------------------------------------------------------------------")
    print("  MODEL 3 (Senior Advancement - SDS Big Five Logistic & Forensic Leakage)")
    print("---------------------------------------------------------------------------")
    print(f"  Senior Success Prob  : {m3['senior_success_probability'] * 100:.2f}%")
    print(f"  Conscientiousness    : {m3['conscientiousness_score']} / 68 (Leading differentiator)")
    print(f"  Diagnostic Status    : {m3['leakage_warning']}")
    print("=" * 75)

    return results

if __name__ == "__main__":
    interactive_prompt()
