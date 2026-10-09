# SAS CU Hackathon
## Problem Statement Evaluation
**Skill market price vs. internal reward — a next-skill decision aid for students**

### Verdict
Yes, this is worth building on. It is more rigorous than what most of 200 teams will submit. Most will do EDA, a salary bar chart, and a random forest on the personality file. Linking all four files, showing uncertainty, and having the tool say "not enough evidence" are real differentiators.

But there are a few weak points the SAS jury will spot. Fix them before you build.

### Scored against the actual rubric
Round 2 counts for 70% of the final score.

| Section | Marks | How your PS does |
| :--- | :--- | :--- |
| **Problem definition** | 10 | Strong: clear user, clear decision, clear question |
| **Approach** | 15 | Strong, if you explain why each method fits each dataset's size |
| **Data exploration** | 25 | Strong. Salary is already pre-bucketed (6 bands, no missing); but `job_type` is 76% empty, JDS has null/duplicate IDs, and JDS/SDS have zero overlap. The "audit log with row counts" idea is excellent; these findings are its centrepiece |
| **Data analysis** | 30 | Strong but overloaded. Five objectives is risky in a hackathon. Also, salary is categorical — you need ordinal/multinomial methods, not OLS |
| **Results** | 10 | Depends on the bridge (see Problem 2) |
| **Implications** | 10 | Good for students. Add one line each for universities and employers |

### Problems to fix

1. **Your data claims don't match the brief**
   The Data Science Jobs file has exactly **1,602 rows** (company-level aggregates). The total `num_of_jobs` sums to **93,005** — if your PS quotes 93,005 postings, state explicitly that it is the aggregate job count, not the row count, or a judge will think you misread the data.
   More importantly, the Data Science Jobs file is aggregated at company level. Its columns are: `reference_no`, `company_name`, `job_title`, `min_experience`, `avg_salary`, `min_salary`, `max_salary`, `num_of_jobs`. It has **no skills column and no city column**. So your "skill premium within role family, controlling for experience and city" can only come from Analytics Jobs (15,841 rows), which has `key_skills`, `location`, `experience`, `salary` and `job_desig`. Use Data Science Jobs for company-level salary bands and title patterns. Rewrite Objective 1 so it is clear which file powers what.

2. **The bridge chart, your headline result, has only 5 points**
   The junior file has five broad skill areas. So "market price vs internal reward" is five dots, and the two axes are in different units (₹ premium vs. hike odds). A "clear verdict on whether the mismatch is real" cannot be a significance test with n = 5. Instead:
   * Put both axes on a common scale: standardised effects or ranks.
   * Report rank agreement (Spearman/Kendall) with a bootstrap interval.
   * Run a crosswalk sensitivity test: build 2–3 alternative skill mappings and show whether the verdict holds. That answers the obvious Q&A question, "isn't your mapping subjective?"

3. **Add a third axis: "listed"**
   Your opening sentence says skill lists show what employers list, not what pays. So measure that directly: how often each skill appears in postings. Then your story becomes Listed vs. Paid vs. Rewarded. That is a much stronger hook for Round 3, and it costs you almost nothing.

4. **The senior personality piece doesn't help your student user yet**
   A student cannot decide to "become more extraverted in six months," so as written it looks bolted on. Reframe it as career-stage contrast: juniors are rewarded on technical skills, seniors on how they work with people. Then link it to the "communication / storytelling" choice in your decision aid.
   The leakage check is a great idea. If the success label turns out to be a near-deterministic function of the scores, report that as a finding about the data rather than celebrating a 0.99 AUC.

