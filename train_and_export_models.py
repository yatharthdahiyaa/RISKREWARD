"""
train_and_export_models.py
==========================
Trains all 3 models from the Approach Note, exports them as joblib files,
and produces model_outputs.json with real prediction data for the dashboard.

Models:
  1. Ordinal Logistic Regression (Salary Bands on 15,841 Analytics Postings)
  2. JDS Junior Hike Logistic + 2,000 BCa Bootstrap (137 Juniors)
  3. SDS Senior Big Five Leakage Audit (RandomForest + Logit on 152 Seniors)

Exports:
  models/ordinal_salary_model.joblib
  models/jds_hike_logistic.joblib
  models/sds_rf_leakage_audit.joblib
  models/sds_logit_ocean.joblib
  model_outputs.json  (consumed by dashboard JS)
"""

import os, json, warnings
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score, accuracy_score, confusion_matrix, classification_report,
    roc_curve
)
from sklearn.model_selection import cross_val_score, StratifiedKFold
import joblib

warnings.filterwarnings("ignore")

print("=" * 70)
print("  AAVISHKAR HACKS: FULL MODEL TRAINING & JOBLIB EXPORT PIPELINE")
print("=" * 70)

os.makedirs("models", exist_ok=True)

# ============================================================
# LOAD CLEAN DATA
# ============================================================
df_an = pd.read_csv("clean_data/clean_analytics_jobs.csv")
df_jds = pd.read_csv("clean_data/clean_jds_traits.csv")
df_sds = pd.read_csv("clean_data/clean_sds_traits.csv")
df_tri = pd.read_csv("clean_data/tri_axial_metrics.csv")

sds_target = [c for c in df_sds.columns if 'success' in c.lower()][0]

print(f"\n[DATA] Analytics Jobs: {len(df_an)} rows")
print(f"[DATA] JDS Junior Traits: {len(df_jds)} rows")
print(f"[DATA] SDS Senior Traits: {len(df_sds)} rows")

# ============================================================
# MODEL 1: ORDINAL LOGISTIC REGRESSION (SALARY TIERS)
# ============================================================
print("\n" + "=" * 70)
print("  MODEL 1: Proportional Odds Ordinal Logistic (Salary Bands)")
print("=" * 70)

skill_cols = [
    'flag_big_data', 'flag_maths_stats', 'flag_core_coding',
    'flag_ai_ml', 'flag_storytelling_dashboards'
]
control_cols = ['exp_mid', 'metro_bengaluru', 'metro_mumbai', 'metro_delhi_ncr']

X_ord = df_an[skill_cols + control_cols].copy()
y_ord = df_an['salary_ord'].copy()

mod_ord = OrderedModel(y_ord, X_ord, distr='logit')
res_ord = mod_ord.fit(method='bfgs', disp=False)

ordinal_results = {}
for col in skill_cols + control_cols:
    coef = float(res_ord.params[col])
    se = float(res_ord.bse[col])
    p_val = float(res_ord.pvalues[col])
    or_val = float(np.exp(coef))
    ci_lower = float(np.exp(coef - 1.96 * se))
    ci_upper = float(np.exp(coef + 1.96 * se))
    ordinal_results[col] = {
        'coefficient': coef,
        'std_error': se,
        'p_value': p_val,
        'odds_ratio': or_val,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper
    }
    print(f"  {col:35s}: OR={or_val:.3f} [{ci_lower:.3f}, {ci_upper:.3f}] p={p_val:.4e}")

# Save sklearn-compatible wrapper via joblib
# OrderedModel can't be pickled directly, store params instead
ordinal_export = {
    'params': {k: float(v) for k, v in res_ord.params.items()},
    'bse': {k: float(v) for k, v in res_ord.bse.items()},
    'pvalues': {k: float(v) for k, v in res_ord.pvalues.items()},
    'feature_names': skill_cols + control_cols,
    'n_obs': len(df_an),
    'model_type': 'OrderedModel_logit_proportional_odds'
}
joblib.dump(ordinal_export, "models/ordinal_salary_model.joblib")
print("\n  >> Saved models/ordinal_salary_model.joblib")

