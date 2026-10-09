# Results and Conclusions

## Our question

> **What makes a data scientist successful at each stage of their career?**

We looked at three stages, each with its own data:

| Stage | Data used | What we measured |
|---|---|---|
| 1. Getting hired | Analytics Jobs, DataScience Jobs | What decides the salary of a job |
| 2. Growing as a junior | JDS Skill Traits | Which skills lead to a high salary hike |
| 3. Succeeding as a senior | SDS Personality Traits | Which personality traits lead to high success |

---

## Stage 1: Getting hired (what decides pay?)

### Result 1: Experience is the biggest driver of pay
- **Each extra year of experience adds about 12% to salary**, even for the same job title.
- Pay rises from **₹6.4 L at 0 years** to **₹25.6 L at 10 years**, about 4 times as much.
- Of all the factors we tested, experience had the **strongest link** with salary band (Cramér's V = 0.40, a large effect).

> **In simple words:** the more years you have, the more you earn, and this holds in every role.

### Result 2: Job title matters, even at the same experience
With experience held the same, compared with a **Data Analyst**:

| Job title | Earns more by |
|---|---|
| Senior Data Scientist | **+197%** (about 3×) |
| Data Scientist | **+134%** (about 2.3×) |
| Senior Data Engineer | +134% |
| Data Engineer | +98% |
| Business Analyst | +52% |

- A "Senior" tag alone adds **14–36%** at the same experience.
- Title, experience and company type together explain **58% of salary differences** (regression R² = 0.58).

> **In simple words:** two people with the same experience can earn very different amounts depending on their job title. Data Scientist pays far more than Data Analyst.

### Result 3: Specific technical skills pay more; generic keywords do not
We tested 116 common skills. **42 had a real (statistically significant) link with pay.**

| Skills that increase the chance of a ₹15 L+ job (2–3× more likely) | Skills linked to low-paying jobs |
|---|---|
| Credit risk, statistical modelling, algorithms, C++, R, NLP, deep learning, product management | Outsourcing, BPO, Google AdWords, SEO, and generic words like "communication skills", "analytical", "coding" |

> **In simple words:** jobs that ask for *specific* technical skills pay well. Jobs that only list *general* words are usually entry-level or support roles.

### Result 4: Most jobs come from companies that pay less
- **67% of all job openings** come from large IT-services firms (TCS, Accenture, Cognizant and others).
- These firms pay **about 11% less** for the same role and experience.
- The best-paying firms (Adobe, Walmart, PayPal, AB InBev) offer only **about 6% of openings**.

> **In simple words:** jobs are easy to find but pay less. High-paying jobs exist but are few and competitive.

### Result 5: City matters much less than experience
- Bengaluru has the most jobs (4,141 postings) and the highest share of ₹15 L+ jobs (30%).
- But city has only a **small effect** on pay (Cramér's V = 0.09), about a quarter of the effect of experience.

> **In simple words:** *where* you work matters much less than *how experienced* you are.

### Result 6: Salary band can be predicted reasonably well
- Our model predicts a job's salary band **within one band 83% of the time**, compared with 62% for guessing.
- The most important input is **experience**. Skills come second.

---

## Stage 2: Growing as a junior (which skills get a high hike?)

### Result 7: Maths/stats and storytelling matter most
How much each +1 point of skill multiplies the chance of a high hike:

| Skill | Effect |
|---|---|
| **Maths & statistics** | **×6.2** (strongest) |
| **Dashboard & storytelling** | **×3.9** |
| AI & ML | ×3.5 |
| Big data | ×2.7 (only helps once the other skills are strong) |
| Coding | ×1.8 (not significant) |

- On its own, **big-data skill makes no difference**. It only helps when combined with strong maths and storytelling.
- Raising **maths/stats by just half a point** gives the biggest increase in the chance of a hike (+9 percentage points).

### Result 8: Hikes are very predictable
- Our model predicts high or low hike with **about 82–86% accuracy (AUC about 0.90)**, compared with 53% for guessing. The range comes from repeating the test in different ways.
- **A simple rule found by the model:**
  - Storytelling above 4.15 **and** maths above 3.55 → mostly a **high hike**
  - Storytelling 4.15 or below → **38 of 41 people got a low hike**

> **In simple words:** juniors who are good at numbers *and* at explaining results get rewarded. Knowing tools alone is not enough.

---

## Stage 3: Succeeding as a senior (which personality traits matter?)

### Result 9: Openness and conscientiousness define success
How much each +10 points multiplies the chance of high success:

| Trait | What it means | Effect |
|---|---|---|
| **Openness** | Curious, creative, open to new ideas | **×14.7** |
| **Conscientiousness** | Organised, responsible, hard-working | **×12.0** |
| Extraversion | Outgoing, social | ×3.1 |
| Agreeableness | Kind, cooperative | ×2.2 (borderline) |
| Neuroticism | Anxious, stressed | **No difference on its own** |

### Result 10: Success can be predicted very accurately
- Our model predicts senior success with **95% accuracy (AUC 0.99)**.
- **Simple rule:** if openness is 38.5 or below, then **0 of 52 people** were successful.

### Result 11: Four personality types
We grouped seniors by personality **without telling the computer who was successful**. The groups still showed very different success rates:

| Personality type | People | Success rate |
|---|---|---|
| **Conscientious & open** | 88 | **89%** |
| Anxious, less agreeable | 22 | 32% |
| Agreeable but not open | 23 | **0%** |
| Low on all traits | 28 | **0%** |

> **In simple words:** seniors who are curious *and* responsible succeed. Being nice alone is not enough.

---

## Final conclusion

> **What drives success changes as a data scientist's career grows:**
>
> 1. **Getting hired:** experience, job title and specialised skills decide pay.
> 2. **As a junior:** maths/statistics and storytelling decide who gets rewarded.
> 3. **As a senior:** curiosity (openness) and responsibility (conscientiousness) decide who succeeds.
>
> **The journey moves from *technical depth* to *communication* to *personality*.**

---

## Limits of this study (be honest)

- Salary in Analytics Jobs is given in **bands** (such as 10–15 L), not exact numbers.
- Some job text was **cut off**, so not every skill was visible.
- The JDS and SDS data are **small** (139 and 161 people) and come from **one company**.
- The results show **links (association), not proof of cause**.
- The four datasets are about different people, so we linked them **by career stage**, not person by person.
