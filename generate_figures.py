"""
generate_figures.py
===================
Generates publication-quality visualizations for the SAS CU Hackathon Round 2 & Round 3.
Saves all charts into the 'figures/' directory.
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns

# Configure aesthetic styles
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.labelweight'] = 'bold'

os.makedirs("figures", exist_ok=True)

# Load pipeline results
with open("pipeline_results.json", "r") as f:
    meta = json.load(f)

df_tri = pd.read_csv("clean_data/tri_axial_metrics.csv")
df_jds = pd.read_csv("clean_data/clean_jds_traits.csv")
df_sds = pd.read_csv("clean_data/clean_sds_traits.csv")
df_an = pd.read_csv("clean_data/clean_analytics_jobs.csv")

# -----------------------------------------------------------------
# FIGURE 1: Data Audit Landscape & Cohort Isolation Matrix
# -----------------------------------------------------------------
print("[Fig 1] Generating Data Audit Landscape Matrix...")
fig, ax = plt.subplots(figsize=(11, 6))
ax.axis('off')

# Title
fig.suptitle("Forensic Data Inventory & Cross-Cohort Isolation Matrix", fontsize=16, fontweight='bold', y=0.96)

# Create table data
table_data = [
    ["Dataset Name", "Raw Rows", "Clean Obs", "Granularity", "Primary Key Audit", "Missingness Profile", "Statistical Role"],
    ["Analytics Jobs.csv", "15,841", "15,841", "Posting Level", "s_no (100% unique)", "job_type 75.8% null; Salary 0% null", "External Listed & Paid Model"],
    ["DataScience Jobs.csv", "1,602", "1,602", "Company Agg", "reference_no", "0% missing; 93,005 vacancies", "Macro Hiring & Salary Benchmarks"],
    ["JDS Skill Traits.xlsx", "171 (grid)", "137 unique", "Junior Employee", "32 ghost rows dropped, 2 dups avg", "Scores 100% complete (1-5 scale)", "Internal Rewarded Hike Model"],
    ["SDS Personality Traits.xlsx", "161", "152 unique", "Senior Consultant", "9 duplicate IDs averaged", "OCEAN scores complete (17-68)", "Career-Stage & Leakage Audit"]
]

table = ax.table(cellText=table_data, loc='center', cellLoc='left')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.0, 2.2)

# Style header row
for j in range(7):
    table[(0, j)].set_facecolor('#1A365D')
    table[(0, j)].get_text().set_color('white')
    table[(0, j)].get_text().set_weight('bold')

# Alternating row colors
for i in range(1, 5):
    color = '#F7FAFC' if i % 2 == 1 else '#EDF2F7'
    for j in range(7):
        table[(i, j)].set_facecolor(color)

# Add highlight box below
ax.text(0.5, 0.12, 
        "[CRITICAL AUDIT LAW]: Cohort Intersection JDS ∩ SDS = ∅ (Zero Overlapping IDs)\n"
        "JDS and SDS represent independent cross-sectional cohorts, not a longitudinal tracked career panel.",
        ha='center', va='center', transform=ax.transAxes,
        fontsize=11, fontweight='bold', color='#9B2C2C',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#FFF5F5', edgecolor='#FEB2B2', lw=2))

plt.tight_layout()
plt.savefig("figures/fig1_data_audit_matrix.png", bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------
# FIGURE 2: Axis 1 - Listed Frequency Distribution
# -----------------------------------------------------------------
print("[Fig 2] Generating Axis 1: Listed Frequency Distribution...")
fig, ax = plt.subplots(figsize=(10, 5))

df_tri_sorted = df_tri.sort_values('Listed_Share_Pct', ascending=True)
colors = ['#2B6CB0' if s not in ['Storytelling & Dashboards', 'Core Coding'] else '#3182CE' for s in df_tri_sorted['Skill_Area']]

bars = ax.barh(df_tri_sorted['Skill_Area'], df_tri_sorted['Listed_Share_Pct'], color=colors, height=0.55, edgecolor='black', alpha=0.85)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.4, bar.get_y() + bar.get_height()/2, f"{w:.1f}% ({int(w*158.41):,} jobs)", 
            ha='left', va='center', fontsize=11, fontweight='bold', color='#2D3748')

ax.set_xlim(0, 30)
ax.set_xlabel("Share of Total Job Postings (%) [N = 15,841 Postings]")
ax.set_title("Axis 1 (Listed): Skill Occurrence Rate in External Postings", pad=15)
ax.axvline(df_tri['Listed_Share_Pct'].mean(), color='#E53E3E', linestyle='--', label=f"Mean Share: {df_tri['Listed_Share_Pct'].mean():.1f}%")
ax.legend(loc='lower right', frameon=True)

plt.tight_layout()
plt.savefig("figures/fig2_listed_frequency_distribution.png", bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------
# FIGURE 3: Axis 2 - Paid Salary-Band Odds Ratios (Forest Plot)
# -----------------------------------------------------------------
print("[Fig 3] Generating Axis 2: Paid Salary-Band Odds Ratios Forest Plot...")
fig, ax = plt.subplots(figsize=(10, 5.5))

df_paid_sorted = df_tri.sort_values('Paid_Odds_Ratio', ascending=True)
y_pos = np.arange(len(df_paid_sorted))

ax.errorbar(df_paid_sorted['Paid_Odds_Ratio'], y_pos, 
             xerr=[df_paid_sorted['Paid_Odds_Ratio'] - df_paid_sorted['Paid_CI_Lower'],
                   df_paid_sorted['Paid_CI_Upper'] - df_paid_sorted['Paid_Odds_Ratio']],
             fmt='o', color='#2C5282', ecolor='#4299E1', elinewidth=3, capsize=6, capthick=2, markersize=9)

for i, (_, row) in enumerate(df_paid_sorted.iterrows()):
    ax.text(row['Paid_Odds_Ratio'], i + 0.22, 
            f"OR = {row['Paid_Odds_Ratio']:.2f} [{row['Paid_CI_Lower']:.2f}, {row['Paid_CI_Upper']:.2f}]",
            ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1A365D')

ax.set_yticks(y_pos)
ax.set_yticklabels(df_paid_sorted['Skill_Area'], fontsize=11, fontweight='bold')
ax.axvline(1.0, color='#E53E3E', linestyle='--', linewidth=1.5, label='Parity (No Salary Band Shift, OR = 1.0)')
ax.set_xlabel("Marginal Odds Ratio for Higher Salary Band [Proportional Odds Cumulative Logit]")
ax.set_title("Axis 2 (Paid): Skill Premium on External Salary Tiers (Controlling for Exp & Location)", pad=15)
ax.set_xlim(0.8, 2.5)
ax.legend(loc='lower right', frameon=True)

plt.tight_layout()
plt.savefig("figures/fig3_paid_salary_band_odds_ratios.png", bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------
# FIGURE 4: Axis 3 - Rewarded Junior Hike Bootstrap Forest Plot
# -----------------------------------------------------------------
print("[Fig 4] Generating Axis 3: Rewarded Junior Hike Bootstrap Forest Plot...")
fig, ax = plt.subplots(figsize=(10, 5.5))

df_rew_sorted = df_tri.sort_values('Rewarded_Odds_Ratio', ascending=True)
y_pos = np.arange(len(df_rew_sorted))

ax.errorbar(df_rew_sorted['Rewarded_Odds_Ratio'], y_pos, 
             xerr=[df_rew_sorted['Rewarded_Odds_Ratio'] - df_rew_sorted['Rewarded_CI_Lower'],
                   df_rew_sorted['Rewarded_CI_Upper'] - df_rew_sorted['Rewarded_Odds_Ratio']],
             fmt='s', color='#276749', ecolor='#48BB78', elinewidth=3, capsize=6, capthick=2, markersize=9)

for i, (_, row) in enumerate(df_rew_sorted.iterrows()):
    ax.text(row['Rewarded_Odds_Ratio'], i + 0.22, 
            f"OR = {row['Rewarded_Odds_Ratio']:.2f} [Boot CI: {row['Rewarded_CI_Lower']:.2f}, {row['Rewarded_CI_Upper']:.2f}]",
            ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1C4532')

ax.set_yticks(y_pos)
ax.set_yticklabels(df_rew_sorted['Skill_Area'], fontsize=11, fontweight='bold')
ax.axvline(1.0, color='#E53E3E', linestyle='--', linewidth=1.5, label='Parity (No Hike Advantage, OR = 1.0)')
ax.set_xlabel("Odds Ratio of High Salary Hike per Point Gain [Firth GLM + 2,000 Bootstrap Resamples]")
ax.set_title("Axis 3 (Rewarded): Internal Performance Hike Odds for Junior Data Scientists (n = 137)", pad=15)
ax.set_xlim(0.5, 23.0)
ax.legend(loc='lower right', frameon=True)

plt.tight_layout()
plt.savefig("figures/fig4_rewarded_junior_hike_bootstrap.png", bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------
# FIGURE 5: THE HEADLINE TRIPLE CHART (Listed vs Paid vs Rewarded)
# -----------------------------------------------------------------
print("[Fig 5] Generating Master Headline Triple Chart...")
fig, ax = plt.subplots(figsize=(12, 6.5))

x = np.arange(len(df_tri))
width = 0.26

rects1 = ax.bar(x - width, df_tri['Z_Listed'], width, label='Axis 1: Listed (Posting Share Z-Score)', color='#3182CE', edgecolor='black', alpha=0.9)
rects2 = ax.bar(x, df_tri['Z_Paid'], width, label='Axis 2: Paid (Salary Band Odds Ratio Z-Score)', color='#D69E2E', edgecolor='black', alpha=0.9)
rects3 = ax.bar(x + width, df_tri['Z_Rewarded'], width, label='Axis 3: Rewarded (Internal Hike Odds Ratio Z-Score)', color='#38A169', edgecolor='black', alpha=0.9)

ax.set_ylabel('Standardized Effect (Z-Score)', fontsize=12, fontweight='bold')
ax.set_title('THE HEADLINE PARADOX: Listed vs. Paid vs. Rewarded\n'
             f"Spearman Rank Discordance: Listed vs Paid (rho = {meta['correlations']['spearman_listed_paid']:.2f}) | "
             f"Paid vs Rewarded (rho = +{meta['correlations']['spearman_paid_rewarded']:.2f})", 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(df_tri['Skill_Area'], fontsize=11, fontweight='bold')
ax.axhline(0, color='gray', linestyle='-', linewidth=0.8)
ax.legend(frameon=True, fontsize=11)

# Annotate the key paradoxes
# Core Coding
ax.annotate('THE ENTRY TRAP:\nHeavily Listed, but\nlowest hike differentiation',
            xy=(2 - width, df_tri.loc[2, 'Z_Listed']), xytext=(1.8, 1.8),
            arrowprops=dict(facecolor='#E53E3E', shrink=0.08, width=2, headwidth=7),
            fontsize=9.5, fontweight='bold', color='#9B2C2C', ha='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF5F5', edgecolor='#FEB2B2'))

# Maths-Stats
ax.annotate('THE HIDDEN PREMIUM:\nModerate listing share, but\nhighest Paid & Rewarded return!',
            xy=(1 + width, df_tri.loc[1, 'Z_Rewarded']), xytext=(0.8, 1.9),
            arrowprops=dict(facecolor='#276749', shrink=0.08, width=2, headwidth=7),
            fontsize=9.5, fontweight='bold', color='#1C4532', ha='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#F0FFF4', edgecolor='#9AE6B4'))

plt.tight_layout()
plt.savefig("figures/fig5_tri_axial_triple_chart.png", bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------
# FIGURE 6: Coding x Storytelling Synergy Interaction Heatmap
# -----------------------------------------------------------------
print("[Fig 6] Generating Coding x Storytelling Synergy Heatmap...")
fig, ax = plt.subplots(figsize=(8.5, 6.5))

coding_range = np.linspace(2.0, 5.0, 30)
story_range = np.linspace(2.0, 5.0, 30)
C_mesh, S_mesh = np.meshgrid(coding_range, story_range)

# Interaction surface formula based on empirical fit
# Logit = b0 + b_c*C + b_s*S + b_cs*C*S + other_mean_effects
b0 = -25.5
b_c = 0.624
b_s = 1.255
b_cs = 0.425
other_effects = 1.004*3.85 + 1.719*4.29 + 1.295*4.57  # baseline other skills at sample mean

logit_mesh = b0 + other_effects + b_c * C_mesh + b_s * S_mesh + b_cs * (C_mesh - 3.5) * (S_mesh - 3.5)
prob_mesh = 1.0 / (1.0 + np.exp(-logit_mesh))

cp = ax.contourf(C_mesh, S_mesh, prob_mesh, levels=12, cmap='viridis', alpha=0.9)
cbar = fig.colorbar(cp, ax=ax)
cbar.set_label("Probability of High Salary Hike P(Hike = 1)", fontweight='bold')

# Contour lines
cs = ax.contour(C_mesh, S_mesh, prob_mesh, levels=[0.3, 0.5, 0.7, 0.85, 0.95], colors='white', linewidths=1.2)
ax.clabel(cs, inline=True, fontsize=10, fmt='%.2f')

ax.set_xlabel("Coding Skills Score (1.0 to 5.0 Scale)", fontweight='bold')
ax.set_ylabel("Dashboard & Storytelling Score (1.0 to 5.0 Scale)", fontweight='bold')
ax.set_title("Super-Additive Synergy: Coding × Storytelling on Junior Hike Probability", pad=15)

plt.tight_layout()
plt.savefig("figures/fig6_coding_storytelling_synergy.png", bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------
# FIGURE 7: Career Stage Divergence & Diagnostic Leakage Audit
# -----------------------------------------------------------------
print("[Fig 7] Generating Career Stage Divergence & Leakage Audit...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

# Subplot 1: Junior Technical Drivers vs Senior Personality
skills_jds = ['Maths-Stats', 'AI & ML', 'Storytelling', 'Big Data', 'Coding']
ors_jds = [5.58, 3.65, 3.51, 2.73, 1.87]
colors_jds = ['#2B6CB0', '#3182CE', '#4299E1', '#63B3ED', '#90CDF4']
ax1.barh(skills_jds, ors_jds, color=colors_jds, edgecolor='black', alpha=0.85)
ax1.set_xlabel("Junior Hike Odds Ratio per Unit Score Gain", fontweight='bold')
ax1.set_title("Junior Stage: Quantitative & Technical Skills Drive Hikes", pad=12)
ax1.set_xlim(0, 7)
for i, v in enumerate(ors_jds):
    ax1.text(v + 0.15, i, f"OR = {v:.2f}", va='center', fontweight='bold', color='#1A365D')

# Subplot 2: Senior Big Five Diagnostic Leakage ROC
traits = ['Conscientiousness', 'Openness', 'Neuroticism', 'Extraversion', 'Agreeableness']
coefs = [0.210, 0.215, 0.073, 0.064, 0.049]
colors_sds = ['#805AD5', '#9F7AEA', '#B794F4', '#D6BCFA', '#E9D8FD']
ax2.barh(traits, coefs, color=colors_sds, edgecolor='black', alpha=0.85)
ax2.set_xlabel("Senior Logistic Regression Coefficient (OCEAN)", fontweight='bold')
ax2.set_title(f"Senior Stage: Behavioral Traits & Leakage Audit\n(Random Forest AUC = {meta['sds_leakage_audit']['rf_auc']:.2f} -> Confirmed Instrument Leakage)", pad=12)
ax2.set_xlim(0, 0.3)
for i, v in enumerate(coefs):
    ax2.text(v + 0.008, i, f"beta = {v:.3f}", va='center', fontweight='bold', color='#44337A')

plt.tight_layout()
plt.savefig("figures/fig7_career_stage_divergence_leakage.png", bbox_inches='tight')
plt.close()

# -----------------------------------------------------------------
# FIGURE 8: Student Persona Investment Radars
# -----------------------------------------------------------------
print("[Fig 8] Generating Student Persona Investment Radar Charts...")

categories = ['Big Data', 'Maths-Stats', 'Core Coding', 'AI & ML', 'Storytelling']
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6), subplot_kw=dict(polar=True))

# Persona 1: Final Year Fresher
baseline_p1 = [1.5, 4.2, 2.2, 2.0, 2.0]
baseline_p1 += baseline_p1[:1]
optimized_p1 = [1.5, 5.0, 3.7, 2.2, 3.5]
optimized_p1 += optimized_p1[:1]

ax1.plot(angles, baseline_p1, linewidth=2, linestyle='solid', label='Current Baseline Profile', color='#E53E3E')
ax1.fill(angles, baseline_p1, '#FEB2B2', alpha=0.4)
ax1.plot(angles, optimized_p1, linewidth=2, linestyle='solid', label='6-Month Optimal Portfolio', color='#3182CE')
ax1.fill(angles, optimized_p1, '#90CDF4', alpha=0.4)
ax1.set_xticks(angles[:-1])
ax1.set_xticklabels(categories, fontweight='bold', fontsize=10)
ax1.set_ylim(0, 5)
ax1.set_title("Persona 1: Final-Year Fresher\n(+1.5 Coding, +1.5 Storytelling, +0.8 Stats)", y=1.1, fontweight='bold')
ax1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.22), frameon=True)

# Persona 2: Mid-Level Analyst
baseline_p2 = [3.0, 3.2, 4.3, 2.8, 2.1]
baseline_p2 += baseline_p2[:1]
optimized_p2 = [3.0, 4.7, 4.3, 3.1, 3.6]
optimized_p2 += optimized_p2[:1]

ax2.plot(angles, baseline_p2, linewidth=2, linestyle='solid', label='Current Baseline Profile', color='#E53E3E')
ax2.fill(angles, baseline_p2, '#FEB2B2', alpha=0.4)
ax2.plot(angles, optimized_p2, linewidth=2, linestyle='solid', label='6-Month Optimal Portfolio', color='#38A169')
ax2.fill(angles, optimized_p2, '#9AE6B4', alpha=0.4)
ax2.set_xticks(angles[:-1])
ax2.set_xticklabels(categories, fontweight='bold', fontsize=10)
ax2.set_ylim(0, 5)
ax2.set_title("Persona 2: Early-Career Analyst\n(+1.5 Storytelling, +1.5 Stats, Coding Maintained)", y=1.1, fontweight='bold')
ax2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.22), frameon=True)

plt.tight_layout()
plt.savefig("figures/fig8_student_decision_radar.png", bbox_inches='tight')
plt.close()

print("\nALL 8 PUBLICATION-QUALITY FIGURES GENERATED SUCCESSFULLY IN 'figures/'!")