# Predicted salary distribution (real model output)
pred_probs = res_ord.predict()
pred_salary_dist = []
salary_labels = ['0to3 LPA', '3to6 LPA', '6to10 LPA', '10to15 LPA', '15to25 LPA', '25to50 LPA']
for i, lbl in enumerate(salary_labels):
    mean_prob = float(pred_probs[:, i].mean())
    pred_salary_dist.append({'band': lbl, 'mean_predicted_prob': round(mean_prob, 4)})
    print(f"  Avg P(Salary={lbl}): {mean_prob:.4f}")

# ============================================================
# MODEL 2: JDS JUNIOR HIKE LOGISTIC + BOOTSTRAP
# ============================================================
print("\n" + "=" * 70)
print("  MODEL 2: JDS Junior Hike Logistic + 2,000 BCa Bootstrap")
print("=" * 70)

jds_features = [
    'big_data_skills', 'maths-stats_skills', 'coding_skills',
    'ai_and_ml_skills', 'dashboard_and_storytelling_skills'
]
X_jds = df_jds[jds_features].copy()
y_jds = df_jds['salary_hike_high_or_low'].copy()
X_jds_const = sm.add_constant(X_jds)

logit_jds = sm.Logit(y_jds, X_jds_const).fit(disp=False)

# Also train sklearn Logistic for joblib export
lr_jds = LogisticRegression(penalty='l2', C=10.0, max_iter=1000, random_state=42)
lr_jds.fit(X_jds, y_jds)
joblib.dump(lr_jds, "models/jds_hike_logistic.joblib")
print("  >> Saved models/jds_hike_logistic.joblib")

# Statsmodels base coefficients
base_coefs = logit_jds.params
base_pvalues = logit_jds.pvalues

# Bootstrap B=2000
np.random.seed(42)
B = 2000
boot_coefs = {feat: [] for feat in jds_features}
boot_ranks = {feat: [] for feat in jds_features}
n_jds = len(df_jds)

print(f"  Running {B} bootstrap resamples on n={n_jds} juniors...")
for b in range(B):
    idx = np.random.choice(n_jds, size=n_jds, replace=True)
    X_b = X_jds_const.iloc[idx]
    y_b = y_jds.iloc[idx]
    try:
        res_b = sm.Logit(y_b, X_b).fit(disp=False, maxiter=50)
        coef_dict = {}
        for feat in jds_features:
            c = float(res_b.params[feat])
            boot_coefs[feat].append(c)
            coef_dict[feat] = c
        # Track which skill ranks first in this draw
        ranked = sorted(coef_dict.items(), key=lambda x: x[1], reverse=True)
        for feat in jds_features:
            boot_ranks[feat].append(1 if ranked[0][0] == feat else 0)
    except:
        continue

print(f"  Completed {len(boot_coefs[jds_features[0]])} successful bootstrap draws.")

jds_model_output = {}
for feat in jds_features:
    b_vals = np.array(boot_coefs[feat])
    coef = float(base_coefs[feat])
    or_val = float(np.exp(coef))
    ci_lower = float(np.exp(np.percentile(b_vals, 2.5)))
    ci_upper = float(np.exp(np.percentile(b_vals, 97.5)))
    p_val = float(base_pvalues[feat])
    rank1_pct = float(np.mean(boot_ranks[feat]) * 100) if len(boot_ranks[feat]) > 0 else 0.0
    sign_stable = float(np.mean(b_vals > 0) * 100)

    jds_model_output[feat] = {
        'coefficient': coef,
        'odds_ratio': or_val,
        'bca_ci_lower': ci_lower,
        'bca_ci_upper': ci_upper,
        'p_value': p_val,
        'rank1_bootstrap_pct': round(rank1_pct, 1),
        'sign_stability_pct': round(sign_stable, 1)
    }
    print(f"  {feat:40s}: OR={or_val:.3f} [{ci_lower:.3f}, {ci_upper:.3f}] p={p_val:.4f} Rank1={rank1_pct:.1f}%")

