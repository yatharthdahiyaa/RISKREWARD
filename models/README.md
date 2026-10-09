# The Data Scientist Career Path: Pay, Skills and Personality

**SAS CU Hackathon: data exploration and analysis**

This folder analyses four datasets from the SAS hackathon brief to answer one question:

> **What decides a data scientist's success at each career stage: getting hired (market pay), growing as a junior (technical skills), and succeeding as a senior (personality)?**

| Stage | Dataset | Question |
|---|---|---|
| Entering the market | `Analytics Jobs.csv`, `DataScience Jobs.csv` | What decides how much a data job pays: role, experience, city, company or skills? |
| Growing as a junior | `JDS Skill Traits.xlsx` | Which technical skills earn a high salary hike? |
| Succeeding as a senior | `SDS Personality Traits.xlsx` | Which Big-Five traits separate high-success seniors? |

## Files and run order

| # | File | Purpose |
|---|---|---|
| 1 | [data_exploration.ipynb](data_exploration.ipynb) | Profiling, data-quality checks, cleaning, descriptive charts. **Writes `cleaned/*.csv`.** |
| 2 | [data_analysis.ipynb](data_analysis.ipynb) | Hypothesis tests, regression, machine-learning models, clustering, career roadmap. **Reads `cleaned/*.csv`.** |
| – | `cleaned/` | Cleaned tables. These are plain CSV, so they can be uploaded to SAS Viya for Learners (VFL). |

```bash
pip install pandas numpy matplotlib openpyxl scipy statsmodels scikit-learn jupyter
# run data_exploration.ipynb first, then data_analysis.ipynb
```

Both notebooks are saved with every output and chart rendered, so you can read them without running them.

These notebooks map to the Round-2 rubric as follows:

| Rubric heading | Notebook section |
|---|---|
| Problem definition (10) | analysis intro |
| Approach (15) | both intros + this README |
| **Data exploration (25)** | `data_exploration.ipynb` (all sections) |
| **Data analysis (30)** | `data_analysis.ipynb` §1–§4 |
| Results and conclusions (10) | analysis §5 + interpretation cells |
| Implications (10) | analysis §5 stakeholder table |

---

## 1. The datasets

| File | Raw rows × cols | Unit of a row | Target / key measure |
|---|---|---|---|
| `Analytics Jobs.csv` | 15,841 × 8 | One job posting | `salary` band (6 classes, ₹ lakhs) |
| `DataScience Jobs.csv` | 1,602 × 8 | One company + job title | `avg_salary` (₹ lakhs, e.g. `"12.8L"`) |
| `JDS Skill Traits.xlsx` | 139 × 7 | One junior data scientist | `salary_hike_high_or_low` (0/1) |
| `SDS Personality Traits.xlsx` | 161 × 7 | One senior data scientist | `success_ classification_ high_low` (0/1) |

Two of the four files are Excel, not CSV. Column meanings are listed in the hackathon's *Data Description Doc.pdf*.

---

## 2. `data_exploration.ipynb`: what each output means

### Section 1: Load and overview
| Output | Meaning |
|---|---|
| Overview table | Only Analytics Jobs has missing values. No file has exact duplicate *rows*, but see §2.2. |
| Missing per column | In Analytics Jobs, `job_type` is 75.8% missing and `job_description` 22.1%. The other files are complete. |
| Column-name problems | SDS has `" extraversion"` (leading space) and `"success_ classification_ high_low"`. These are renamed to `extraversion` and `success_high`, and the JDS columns to `hike_high` and `maths_stats_skills`. |