5. **Salary in Analytics Jobs is pre-bucketed, not raw — plan accordingly**
   The salary column is **not** free-text or messy. It contains six clean categorical bands: `0to3`, `3to6`, `6to10`, `10to15`, `15to25`, `25to50` (in Lacs PA). There are **zero missing or "Not disclosed" values** — every row has a salary band. This is good news for exploration (no imputation needed), but it limits your modelling: you cannot compute a precise ₹ premium per skill. You can model salary-band membership (ordinal logistic or multinomial), or treat bands as ordered categories and report "skills that shift the distribution upward." Frame this limitation explicitly — it shows the judges you understand the data.

   **Other data quality issues worth surfacing in the 25-mark exploration section:**
   * The `job_type` column in Analytics Jobs is **empty for 75.8%** of rows (12,011 / 15,841). The remaining rows are all variants of "Analytics" / "analytics" / "ANALYTICS". This column adds almost no information.
   * JDS (Junior Skill Traits) has **171 rows but only 138 unique IDs**: 32 rows have `null` IDs, and 2 other IDs are duplicated. Decide whether to de-duplicate or keep all rows.
   * SDS (Senior Personality Traits) has **161 rows with 152 unique IDs**: 9 IDs appear twice.
   * JDS and SDS have **zero overlapping IDs** — they are entirely separate cohorts, not junior and senior employees from the same company. This matters for any career-stage comparison.
   * Only 1 row in Analytics Jobs has an empty `key_skills` field.
   Documenting these findings with counts is exactly what earns high marks in the exploration section.

6. **Internal reward comes from small, separate cohorts — not one unified sample**
   JDS has 138 unique juniors (after removing null-ID and duplicate rows); SDS has 152 unique seniors. The two files share **zero IDs**, so they are separate cohorts, not the same group at different career stages. Say this upfront. Frame the internal files as "two case studies of one employer's reward structure" rather than "what companies reward." Judges reward honesty about limits — and the zero-overlap fact strengthens your argument that junior and senior reward systems are structurally different.

7. **Use SAS more visibly**
   It is officially technology-agnostic, but the jury is SAS. "Python for models, SAS only for reporting" undersells it. At minimum:
   * Run the senior-success and junior-hike model comparisons as a SAS Model Studio pipeline (logistic vs. tree vs. forest).
   * Build the scorecard as a SAS Visual Analytics report. Visuals made in SAS Visual Analytics are explicitly allowed in the Round 3 deck.

8. **Small fixes**
   * Fill in "Data vintage: [state it]". The deck says 2024–25.
   * Your Naukri citation is accurate: the May 2026 JobSpeak reports fresher hiring and AI/ML roles growing +7% and +22% YoY respectively. Note that it is 2026 context for 2024–25 data, and keep it as context only, since external data transfer isn't allowed.
   * Define "abstain" concretely, for example: fewer than N postings for the skill, or the interval crosses zero.

### Cut scope so you finish
Rank the objectives so a time crunch does not kill you:
* **Must-have:** Analytics Jobs cleaning and audit log (flag `job_type` sparsity, JDS nulls, SDS duplicates), the skill-to-salary-band model (ordinal logistic), the junior hike model with bootstrap intervals, and the Listed/Paid/Rewarded chart.
* **Should-have:** senior model with permutation test and leakage check, framed as career-stage contrast.
* **Nice-to-have:** the full interactive scorecard. A one-page "Skill Investment Card" for 2–3 example student profiles is enough to show the idea.

### Make it land with students
The deliverable is a report and a deck, not an app, so the student benefit has to be visible on paper. End both with a concrete card, for example:
> "Final-year, decent at stats, weak at coding → next 6 months: coding (premium ₹X, interval Y–Z). Do not prioritise deep learning yet: insufficient evidence at 0–3 years."

One card like that will stick with the jury more than ten charts.

Also tighten the PS wording. It is dense with method terms. Lead with a one-line claim the jury can remember, for example:
> "The skills employers list most aren't the ones that get juniors paid more — here's the evidence, and how sure we are."

### Next steps (based on actual data review)
The data has been inspected. Here is what to do now:
1. **Build the crosswalk** mapping Analytics Jobs `key_skills` (free-text, comma-separated, ~15,840 rows) to the five JDS skill areas. Start with keyword lists, then validate with a sample.
2. **Handle JDS null/duplicate IDs** — decide on a de-duplication strategy (drop nulls? average duplicates?) and document it.
3. **Rethink the salary premium metric** — salary is categorical (six ordered bands), not continuous. Use ordinal logistic regression or proportional-odds modelling, not OLS.
4. **Draft the Listed / Paid / Rewarded triple chart** — "Listed" = skill frequency in Analytics Jobs; "Paid" = salary-band shift; "Rewarded" = JDS hike odds.
5. **Note experience is text ranges** (e.g., "5-10 yrs", "2-7 yrs") — parse min and max from each and decide whether to use midpoint or treat as a range variable.