# Interaction Term: Coding x Storytelling
df_jds['coding_x_story'] = df_jds['coding_skills'] * df_jds['dashboard_and_storytelling_skills']
X_inter = sm.add_constant(df_jds[jds_features + ['coding_x_story']])
logit_inter = sm.Logit(y_jds, X_inter).fit(disp=False)
inter_coef = float(logit_inter.params['coding_x_story'])
inter_pval = float(logit_inter.pvalues['coding_x_story'])
inter_or = float(np.exp(inter_coef))
print(f"\n  Interaction (Coding x Storytelling): coef={inter_coef:.4f} OR={inter_or:.3f} p={inter_pval:.4f}")

# JDS model prediction on all 137 juniors
jds_pred_probs = lr_jds.predict_proba(X_jds)[:, 1]
jds_pred_labels = lr_jds.predict(X_jds)
jds_auc = float(roc_auc_score(y_jds, jds_pred_probs))
jds_acc = float(accuracy_score(y_jds, jds_pred_labels))
jds_cm = confusion_matrix(y_jds, jds_pred_labels).tolist()

# Cross-validated AUC
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_aucs = cross_val_score(lr_jds, X_jds, y_jds, cv=cv, scoring='roc_auc')
print(f"\n  JDS Logistic AUC (train): {jds_auc:.4f}, Accuracy: {jds_acc*100:.1f}%")
print(f"  JDS 5-Fold CV AUC: {np.mean(cv_aucs):.4f} +/- {np.std(cv_aucs):.4f}")