### Section 2: Analytics Jobs
| Step | Output | Meaning |
|---|---|---|
| 2.1 | `head()`, `describe()` | 10,097 unique titles, 1,355 location strings and 128 experience formats. Very messy categorical data. |
| 2.2 Cleaning | Duplicates removed | **1,001 postings (6%) are identical except for `s_no`** and are dropped, leaving 14,840 rows. They had inflated the average salary from 11.8 L to 12.3 L. |
| | `job_type` before/after | 5 spellings of "Analytics" are merged. Only 22% of rows are tagged, so the column is unreliable. |
| | Truncation report | 77% of descriptions and 87% of skill lists are cut off at about 100 characters (`...`). |
| | Location cleaning | Sub-areas (`Bengaluru(Whitefield)`), `+1` suffixes and variants (`Bangalore`, `Gurugram`, `Navi Mumbai`, `New Delhi`) are mapped to one city. **927 raw city tokens become 467 cities.** 13% of postings list several cities. |
| | Flags | 113 fresher postings (0-0 yrs, kept), 295 **junk postings** (data entry, part-time, walk-in), and 10 **experience/salary conflicts** (10+ years but pay under 3 L, likely errors and excluded from modelling). |
| 2.3 | **Chart: postings per band** | The bands are reasonably balanced: 7% (25–50 L) to 24% (10–15 L). That makes the band a good classification target. |
| 2.4 | **Chart: experience vs band** | Median minimum experience rises from 1 year (0–3 L) to 10 years (25–50 L), r = 0.65. |
| 2.5 | **Chart: top cities** | Bengaluru 4,141, Mumbai 2,809, Gurgaon 2,041, Delhi NCR 1,702. |
| | **Chart: pay by city** | Bengaluru (13.0 L), Mumbai (12.4) and Delhi NCR (12.3) pay the most. Kolkata (9.3) and Ahmedabad (8.5) pay the least. |
| 2.6 | **Chart: top 20 skills** | The most common are analytics, SQL, Python, finance, Java, business analysis, ML, R and SAS. |
| | **Charts: highest- and lowest-paying skills** | Highest: algorithms (17.0 L), product management, software development, data science, C++, R, Spark, ML. Lowest: communication skills (5.0 L), SEO, outsourcing, SEM. |
| 2.7 | Role-group table and chart | Data Scientist/ML pays 16.4 L and Data Engineer 14.7 L. Data/Business Analyst (9.8 L) and Marketing/SEO (10.3 L) pay the least. 43% of titles are "Other", so the file is not only data roles. |

### Section 3: DataScience Jobs
| Output | Meaning |
|---|---|
| Parsing check | All salaries parse and min ≤ avg ≤ max in 100% of rows, so the file is internally consistent. |
| `describe()` | Median average salary is 11.9 L (range 1.4–82 L). `num_of_jobs` is very skewed (median 22, max 4,200). |
| **Chart: salary by title** | Data Architect 24.3 L > Senior DS 21.2 > Senior DE 17.6 > Senior BA 13.0 ≈ DS 12.8 > … > Data Analyst 5.0. |
| **Chart: seniority premium** | The raw Senior uplift is +57% to +72%. Part of it is extra experience (see analysis §1.2). |
| **Chart: experience vs salary** | 6.4 L at 0 years, 15.2 L at 4 years, 25.6 L at 10 years (r = 0.59). |
| **Charts: top hirers / payers** | TCS, Accenture and Cognizant hire the most. Adobe, Walmart and AB InBev pay the most. The 8 biggest hirers pay 9.8 L against 12.0 L elsewhere. |
| **Chart: salary histogram + outlier threshold** | 39 IQR outliers, almost all Senior DS, Data Architect or Senior DE at product firms. They are genuine, so they are **kept**. Salary is right-skewed (skew 1.74), and the log scale fixes this (−0.45), so the analysis uses log-salary. |

### Sections 4–5: JDS and SDS
| Output | Meaning |
|---|---|
| Range / duplicate-ID checks | No out-of-range values. **JDS has 2 and SDS has 9 duplicate IDs, but the rows differ (sometimes even the outcome), so these are ID collisions, not repeats.** All rows are kept and a unique `row_key` is added. |
| IQR outliers | JDS `ai_and_ml` has 18 "outliers", because 49% of people score 5.0 and the few low scorers get flagged. SDS agreeableness has 5. All are real values and are kept. |
| Group-mean tables and charts | High-hike juniors score higher on every skill, with the largest gap on storytelling (+1.03). High-success seniors score much higher on conscientiousness (+18) and openness (+15). Neuroticism shows no difference. |
| Simple rules | Total skill score ≥ 21.2 classifies 87% of juniors correctly. Conscientiousness + openness ≥ 85 classifies 92% of seniors correctly. |

### Section 6: Cross-check
Both job files rank roles the same way (Data Scientist highest, Data Analyst lowest). Analytics Jobs is about 1–3 L higher because band midpoints overstate pay.

### Section 7: Saved files
`cleaned/analytics_jobs_clean.csv` (14,840 rows), `ds_jobs_clean.csv` (1,602), `jds_clean.csv` (139), `sds_clean.csv` (161).

---

## 3. `data_analysis.ipynb`: methods, outputs and results

### §1 Market pay (DataScience Jobs)
| Output | Method | Result |
|---|---|---|
| Kruskal-Wallis | Non-parametric test across the 10 titles | H = 833, p < 1e-170, ε² = 0.52, so **title explains a large share of salary differences** |
| Spearman (overall and within title) | Rank correlation | rho = 0.63 overall and 0.29–0.59 **inside every title**, so experience matters even within one role |
| **OLS on log-salary + forest chart** | `log(salary) ~ experience + title + big_hirer`, robust SEs | **R² = 0.58.** At the same experience, Data Scientist is +134% vs Data Analyst, and Senior DS +197%. **Each year adds +12%.** **The top-10 volume hirers pay 11% less.** |
| **Company quadrant scatter** + table | Median split on openings × median pay | "High volume, low pay" firms provide **67% of all openings** (median 9.4 L). "Selective, high pay" firms pay 16.6 L but offer only 6% of openings. |

### §2 Roles, cities and skills (Analytics Jobs)
| Output | Method | Result |
|---|---|---|
| **Cramér's V table and chart** | Chi-square test of independence | Experience has a **large** effect (V = 0.40). City and role group are significant but **small** (V ≈ 0.09). |
| **Share 15 L+ by role / city** | Rates | Data Scientist/ML (42%) and Data Engineer (36%) are most often in the 15 L+ bands. Data/Business Analyst is lowest (18%). Bengaluru leads the cities (30%), and Noida and Chennai trail (about 20%). |
| Skill premium table | 2×2 odds ratios with Bonferroni correction, 116 skills | **42 skills significant.** Premiums of 2–3× for credit risk, statistical modelling, algorithms, C++, R, NLP and deep learning. Penalties of 0.06–0.2× for outsourcing, BPO, AdWords and generic keywords like "communication skills". |
| **Demand vs premium scatter** | Visual | Python, R and finance combine high demand with a premium. Generic keywords sit at the bottom. |
| **Model comparison chart** | 5-fold CV, 171 features | Exact band accuracy is **41%** against a 24% baseline. **Within-one-band accuracy is 83%** against 62%. LR, RF and GBM perform about the same. |
| **Confusion matrix** | Hold-out 20% | Most errors fall in an adjacent band. |
| **Permutation importance** | Shuffle-one-feature test | Experience dominates. Skills such as analytics, ML, product management and NLP refine the prediction. |

### §3 Junior skills (JDS)
| Output | Method | Result |
|---|---|---|
| Mann-Whitney table | Rank test + rank-biserial *r*, Bonferroni | Storytelling (r = 0.59), maths/stats (0.55), coding (0.49) and AI/ML (0.36) are significant. **Big data is not significant on its own.** |
| **Odds-ratio forest plot** | Multivariable logistic regression | Per +1 point: **maths/stats ×6.2**, storytelling ×3.9, AI/ML ×3.5, big data ×2.7, coding ×1.8 (n.s.). Pseudo-R² = 0.50. Big data only matters once the other skills are held constant (a suppression effect). |
| Model comparison | 10 × 5-fold CV | **Logistic Regression: 86% accuracy, AUC 0.90** (baseline 53%). |
| Decision-tree rules | Depth-3 tree | **Storytelling > 4.15 and maths > 3.55** → mostly high hike. Storytelling ≤ 4.15 → 38 of 41 people got a low hike. |
| **What-if chart** | +0.5 points in one skill for an average low-hike junior | The largest gain comes from maths/stats, then storytelling and AI/ML. This is the prescriptive training priority. |