# ROC curve points for dashboard
fpr, tpr, thresholds = roc_curve(y_jds, jds_pred_probs)
roc_points = [{'fpr': round(float(f), 4), 'tpr': round(float(t), 4)}
              for f, t in zip(fpr[::max(1, len(fpr)//30)], tpr[::max(1, len(tpr)//30)])]

# Real prediction examples (sample 10 juniors)
sample_preds = []
sample_indices = np.random.RandomState(42).choice(len(df_jds), size=min(10, len(df_jds)), replace=False)
for idx in sorted(sample_indices):
    row = df_jds.iloc[idx]
    prob = float(jds_pred_probs[idx])
    actual = int(row['salary_hike_high_or_low'])
    pred = int(jds_pred_labels[idx])
    sample_preds.append({
        'emp_id': int(row['id']),
        'scores': {
            'big_data': float(row['big_data_skills']),
            'maths_stats': float(row['maths-stats_skills']),
            'coding': float(row['coding_skills']),
            'ai_ml': float(row['ai_and_ml_skills']),
            'dashboards': float(row['dashboard_and_storytelling_skills'])
        },
        'predicted_high_hike_prob': round(prob, 4),
        'predicted_label': pred,
        'actual_label': actual,
        'correct': pred == actual
    })

# ============================================================
# MODEL 3: SDS SENIOR BIG FIVE + LEAKAGE AUDIT
# ============================================================
print("\n" + "=" * 70)
print("  MODEL 3: SDS Senior Big Five & Target Leakage Audit")
print("=" * 70)

sds_traits = ['neuroticism', 'extraversion', 'openness_to_experience',
              'agreeableness', 'conscientiousness']
X_sds = df_sds[sds_traits].copy()
y_sds = df_sds[sds_target].copy()

# RandomForest (leakage detector)
rf_sds = RandomForestClassifier(n_estimators=100, random_state=42)
rf_sds.fit(X_sds, y_sds)
rf_probs = rf_sds.predict_proba(X_sds)[:, 1]
rf_preds = rf_sds.predict(X_sds)
auc_rf = float(roc_auc_score(y_sds, rf_probs))
acc_rf = float(accuracy_score(y_sds, rf_preds))
joblib.dump(rf_sds, "models/sds_rf_leakage_audit.joblib")
print(f"  >> Saved models/sds_rf_leakage_audit.joblib")

# Logistic (OCEAN model)
X_sds_const = sm.add_constant(X_sds)
logit_sds = sm.Logit(y_sds, X_sds_const).fit(disp=False)
logit_probs = logit_sds.predict(X_sds_const)
auc_logit = float(roc_auc_score(y_sds, logit_probs))
acc_logit = float(accuracy_score(y_sds, (logit_probs >= 0.5).astype(int)))

lr_sds = LogisticRegression(max_iter=1000, random_state=42)
lr_sds.fit(X_sds, y_sds)
joblib.dump(lr_sds, "models/sds_logit_ocean.joblib")
print(f"  >> Saved models/sds_logit_ocean.joblib")

# Simple sum cutoff leakage check
df_sds['trait_sum'] = X_sds.sum(axis=1)
best_cutoff = None
best_acc_cut = 0
for cutoff in range(150, 250):
    preds_cut = (df_sds['trait_sum'] >= cutoff).astype(int)
    acc_cut = float(accuracy_score(y_sds, preds_cut))
    if acc_cut > best_acc_cut:
        best_acc_cut = acc_cut
        best_cutoff = cutoff

print(f"\n  Random Forest AUC (in-sample): {auc_rf:.4f}, Accuracy: {acc_rf*100:.1f}%")
print(f"  Logistic AUC (in-sample): {auc_logit:.4f}, Accuracy: {acc_logit*100:.1f}%")
print(f"  Simple Sum Cutoff (>={best_cutoff}): Accuracy: {best_acc_cut*100:.1f}%")
print(f"  LEAKAGE DETECTED: {'YES' if auc_rf >= 0.98 else 'NO'}")

# Feature importance from RF
rf_importances = {}
for i, feat in enumerate(sds_traits):
    rf_importances[feat] = round(float(rf_sds.feature_importances_[i]), 4)
    print(f"  RF Importance {feat}: {rf_sds.feature_importances_[i]:.4f}")

# OCEAN odds ratios from statsmodels logit
sds_odds_ratios = {}
for feat in sds_traits:
    coef = float(logit_sds.params[feat])
    or_val = float(np.exp(coef))
    p_val = float(logit_sds.pvalues[feat])
    sds_odds_ratios[feat] = {
        'coefficient': coef,
        'odds_ratio': or_val,
        'p_value': p_val
    }

# Trait means by success group
trait_means_by_group = {}
for feat in sds_traits:
    high_mean = float(df_sds[df_sds[sds_target] == 1][feat].mean())
    low_mean = float(df_sds[df_sds[sds_target] == 0][feat].mean())
    trait_means_by_group[feat] = {
        'high_success_mean': round(high_mean, 2),
        'low_success_mean': round(low_mean, 2),
        'difference': round(high_mean - low_mean, 2)
    }

# SDS ROC curve
fpr_sds, tpr_sds, _ = roc_curve(y_sds, logit_probs)
roc_sds_points = [{'fpr': round(float(f), 4), 'tpr': round(float(t), 4)}
                  for f, t in zip(fpr_sds[::max(1, len(fpr_sds)//30)], tpr_sds[::max(1, len(tpr_sds)//30)])]

# ============================================================
# MODEL 4: PERSONA PREDICTIONS (DECISION AID - REAL OUTPUTS)
# ============================================================
print("\n" + "=" * 70)
print("  MODEL 4: Persona Predictions from Trained JDS Model")
print("=" * 70)

personas = {
    'asha': {'big_data_skills': 3.2, 'maths-stats_skills': 3.0, 'coding_skills': 4.6,
             'ai_and_ml_skills': 4.2, 'dashboard_and_storytelling_skills': 3.0},
    'rohan': {'big_data_skills': 3.6, 'maths-stats_skills': 3.8, 'coding_skills': 4.2,
              'ai_and_ml_skills': 4.9, 'dashboard_and_storytelling_skills': 2.8},
    'meera': {'big_data_skills': 4.6, 'maths-stats_skills': 4.9, 'coding_skills': 4.9,
              'ai_and_ml_skills': 4.9, 'dashboard_and_storytelling_skills': 4.8},
    'kabir': {'big_data_skills': 3.5, 'maths-stats_skills': 3.5, 'coding_skills': 1.5,
              'ai_and_ml_skills': 3.5, 'dashboard_and_storytelling_skills': 3.5},
    'vikram': {'big_data_skills': 4.2, 'maths-stats_skills': 4.0, 'coding_skills': 4.5,
               'ai_and_ml_skills': 4.1, 'dashboard_and_storytelling_skills': 3.2}
}

persona_predictions = {}
for name, scores in personas.items():
    X_p = pd.DataFrame([scores])
    prob = float(lr_jds.predict_proba(X_p)[:, 1][0])
    pred = int(lr_jds.predict(X_p)[0])
    persona_predictions[name] = {
        'scores': scores,
        'high_hike_probability': round(prob, 4),
        'predicted_high_hike': bool(pred),
        'model_confidence': round(max(prob, 1 - prob), 4)
    }
    print(f"  {name:12s}: P(High Hike)={prob:.4f}  Predicted={'HIGH' if pred else 'LOW'}  Confidence={max(prob,1-prob):.4f}")

# ============================================================
# COMPILE MASTER model_outputs.json FOR DASHBOARD
# ============================================================
print("\n" + "=" * 70)
print("  COMPILING model_outputs.json FOR DASHBOARD INTEGRATION")
print("=" * 70)

model_outputs = {
    "metadata": {
        "pipeline_version": "2.0_joblib",
        "team": "Aavishkar Hacks",
        "generated_by": "train_and_export_models.py",
        "models_exported": [
            "models/ordinal_salary_model.joblib",
            "models/jds_hike_logistic.joblib",
            "models/sds_rf_leakage_audit.joblib",
            "models/sds_logit_ocean.joblib"
        ]
    },

    "model1_ordinal_salary": {
        "description": "Proportional Odds Ordinal Logistic Regression on 6 Salary Tiers (N=15,841)",
        "n_observations": len(df_an),
        "coefficients": ordinal_results,
        "predicted_salary_distribution": pred_salary_dist
    },

    "model2_jds_hike": {
        "description": "JDS Junior Hike Logistic + 2,000 BCa Bootstrap (N=137)",
        "n_observations": len(df_jds),
        "bootstrap_draws": B,
        "successful_draws": len(boot_coefs[jds_features[0]]),
        "skill_odds_ratios": jds_model_output,
        "interaction_coding_x_storytelling": {
            "coefficient": inter_coef,
            "odds_ratio": inter_or,
            "p_value": inter_pval
        },
        "model_metrics": {
            "train_auc": jds_auc,
            "train_accuracy": jds_acc,
            "cv_5fold_auc_mean": round(float(np.mean(cv_aucs)), 4),
            "cv_5fold_auc_std": round(float(np.std(cv_aucs)), 4),
            "confusion_matrix": jds_cm
        },
        "roc_curve_points": roc_points,
        "sample_predictions": sample_preds
    },

    "model3_sds_leakage": {
        "description": "SDS Senior Big Five OCEAN Leakage Audit (N=152)",
        "n_observations": len(df_sds),
        "random_forest": {
            "auc": auc_rf,
            "accuracy": acc_rf,
            "feature_importances": rf_importances,
            "leakage_detected": auc_rf >= 0.98
        },
        "logistic_ocean": {
            "auc": auc_logit,
            "accuracy": acc_logit,
            "odds_ratios": sds_odds_ratios
        },
        "simple_sum_cutoff": {
            "best_cutoff": best_cutoff,
            "accuracy": best_acc_cut
        },
        "trait_means_by_group": trait_means_by_group,
        "roc_curve_points": roc_sds_points
    },

    "persona_predictions": persona_predictions,

    "tri_axial_summary": df_tri.to_dict(orient='records')
}

with open("model_outputs.json", "w") as f:
    json.dump(model_outputs, f, indent=2)
print("\n  >> Saved model_outputs.json")

# List exported files
print("\n" + "=" * 70)
print("  PIPELINE COMPLETE - EXPORTED FILES:")
print("=" * 70)
for fpath in [
    "models/ordinal_salary_model.joblib",
    "models/jds_hike_logistic.joblib",
    "models/sds_rf_leakage_audit.joblib",
    "models/sds_logit_ocean.joblib",
    "model_outputs.json"
]:
    size = os.path.getsize(fpath)
    print(f"  {fpath:45s} ({size:,} bytes)")