### §4 Senior personality (SDS)
| Output | Method | Result |
|---|---|---|
| Mann-Whitney table | Rank test | Openness (r = 0.77) and conscientiousness (0.76) are very large, extraversion 0.57, agreeableness 0.30. **Neuroticism shows no difference on its own.** |
| **Odds-ratio forest plot** | Logistic regression, per +10 points | **Openness ×14.7, conscientiousness ×12.0.** Neuroticism turns positive only when controlled for the other traits (suppression, wide CIs). Do not over-interpret it. |
| Model comparison | 10 × 5-fold CV | **Random Forest: 95% accuracy, AUC 0.99.** Logistic Regression: 93%. |
| Decision-tree rules | Depth-3 tree | Openness > 38.5 → conscientiousness > 36.5 → agreeableness > 38.5 → 83 of 88 people are high-success. Openness ≤ 38.5 → 0 of 52. |
| **Persona heatmap and success-rate chart** | K-Means (k = 4, silhouette 0.33), without the success label | **Conscientious & open (n = 88): 89% success**. High neuroticism/low agreeableness: 32%. High agreeableness/low openness: 0%. Low on all traits: 0%. |

### §5 Synthesis
A roadmap table (stage → what matters → evidence → action) and a table of stakeholder implications.

---

## 4. Key insights

**Market**
1. **Experience is the single strongest pay driver.** Each extra year adds about +12% at the same title, and experience has a large association with salary band (V = 0.40).
2. **Title matters even at the same experience.** Data Scientist earns about 2.3× a Data Analyst, and Senior Data Scientist about 3×.
3. **Specific technical skills earn a premium; generic keywords do not.** Algorithms, statistical modelling, NLP, deep learning, C++, R and credit risk give 2–3× the odds of a 15 L+ posting. "Communication skills", outsourcing and SEO postings are mostly low-pay.
4. **Most jobs come from firms that pay less.** Two-thirds of openings are at high-volume, below-median-pay firms, which pay about 11% less like-for-like.
5. **City matters much less than experience** (V = 0.09). Bengaluru has the most postings and the highest average pay.

**Junior → Senior**
6. **For juniors, maths/stats and storytelling come first.** They are the strongest drivers of a high hike. Big-data skill only helps on top of them.
7. **For seniors, openness and conscientiousness define success.** The "conscientious & open" persona succeeds 89% of the time. Agreeableness alone is not enough (0% success when openness is low).
8. **Both outcomes are highly predictable** (AUC 0.90 for juniors, 0.99 for seniors). Simple, transparent rules can support HR decisions.

**Data quality (part of the story)**
9. We removed 1,001 duplicate postings and reduced 927 city tokens to 467. Duplicate IDs in JDS and SDS turned out to be different people. Salary outliers are genuine senior roles, so we used log-salary instead of dropping them.

### Limitations
- The Analytics salary is a band, its text is truncated, and the file is not limited to data roles.
- DataScience Jobs reports company-level averages, not individuals.
- JDS and SDS are small single-company samples. They show association, not causation.
- The four datasets cannot be joined at person level. The roadmap links them by career stage.

## 5. Possible extensions
- Build the same reports and models in **SAS Visual Analytics / Model Studio** from `cleaned/*.csv`.
- Use ordinal regression for the salary band. Use TF-IDF on job titles for better role classification.
- Build a dashboard: choose a role, city and experience, and see the expected band, the premium skills to learn, and the hike or success drivers.
