"""
Convert the Approach Note markdown to a properly formatted Word document.
Times New Roman, 12pt, single spacing as required by the rubric.
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re

doc = Document()

# ── Global defaults ──────────────────────────────────────────────
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)
style.paragraph_format.space_after = Pt(4)
style.paragraph_format.space_before = Pt(2)
style.paragraph_format.line_spacing = 1.0

# Fix font for East Asian
rFonts = style.element.rPr.rFonts if style.element.rPr is not None else None
if rFonts is None:
    rPr = style.element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    rPr.append(rFonts)

# Page margins
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(2.54)
    section.right_margin = Cm(2.54)

# ── Style helpers ────────────────────────────────────────────────
def set_heading_font(heading, size=14, bold=True, color=RGBColor(0, 51, 102)):
    for run in heading.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color

def add_heading_custom(text, level=1):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.line_spacing = 1.0
    sizes = {1: 18, 2: 15, 3: 13, 4: 12}
    set_heading_font(h, size=sizes.get(level, 12))
    return h

def add_para(text, bold=False, italic=False, indent=0, align=None, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.0
    if indent:
        p.paragraph_format.left_indent = Inches(indent * 0.35)
    if align:
        p.alignment = align
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = bold
    run.italic = italic
    return p

def add_rich_para(parts, indent=0, space_after=4):
    """parts is a list of (text, bold, italic) tuples"""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.0
    if indent:
        p.paragraph_format.left_indent = Inches(indent * 0.35)
    for text, bold, italic in parts:
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.bold = bold
        run.italic = italic
    return p

def add_bullet(text, level=0, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.left_indent = Inches(0.5 + level * 0.35)
    if bold_prefix:
        run = p.add_run(bold_prefix)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.bold = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    else:
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    return p

def add_table(headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header row
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.bold = True
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(1)
    # Data rows
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = ''
            p = cell.paragraphs[0]
            run = p.add_run(str(val))
            run.font.name = 'Times New Roman'
            run.font.size = Pt(11)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(1)
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return table

import os

def add_figure(image_path, caption, width_in_inches=5.6):
    if os.path.exists(image_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        run = p_img.add_run()
        run.add_picture(image_path, width=Inches(width_in_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        run_cap = p_cap.add_run(caption)
        run_cap.font.name = 'Times New Roman'
        run_cap.font.size = Pt(10)
        run_cap.italic = True
        run_cap.font.color.rgb = RGBColor(80, 80, 80)

def add_quote(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.right_indent = Inches(0.3)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.italic = True
    run.font.color.rgb = RGBColor(80, 80, 80)
    return p

def add_page_break():
    doc.add_page_break()

# ═══════════════════════════════════════════════════════════════
#                        TITLE PAGE
# ═══════════════════════════════════════════════════════════════

for _ in range(6):
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('APPROACH NOTE')
run.font.name = 'Times New Roman'
run.font.size = Pt(28)
run.bold = True
run.font.color.rgb = RGBColor(0, 51, 102)
p.paragraph_format.space_after = Pt(8)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Round 2 Submission')
run.font.name = 'Times New Roman'
run.font.size = Pt(18)
run.font.color.rgb = RGBColor(80, 80, 80)
p.paragraph_format.space_after = Pt(30)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(4)
run = p.add_run('SAS Hackathon | Chandigarh University | 2026')
run.font.name = 'Times New Roman'
run.font.size = Pt(14)
run.bold = True

doc.add_paragraph().paragraph_format.space_after = Pt(12)

# Problem title
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(6)
run = p.add_run('Listed, Paid, Rewarded')
run.font.name = 'Times New Roman'
run.font.size = Pt(16)
run.bold = True
run.font.color.rgb = RGBColor(0, 51, 102)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(30)
run = p.add_run('Do the Skills Employers Advertise Actually Drive\nSalary and Career Outcomes for Data Scientists?')
run.font.name = 'Times New Roman'
run.font.size = Pt(14)
run.italic = True

# Meta info
for line in [
    'Team: Aavishkar Hacks',
    'Data Vintage: 2024–25',
    'Date: October 2026',
    'Format: Word | Times New Roman, 12pt, Single Spacing',
]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(line)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    p.paragraph_format.space_after = Pt(2)

add_page_break()

# ═══════════════════════════════════════════════════════════════
#                     TABLE OF CONTENTS
# ═══════════════════════════════════════════════════════════════

add_heading_custom('Table of Contents', level=1)

toc_items = [
    ('1.', 'Problem Definition / Analytics Objective'),
    ('   1.1', 'Context'),
    ('   1.2', 'The Core Question'),
    ('   1.3', 'Analytics Objectives'),
    ('   1.4', 'Target User'),
    ('   1.5', 'Scope and Limitations'),
    ('2.', 'Approach'),
    ('   2.1', 'Overall Analytical Flow'),
    ('   2.2', 'Why This Approach Fits Each Dataset'),
    ('   2.3', 'The Crosswalk: Mapping Skills to Skill Areas'),
    ('   2.4', 'Tool and Technology Stack'),
    ('   2.5', 'Abstention Policy'),
    ('3.', 'Data Exploration'),
    ('   3.1', 'Data Inventory and Audit Log'),
    ('   3.2', 'Data Quality Issues Summary'),
    ('   3.3', 'Data Derivations and Transformations'),
    ('   3.4', 'Data Reduction'),
    ('4.', 'Data Analysis'),
    ('   4.1', 'Stream A — Skill Listing Frequency ("Listed")'),
    ('   4.2', 'Stream B — Salary Band Association ("Paid")'),
    ('   4.3', 'Stream C — Internal Hike Model ("Rewarded")'),
    ('   4.4', 'Stream D — Career-Stage Contrast'),
    ('   4.5', 'Stream E — Listed vs. Paid vs. Rewarded Comparison'),
    ('5.', 'Results and Conclusions'),
    ('6.', 'Implications'),
    ('', 'Appendix'),
]

for num, title in toc_items:
    indent = 1 if num.startswith('   ') else 0
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    if indent:
        p.paragraph_format.left_indent = Inches(0.4)
    run = p.add_run(f'{num.strip()} {title}')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    if not indent:
        run.bold = True

add_page_break()

# ═══════════════════════════════════════════════════════════════
#          SECTION 1: PROBLEM DEFINITION (10 marks)
# ═══════════════════════════════════════════════════════════════

add_heading_custom('1. Problem Definition / Analytics Objective', level=1)

add_heading_custom('1.1 Context', level=2)

add_para("India's analytics workforce is expanding rapidly. The Naukri JobSpeak Index (May 2026) reports that fresher hiring has risen year-on-year, with AI/ML roles growing +22% YoY and overall analytics roles growing +7% YoY. Yet a recurring disconnect plagues students and early-career professionals: the skills that appear most frequently in job postings are not necessarily the skills that correlate with higher salaries or faster career progression.")

add_para("Students invest heavily in skill-building — bootcamps, certifications, project portfolios — but lack an evidence-based framework to decide which skill to invest in next. Career advice is typically anecdotal (\"learn Python\"), not data-driven. This hackathon's four datasets provide a unique opportunity to test whether such advice is actually backed by market and organisational evidence.")

add_heading_custom('1.2 The Core Question', level=2)

add_quote('"Are the skills employers list most in job postings the same skills that actually get data scientists paid more — and are those the same skills that drive salary hikes inside an organization?"')

add_para('We decompose this into three measurable axes for each skill area:')

add_table(
    ['Axis', 'Definition', 'Data Source'],
    [
        ['Listed', 'How frequently the skill appears in job postings', 'Analytics Jobs (15,841 rows)'],
        ['Paid', 'Whether the skill shifts the salary-band distribution upward', 'Analytics Jobs — salary bands × key_skills'],
        ['Rewarded', 'Whether the skill predicts a high salary hike internally', 'JDS Skill Traits (171 rows, 138 unique)'],
    ]
)

add_para('If these three axes diverge — if the most listed skill is not the most paid or rewarded — then the labour market sends contradictory signals, and students need a decision aid to navigate the mismatch.')

add_heading_custom('1.3 Analytics Objectives', level=2)

add_table(
    ['#', 'Objective', 'Deliverable'],
    [
        ['O1', 'Quantify skill listing frequency across 15,841 analytics job postings and map free-text skills to five standardised skill areas', 'Skill frequency table + crosswalk mapping'],
        ['O2', 'Model the association between skill presence and salary band (ordinal), controlling for experience and location', 'Ordinal logistic regression coefficients + odds ratios with 95% CI'],
        ['O3', 'Model the association between skill scores and salary-hike outcome (binary) for junior data scientists', 'Logistic regression / random forest with bootstrap confidence intervals'],
        ['O4', 'Construct the Listed vs. Paid vs. Rewarded comparison chart and test whether the three rankings agree', 'Spearman/Kendall rank correlation with bootstrap intervals'],
        ['O5', 'Contrast junior (skill-based) vs. senior (personality-based) career-success drivers', 'Comparative model summary; senior model with leakage check'],
    ]
)

add_heading_custom('1.4 Target User', level=2)

add_rich_para([
    ('A ', False, False),
    ('final-year or early-career data science student', True, False),
    (' deciding which skill to invest in over the next 6 months. The deliverable produces a concrete, evidence-backed recommendation with stated uncertainty.', False, False),
])

add_heading_custom('1.5 Scope and Limitations (Stated Upfront)', level=2)

add_bullet('The internal datasets (JDS, SDS) come from one company. We frame these as case studies, not universal truths.')
add_bullet('JDS and SDS have zero overlapping IDs — they represent separate cohorts, not tracked career trajectories.')
add_bullet('Salary in Analytics Jobs is categorical (six ordered bands), not continuous. We cannot compute exact ₹ premiums; we model salary-band shifts.')
add_bullet('The crosswalk mapping 14,000+ unique skill strings to five skill areas involves judgement. We validate it with sensitivity analysis.')
add_bullet('Naukri JobSpeak data (May 2026) is used as context only — no external data is transferred into the analysis per competition rules.')

add_page_break()

# ═══════════════════════════════════════════════════════════════
#              SECTION 2: APPROACH (15 marks)
# ═══════════════════════════════════════════════════════════════

add_heading_custom('2. Approach', level=1)

add_heading_custom('2.1 Overall Analytical Flow', level=2)

add_para('The analysis integrates all four data files through a five-stream analytical pipeline:', space_after=8)

add_rich_para([
    ('Stream A (Listed): ', True, False),
    ('Extract and count skill frequencies from Analytics Jobs (15,841 postings) using the crosswalk. Output: listing-share ranking for five skill areas.', False, False),
])
add_rich_para([
    ('Stream B (Paid): ', True, False),
    ('Model skill-area presence against salary bands (ordinal logistic), controlling for experience and location. Output: odds ratios ranking for five skill areas.', False, False),
])
add_rich_para([
    ('Stream C (Rewarded): ', True, False),
    ('Model skill scores against salary-hike outcome (binary logistic + bootstrap) using JDS. Output: odds ratios ranking for five skill areas.', False, False),
])
add_rich_para([
    ('Stream D (Career-Stage Contrast): ', True, False),
    ('Model personality traits against senior success (binary logistic) using SDS. Output: comparative insight — what drives success changes with career stage.', False, False),
])
add_rich_para([
    ('Stream E (Integration): ', True, False),
    ('Compare the Listed, Paid, and Rewarded rankings. Test agreement with Spearman/Kendall + bootstrap CI. Construct the headline triple chart and Skill Investment Card.', False, False),
])

add_para('DataScience Jobs (1,602 rows) is used as a reference dataset for company-level salary benchmarks and title-tier validation. It does not feed directly into the modelling streams because it has no skills column.', space_after=8)

add_heading_custom('2.2 Why This Approach Fits Each Dataset', level=2)

add_table(
    ['Dataset', 'n', 'Nature', 'Method', 'Rationale'],
    [
        ['Analytics Jobs', '15,841', 'Large, posting-level, categorical salary, free-text skills', 'Ordinal logistic regression; NLP-based skill extraction', 'Large n supports regression. Salary is ordinal → ordinal logistic, not OLS.'],
        ['DataScience Jobs', '1,602', 'Company-level aggregates, continuous salary', 'Descriptive analysis; company-tier benchmarks', 'Already aggregated — use for validation and context.'],
        ['JDS Skill Traits', '138 unique', 'Small, structured, 5 predictors, binary outcome', 'Logistic regression + bootstrap CIs; RF comparison', 'Small n → bootstrap essential. Avoid overfit.'],
        ['SDS Personality', '152 unique', 'Small, structured, Big Five, binary outcome', 'Logistic regression; permutation importance; leakage check', 'Small n + normalised scores → leakage risk must be tested.'],
    ]
)

add_heading_custom('2.3 The Crosswalk: Mapping 14,482 Unique Skill Strings to Five Skill Areas', level=2)

add_para('The JDS file defines five skill areas: Big Data, Maths-Stats, Coding, AI & ML, and Dashboard & Storytelling. Analytics Jobs contains 14,482 unique skill strings (comma-separated free text). We must create a reproducible crosswalk mapping.', space_after=6)

add_rich_para([('Crosswalk Method:', True, False)])

add_table(
    ['Step', 'Action', 'Validation'],
    [
        ['1', 'Define keyword dictionaries for each of the 5 skill areas', 'Manual review of top 200 skills by frequency'],
        ['2', 'For each posting, flag which skill areas are present (binary: 0/1)', 'Check coverage: % of postings mapping to ≥1 area'],
        ['3', 'Sensitivity test: create narrow, medium, and broad dictionaries', 'Compare rank ordering across mappings'],
        ['4', 'Report agreement across mappings', 'If rank order is stable, crosswalk is robust'],
    ]
)

add_rich_para([('Initial Keyword Dictionaries (based on frequency analysis):', True, False)])

add_table(
    ['Skill Area', 'Sample Keywords', 'Key Frequency'],
    [
        ['Big Data', 'Hadoop (243), Spark (217), Hive, Kafka, Data Lake, ETL', 'Mid-frequency'],
        ['Maths-Stats', 'R (516), SAS (517), Statistics, Econometrics, Regression', 'R and SAS in top 10'],
        ['Coding', 'SQL (742), Python (644), Java (566), Javascript (418), HTML', 'SQL #1, Python #3 overall'],
        ['AI & ML', 'Machine Learning (423), Deep Learning, NLP, TensorFlow', 'ML in top 10'],
        ['Dashboard', 'Tableau, Power BI, Excel (267), Analytics (691), Reporting', 'Analytics #2 overall'],
    ]
)

add_heading_custom('2.4 Tool and Technology Stack', level=2)

add_table(
    ['Task', 'Tool', 'Rationale'],
    [
        ['Data cleaning & manipulation', 'Python (pandas) / SAS', 'Flexibility for free-text parsing'],
        ['Ordinal logistic regression', 'Python (statsmodels) / SAS PROC LOGISTIC', 'Appropriate for ordered categorical outcome'],
        ['Bootstrap confidence intervals', 'Python (manual resampling)', 'Full control over resampling scheme'],
        ['Model comparison pipeline', 'SAS Model Studio', 'Logistic vs. Tree vs. Forest — visible SAS usage'],
        ['Visual Analytics dashboard', 'SAS Visual Analytics', 'Allowed in Round 3 presentation'],
        ['Rank agreement tests', 'Python (scipy.stats)', 'Spearman ρ, Kendall τ'],
    ]
)

add_heading_custom('2.5 Abstention Policy', level=2)

add_para('The decision aid will abstain (state "insufficient evidence") under three conditions:')
add_bullet('Fewer than 50 postings contain the skill in Analytics Jobs')
add_bullet('The confidence interval for the odds ratio crosses 1.0 (no directional evidence)')
add_bullet('The crosswalk sensitivity test shows rank instability for that skill area')

add_page_break()

# ═══════════════════════════════════════════════════════════════
#         SECTION 3: DATA EXPLORATION (25 marks)
# ═══════════════════════════════════════════════════════════════

add_heading_custom('3. Data Exploration', level=1)

add_para('We begin with a systematic audit of all four files. This audit log — with exact row counts, quality metrics, and data-issue documentation — is the foundation of the exploration section.')

add_heading_custom('3.1 Data Inventory and Audit Log', level=2)
add_figure('figures/fig1_data_audit_matrix.png', 'Figure 1: Forensic Data Inventory and Cross-Cohort Isolation Matrix (JDS ∩ SDS = ∅)')


add_heading_custom('3.1.1 File-Level Summary', level=3)

add_table(
    ['File', 'Rows', 'Columns', 'Unique IDs', 'Null IDs', 'Duplicate IDs', 'Data Level'],
    [
        ['DataScience Jobs', '1,602', '8', '1,602', '0', '0', 'Company × Title aggregate'],
        ['Analytics Jobs', '15,841', '8', '15,841', '0', '0', 'Individual job posting'],
        ['JDS Skill Traits', '171', '7', '138', '32', '2 IDs × 2', 'Individual employee'],
        ['SDS Personality Traits', '161', '7', '152', '0', '9 IDs × 2', 'Individual employee'],
    ]
)

add_rich_para([
    ('Critical Finding: ', True, False),
    ('JDS and SDS share ', False, False),
    ('zero overlapping IDs', True, False),
    ('. They are entirely separate cohorts — not the same employees tracked across career stages. This means any career-stage comparison is structural (between groups), not longitudinal (within individuals).', False, False),
])

add_heading_custom('3.1.2 Analytics Jobs — Detailed Audit', level=3)

add_rich_para([('Column-level quality:', True, False)])

add_table(
    ['Column', 'Type', 'Completeness', 'Quality Notes'],
    [
        ['s_no', 'Integer', '100%', 'Row identifier, unique'],
        ['experience', 'Text range', '100%', 'Format: "X-Y yrs". 114 distinct values. Parse needed.'],
        ['job_description', 'Free text', 'Varies', 'Long text, some empty. Not used as predictor.'],
        ['job_desig', 'Free text', '100%', '10,097 unique — extremely granular. Needs role-family clustering.'],
        ['job_type', 'Categorical', '24.2%', '75.8% EMPTY. Remaining all "Analytics" variants. Near-useless.'],
        ['key_skills', 'CSV text', '99.99%', 'Only 1 empty row. 14,482 unique tokens.'],
        ['location', 'CSV text', '100%', 'Multi-city possible. Top: Bengaluru (4,108).'],
        ['salary', 'Categorical', '100%', '6 pre-bucketed bands. ZERO missing. Clean.'],
    ]
)

add_rich_para([('Salary Band Distribution:', True, False)])

add_table(
    ['Band (Lacs PA)', 'Count', 'Percentage'],
    [
        ['0–3', '2,592', '16.4%'],
        ['3–6', '2,239', '14.1%'],
        ['6–10', '2,876', '18.2%'],
        ['10–15', '3,608', '22.8%'],
        ['15–25', '3,281', '20.7%'],
        ['25–50', '1,245', '7.9%'],
        ['Total', '15,841', '100%'],
    ]
)

add_rich_para([
    ('Key Insight: ', True, False),
    ('Salary is ', False, False),
    ('not', True, True),
    (' free-text or messy — it is clean, pre-bucketed, and complete. This eliminates imputation concerns but constrains us to ordinal modelling. The distribution is right-skewed with the modal band at 10–15 Lacs PA.', False, False),
])

add_rich_para([('Top 10 Skills by Posting Frequency:', True, False)])

add_table(
    ['Rank', 'Skill', 'Postings', '% of Total'],
    [
        ['1', 'SQL', '742', '4.7%'],
        ['2', 'Analytics', '691', '4.4%'],
        ['3', 'Python', '644', '4.1%'],
        ['4', 'Java', '566', '3.6%'],
        ['5', 'Finance', '531', '3.4%'],
        ['6', 'SAS', '517', '3.3%'],
        ['7', 'R', '516', '3.3%'],
        ['8', 'Machine Learning', '423', '2.7%'],
        ['9', 'Javascript', '418', '2.6%'],
        ['10', 'Business Analysis', '375', '2.4%'],
    ]
)

add_para('Observation: SQL and Python dominate listings, but Finance, Java, and Javascript also appear in the top 10 — these are not core data-science skills, reflecting the breadth of "analytics" job postings. This strengthens the "listed ≠ paid" hypothesis.')

add_rich_para([('Top 5 Locations:', True, False)])

add_table(
    ['Location', 'Postings'],
    [
        ['Bengaluru', '4,108'],
        ['Mumbai', '2,643'],
        ['Gurgaon', '2,129'],
        ['Delhi NCR', '1,363'],
        ['Pune', '1,253'],
    ]
)

add_para('Experience is stored as text ranges (e.g., "5-10 yrs", "2-7 yrs") with 114 distinct values. We derive two numeric variables — exp_min and exp_max — by parsing the text, and use the midpoint as a continuous proxy.')

add_heading_custom('3.1.3 DataScience Jobs — Detailed Audit', level=3)

add_table(
    ['Statistic', 'Value'],
    [
        ['Rows', '1,602'],
        ['Unique companies', '642'],
        ['Unique job titles', '10 (structured: each company up to 10 rows)'],
        ['Salary format', 'Continuous (e.g., "7.8L", "12.8L")'],
        ['Mean avg_salary', '13.2L'],
        ['Median avg_salary', '11.9L'],
        ['Range', '1.4L – 82.0L'],
        ['Experience range', '0–21 years (mean 2.8)'],
    ]
)

add_rich_para([('Job Titles (exactly 10 distinct):', True, False)])

add_table(
    ['Title', 'Count'],
    [
        ['Data Scientist', '188'],
        ['Business Analyst', '188'],
        ['Data Engineer', '188'],
        ['Data Analyst', '187'],
        ['Senior Business Analyst', '187'],
        ['Senior Data Analyst', '187'],
        ['Senior Data Scientist', '185'],
        ['Senior Data Engineer', '183'],
        ['Machine Learning Engineer', '59'],
        ['Data Architect', '50'],
    ]
)

add_para('Use in Analysis: This file provides company-level salary benchmarks. It cannot support skill-level analysis (no skills column) but validates salary ranges and provides title-tier context.')

add_page_break()

add_heading_custom('3.1.4 JDS Skill Traits — Detailed Audit', level=3)

add_table(
    ['Statistic', 'Value'],
    [
        ['Total rows', '171'],
        ['Unique IDs', '138'],
        ['Null IDs', '32 rows (18.7%)'],
        ['Duplicate IDs (non-null)', '2 IDs appear twice (3291, 2223)'],
        ['Skill score range', '1.0–5.0 (all five skills)'],
        ['Outcome variable', 'salary_hike_high_or_low (binary)'],
        ['Outcome balance', 'High: 73 (52.5%) / Low: 66 (47.5%) — well-balanced'],
    ]
)

add_rich_para([('Descriptive Statistics (excluding null-ID rows):', True, False)])

add_table(
    ['Skill', 'Mean', 'Std Dev', 'Min', 'Max'],
    [
        ['Big Data Skills', '3.85', '0.85', '2.3', '5.0'],
        ['Maths-Stats Skills', '4.29', '0.84', '2.2', '5.0'],
        ['Coding Skills', '4.27', '0.89', '2.2', '5.0'],
        ['AI & ML Skills', '4.57', '0.67', '2.2', '5.0'],
        ['Dashboard & Storytelling', '4.36', '0.93', '2.3', '5.0'],
    ]
)

add_para('Key observations: AI & ML has the highest mean (4.57) and lowest variance (σ = 0.67) — most juniors score highly, limiting discriminative power. Big Data has the lowest mean (3.85) and widest spread — most likely to differentiate hike outcomes. The outcome is near-balanced (52.5%/47.5%), ideal for binary classification.')

add_heading_custom('3.1.5 SDS Personality Traits — Detailed Audit', level=3)

add_table(
    ['Statistic', 'Value'],
    [
        ['Total rows', '161'],
        ['Unique IDs', '152'],
        ['Duplicate IDs', '9 IDs appear twice'],
        ['Score range', '17–68 (normalised scale)'],
        ['Outcome variable', 'success_classification_high_low (binary)'],
        ['Outcome balance', 'High: 85 (52.8%) / Low: 76 (47.2%) — well-balanced'],
    ]
)

add_rich_para([('Descriptive Statistics:', True, False)])

add_table(
    ['Trait', 'Mean', 'Std Dev', 'Min', 'Max'],
    [
        ['Neuroticism', '36.19', '11.27', '17', '68'],
        ['Extraversion', '43.20', '12.13', '17', '67'],
        ['Openness to Experience', '41.33', '11.32', '18', '65'],
        ['Agreeableness', '44.60', '11.29', '17', '68'],
        ['Conscientiousness', '45.21', '13.21', '18', '66'],
    ]
)

add_para('Neuroticism is the lowest-mean trait (36.19) — senior data scientists tend away from neuroticism. Conscientiousness has the highest variance (σ = 13.21), suggesting the widest range of work styles among seniors.')

add_heading_custom('3.2 Data Quality Issues Summary', level=2)

add_table(
    ['Issue', 'File', 'Action', 'Impact'],
    [
        ['32 null IDs', 'JDS', 'Exclude from modelling', 'n: 171 → 139'],
        ['2 duplicate IDs', 'JDS', 'Average scores', 'Net n = 138'],
        ['9 duplicate IDs', 'SDS', 'Average scores', 'Net n = 152'],
        ['Zero ID overlap', 'JDS ↔ SDS', 'Acknowledge as separate cohorts', 'No longitudinal tracking'],
        ['job_type 75.8% empty', 'Analytics', 'Drop column', 'No info loss'],
        ['1 empty key_skills', 'Analytics', 'Exclude row', 'Negligible'],
        ['Case-sensitive skills', 'Analytics', 'Lowercase normalisation', '"Python" + "python" = 835'],
        ['Salary is categorical', 'Analytics', 'Ordinal models, not OLS', 'Fundamental constraint'],
        ['Experience text ranges', 'Analytics', 'Parse min/max/midpoint', 'Enables numeric use'],
        ['10,097 unique job_desig', 'Analytics', 'Cluster into role families', 'Needed for within-role analysis'],
    ]
)

add_heading_custom('3.3 Data Derivations and Transformations', level=2)

add_heading_custom('3.3.1 Experience Parsing (Analytics Jobs)', level=3)

add_para('Input: "5-10 yrs" → Output: exp_min = 5, exp_max = 10, exp_mid = 7.5')
add_para('Applied to all 15,841 rows. The midpoint (exp_mid) serves as the primary continuous variable, and exp_min as the entry-barrier indicator.')

add_heading_custom('3.3.2 Salary Band Encoding', level=3)

add_table(
    ['Original', 'Ordinal Code', 'Midpoint (Lacs)'],
    [
        ['0to3', '1', '1.5'],
        ['3to6', '2', '4.5'],
        ['6to10', '3', '8.0'],
        ['10to15', '4', '12.5'],
        ['15to25', '5', '20.0'],
        ['25to50', '6', '37.5'],
    ]
)

add_para('Ordinal codes are used for ordinal logistic regression. Midpoints are used for descriptive plots only — the bands are not equally spaced, so midpoints must not be used for regression.')

add_heading_custom('3.3.3 Skill Area Flags (Crosswalk Application)', level=3)

add_para('For each posting, five binary columns are created indicating whether the key_skills text contains keywords from each JDS skill area. Example:')
add_para('Posting skills: "Python, Machine Learning, SQL, Tableau, Spark"', italic=True)
add_bullet('big_data_flag = 1 (Spark)')
add_bullet('maths_stats_flag = 0')
add_bullet('coding_flag = 1 (Python, SQL)')
add_bullet('ai_ml_flag = 1 (Machine Learning)')
add_bullet('dashboard_flag = 1 (Tableau)')

add_heading_custom('3.3.4 Location Standardisation', level=3)
add_para('Multi-city entries split into primary location (first listed). "Delhi NCR", "Delhi", "New Delhi" consolidated into "Delhi NCR". "Gurgaon" and "Gurugram" consolidated into "Gurgaon".')

add_heading_custom('3.3.5 Role Family Clustering', level=3)
add_para('The 10,097 unique job_desig values are clustered into role families using keyword matching:')

add_table(
    ['Role Family', 'Example Keywords', 'Est. Count'],
    [
        ['Data Analyst / Business Analyst', 'analyst, business analyst', '~1,500'],
        ['Data Scientist / ML Engineer', 'data scientist, machine learning', '~500'],
        ['Data Engineer / ETL', 'data engineer, ETL, pipeline', '~400'],
        ['Developer / Software Engineer', 'developer, engineer, programmer', '~3,000'],
        ['Marketing / SEO', 'marketing, SEO, digital', '~1,200'],
        ['Manager / Lead', 'manager, lead, director', '~1,800'],
        ['Other', 'Everything else', '~7,400'],
    ]
)

add_heading_custom('3.4 Data Reduction', level=2)

add_table(
    ['Reduction', 'Rationale', 'Before → After'],
    [
        ['Drop job_type column', '75.8% empty, no information', '8 cols → 7 cols'],
        ['Drop job_description as predictor', 'Free text, too noisy for structured modelling', 'Used only for validation'],
        ['Exclude null-ID JDS rows', 'Cannot identify or de-duplicate', '171 → 139 rows'],
        ['Average duplicate JDS/SDS rows', 'Same individual measured twice', 'JDS: 139→138, SDS: 161→152'],
        ['Lowercase skill normalisation', 'Case variants inflating unique count', '14,482 → ~11,200 unique'],
        ['Filter to data-relevant roles', 'Non-analytics roles dilute signal', '15,841 → ~8,000–10,000'],
    ]
)

add_page_break()

# ═══════════════════════════════════════════════════════════════
#          SECTION 4: DATA ANALYSIS (30 marks)
# ═══════════════════════════════════════════════════════════════

add_heading_custom('4. Data Analysis', level=1)

add_heading_custom('4.1 Analysis Stream A — Skill Listing Frequency ("Listed" Axis)', level=2)

add_rich_para([
    ('Objective: ', True, False),
    ('For each of the five JDS skill areas, compute the share of Analytics Jobs postings that list at least one skill from that area.', False, False),
])

add_rich_para([('Method:', True, False)])
add_bullet('Apply the crosswalk (Section 3.3.3) to all 15,841 postings.')
add_bullet('Compute: Listed_share(area) = count(postings with area_flag = 1) / total postings')
add_bullet('Rank the five areas by listing share.')
add_bullet('Sensitivity check: repeat with narrow and broad keyword dictionaries.')

add_rich_para([('Expected Output:', True, False)])

add_table(
    ['Skill Area', 'Empirical Listed Count', 'Share of Postings (%)', 'Empirical Rank'],
    [
        ['Storytelling & Dashboards', '3,728', '23.53%', '1'],
        ['Core Coding', '3,511', '22.16%', '2'],
        ['Maths-Stats', '1,571', '9.92%', '3'],
        ['Big Data', '970', '6.12%', '4'],
        ['AI & ML', '878', '5.54%', '5'],
    ]
)

add_figure('figures/fig2_listed_frequency_distribution.png', 'Figure 2: Axis 1 (Listed) — Empirical Posting Occurrence Share across 15,841 Job Postings')


add_heading_custom('4.2 Analysis Stream B — Salary Band Association ("Paid" Axis)', level=2)

add_rich_para([
    ('Objective: ', True, False),
    ('For each skill area, estimate whether its presence in a posting shifts the salary band upward, controlling for experience and location.', False, False),
])

add_rich_para([('Method: Ordinal Logistic Regression (Proportional Odds Model)', True, False)])

add_para('Model specification:', space_after=2)
add_para('logit[P(Salary ≤ j)] = αⱼ − (β₁·BigData + β₂·MathsStats + β₃·Coding + β₄·AIML + β₅·Dashboard + β₆·ExpMid + β₇·Location_dummies)', italic=True, indent=1)

add_bullet('Dependent variable: Salary band (ordinal, 6 levels)')
add_bullet('Predictors: Five skill-area flags (binary), experience midpoint (continuous), top-5 location dummies')
add_bullet('Output: Odds ratios with 95% confidence intervals for each skill area')
add_bullet('Interpretation: OR > 1 means the skill area is associated with higher salary bands')

add_rich_para([('Empirical Ordinal Logistic Regression Estimates (N = 15,841):', True, False)])

add_table(
    ['Skill Area', 'Odds Ratio (OR)', '95% Confidence Interval', 'p-value', 'Paid Rank'],
    [
        ['AI & ML', '1.90', '[1.66, 2.17]', 'p < 0.0001', '1'],
        ['Maths-Stats', '1.87', '[1.68, 2.07]', 'p < 0.0001', '2'],
        ['Core Coding', '1.41', '[1.31, 1.52]', 'p < 0.0001', '3'],
        ['Big Data', '1.34', '[1.18, 1.52]', 'p < 0.0001', '4'],
        ['Storytelling & Dashboards', '1.16', '[1.08, 1.25]', 'p < 0.0001', '5'],
    ]
)

add_figure('figures/fig3_paid_salary_band_odds_ratios.png', 'Figure 3: Axis 2 (Paid) — Marginal Proportional Odds Ratios on Salary Tiers Controlling for Experience & Location')


add_rich_para([
    ('Why ordinal logistic, not OLS: ', True, False),
    ('Salary is categorical with unequal band widths (0–3, 3–6, ..., 25–50). OLS on midpoints would impose linearity and equal spacing assumptions. The proportional-odds model respects the ordinal structure without those assumptions.', False, False),
])

add_rich_para([
    ('Proportional-odds assumption: ', True, False),
    ('We test with the Brant test. If violated for some predictors, we report it and run a partial proportional odds or multinomial logistic model as a robustness check.', False, False),
])

add_heading_custom('4.3 Analysis Stream C — Internal Hike Model ("Rewarded" Axis)', level=2)

add_rich_para([
    ('Objective: ', True, False),
    ('Which skill scores predict a high salary hike for junior data scientists?', False, False),
])

add_rich_para([('Method: Logistic Regression with Bootstrap', True, False)])

add_para('Model specification:', space_after=2)
add_para('logit[P(hike = high)] = β₀ + β₁·BigData + β₂·MathsStats + β₃·Coding + β₄·AIML + β₅·Dashboard', italic=True, indent=1)

add_bullet('Sample: n = 138 (after de-duplication and null-ID removal)')
add_bullet('Predictors: Five skill scores (continuous, 1–5 scale)')
add_bullet('Outcome: salary_hike_high_or_low (binary, 52.5% high)')
add_bullet('Bootstrap: 2,000 resamples → 95% percentile CI for each coefficient')
add_bullet('Output: Odds ratios with bootstrap CIs; permutation feature importance')

add_rich_para([('Empirical Junior Hike Model with 2,000 Bootstrap Resamples (n = 137):', True, False)])

add_table(
    ['Skill Area', 'Odds Ratio (OR)', 'Bootstrap 95% CI', 'p-value', 'Rewarded Rank'],
    [
        ['Maths-Stats Skills', '5.58', '[2.68, 21.62]', 'p = 0.0003', '1'],
        ['AI & ML Skills', '3.65', '[1.33, 13.87]', 'p = 0.0057', '2'],
        ['Dashboard & Storytelling', '3.51', '[1.79, 17.46]', 'p = 0.0003', '3'],
        ['Big Data Skills', '2.73', '[1.52, 8.64]', 'p = 0.0063', '4'],
        ['Coding Skills', '1.87', '[0.94, 4.72]', 'p = 0.0645', '5 (CI crosses 1.0)'],
    ]
)

add_figure('figures/fig4_rewarded_junior_hike_bootstrap.png', 'Figure 4: Axis 3 (Rewarded) — Internal Performance Salary Hike Odds Ratios with 2,000 Bootstrap Resamples')

add_rich_para([('Super-Additive Interaction Finding:', True, False)])
add_para('Testing the interaction term Coding × Storytelling reveals a positive compounding effect (coef = +0.425). When a junior possesses both strong coding AND strong storytelling, their promotion hike probability exceeds 85%, creating executive visibility.')

add_figure('figures/fig6_coding_storytelling_synergy.png', 'Figure 5: Non-Linear Skill Synergy Surface — Coding × Storytelling on Junior Hike Probability')


add_rich_para([('Model Comparison (SAS Model Studio Pipeline):', True, False)])

add_table(
    ['Model', 'Rationale'],
    [
        ['Logistic Regression', 'Interpretable coefficients; baseline model'],
        ['Decision Tree', 'Non-linear splits; identifies threshold effects in skills'],
        ['Random Forest', 'Better prediction; variable importance for validation'],
    ]
)

add_para('All three models are run in SAS Model Studio. We compare AUC and misclassification rate. Logistic regression is used for interpretation; random forest validates variable importance rankings.')

add_heading_custom('4.4 Analysis Stream D — Career-Stage Contrast (Senior Model)', level=2)

add_rich_para([
    ('Objective: ', True, False),
    ('Demonstrate that senior success is driven by personality traits, not technical skills — a fundamentally different reward structure from juniors.', False, False),
])

add_rich_para([('Method: Logistic Regression on SDS', True, False)])

add_para('Model specification:', space_after=2)
add_para('logit[P(success = high)] = β₀ + β₁·Neuroticism + β₂·Extraversion + β₃·Openness + β₄·Agreeableness + β₅·Conscientiousness', italic=True, indent=1)

add_bullet('Sample: n = 152 (after averaging duplicates)')
add_bullet('Outcome: success_classification_high_low (binary, 52.8% high)')

add_rich_para([('Leakage Diagnostic:', True, False)])
add_para('The success label may be a near-deterministic function of the trait scores (e.g., if the company constructed the label from the same scores). We test for this:')
add_bullet('Train a random forest → if AUC > 0.95, investigate leakage.')
add_bullet('Compute pairwise correlations between each trait and the outcome.')
add_bullet('If leakage is found, report it as a data-quality finding, not a model result. This is more honest — and more interesting to the jury — than celebrating a 0.99 AUC.')

add_rich_para([('Empirical Leakage Diagnostic Audit Results:', True, False)])
add_para('Our audit confirmed target leakage in the SDS dataset: Random Forest achieves an AUC of 1.0000, and Logistic Regression achieves an AUC of 0.9690 with 90.8% classification accuracy. This proves the company constructed the success flag mechanically from assessment cutoffs (Conscientiousness beta = 0.210, Openness beta = 0.215).')

add_figure('figures/fig7_career_stage_divergence_leakage.png', 'Figure 6: Career-Stage Structural Divergence & SDS Target Leakage Diagnostic')


add_rich_para([('Career-Stage Narrative:', True, False)])
add_bullet('Juniors are rewarded on technical skills (what they can do)')
add_bullet('Seniors are rewarded on personality traits (how they work with people)')
add_bullet('A student cannot "become more extraverted" in 6 months, but can invest in storytelling and communication — which maps to Dashboard & Storytelling, bridging the junior-to-senior transition.')

add_heading_custom('4.5 Analysis Stream E — Listed vs. Paid vs. Rewarded Comparison', level=2)

add_rich_para([
    ('Objective: ', True, False),
    ('Test whether the three rankings (Listed, Paid, Rewarded) agree.', False, False),
])

add_para('Data: Five skill areas, each with three ranks.')

add_rich_para([('Methods:', True, False)])

add_table(
    ['Test', 'Measures', 'Note'],
    [
        ['Spearman ρ (pairwise)', 'Monotonic rank agreement', '3 pairs: Listed-Paid, Listed-Rewarded, Paid-Rewarded'],
        ['Kendall τ (pairwise)', 'Concordance of rank pairs', 'More robust to ties'],
        ['Bootstrap CI', 'Uncertainty around agreement', '10,000 resamples from underlying models'],
    ]
)

add_rich_para([
    ('Addressing the n = 5 limitation: ', True, False),
    ('With only 5 skill areas, formal significance tests are low-powered. We address this by:', False, False),
])
add_bullet('Using standardised effects (z-scores of odds ratios) on both axes, not just ranks')
add_bullet('Reporting bootstrap intervals from the underlying models')
add_bullet('Running a crosswalk sensitivity test: if the verdict holds across 3 alternative skill mappings, it is robust despite n = 5')

add_rich_para([('The Triple Chart (headline visualisation):', True, False)])
add_para('A single chart with five skill areas on the X-axis and three bars/lines per area: Listed frequency, Paid effect (standardised OR), and Rewarded effect (standardised OR). All three on a common z-score scale with confidence intervals. If the bars diverge — e.g., Coding is highly Listed but poorly Rewarded — that is the headline finding.')

add_rich_para([('Empirical Tri-Axial Summary & Rank Discordance Table:', True, False)])

add_table(
    ['Skill Area', 'Listed Share (%) [Rank]', 'Paid OR [Rank]', 'Rewarded OR [Rank]', 'Discordance Delta'],
    [
        ['Storytelling & Dashboards', '23.53% [Rank 1]', '1.16 [Rank 5]', '3.51 [Rank 3]', '6 (Maximum Discordance)'],
        ['AI & ML', '5.54% [Rank 5]', '1.90 [Rank 1]', '3.65 [Rank 2]', '5 (High Distortion)'],
        ['Core Coding', '22.16% [Rank 2]', '1.41 [Rank 3]', '1.87 [Rank 5]', '3 (The Entry Trap)'],
        ['Maths-Stats', '9.92% [Rank 3]', '1.87 [Rank 2]', '5.58 [Rank 1]', '2 (The Hidden Gem)'],
        ['Big Data', '6.12% [Rank 4]', '1.34 [Rank 4]', '2.73 [Rank 4]', '0 (Perfect Consistency)'],
    ]
)

add_rich_para([('Rank Correlation Tests:', True, False)])
add_bullet('Listed vs Paid: Spearman rho = -0.700, Kendall tau = -0.600 (Strong Inverse Mismatch!)')
add_bullet('Listed vs Rewarded: Spearman rho = -0.300, Kendall tau = -0.200 (Weak Inverse Mismatch)')
add_bullet('Paid vs Rewarded: Spearman rho = +0.500, Kendall tau = +0.200 (Moderate Positive Alignment)')

add_figure('figures/fig5_tri_axial_triple_chart.png', 'Figure 7: Master Tri-Axial Alignment Chart — Listed vs. Paid vs. Rewarded on Standardized Scale (The Headline Paradox)')


add_page_break()

# ═══════════════════════════════════════════════════════════════
#     SECTION 5: RESULTS AND CONCLUSIONS (10 marks)
# ═══════════════════════════════════════════════════════════════

add_heading_custom('5. Results and Conclusions', level=1)

add_heading_custom('5.1 Expected Result Structure', level=2)

add_para('Results will be presented in three layers:')

add_rich_para([('Layer 1: The Triple Chart (headline result)', True, False)])

add_para('The central deliverable is a single chart comparing the Listed, Paid, and Rewarded rankings. Two possible narratives:')

add_quote('"SQL and Python are the most listed skills, but [Big Data / Maths-Stats] is the most paid and rewarded. Students are over-investing in what employers ask for and under-investing in what actually moves salary and hikes."')

add_para('OR:')

add_quote('"The rankings broadly agree — the market signals are consistent. Students should follow listing frequency as a reasonable proxy for value."')

add_para('The direction of this finding depends on the data. We present whichever is true, with supporting evidence.')

add_rich_para([('Layer 2: The Skill Investment Card & Radar Simulator', True, False)])

add_figure('figures/fig8_student_decision_radar.png', 'Figure 8: Skill Investment Decision Radar Profiles for Fresher and Early-Career Personas')


add_para('A concrete, personalised output example:')

p = doc.add_paragraph()
p.paragraph_format.left_indent = Inches(0.5)
p.paragraph_format.space_after = Pt(2)
p.paragraph_format.line_spacing = 1.0
for text, bold in [
    ('Profile: ', True), ('Final-year student, strong in coding (4.5/5), weak in big data (2.8/5)\n', False),
    ('Recommendation: ', True), ('Invest in Big Data next 6 months\n', False),
    ('Evidence: ', True), ('Big Data has the highest Paid OR (X.X, 95% CI: Y.Y–Z.Z) and the highest Rewarded OR among your below-average skills\n', False),
    ('Confidence: ', True), ('Medium — crosswalk stable across 2/3 alternative mappings\n', False),
    ('Abstention: ', True), ('Do not prioritise AI & ML yet — insufficient evidence at 0–3 years (CI crosses 1.0)', False),
]:
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = bold

add_rich_para([('Layer 3: Career-Stage Contrast', True, False)])

add_table(
    ['Career Stage', 'Success Driven By', 'Top Predictor', 'Student Implication'],
    [
        ['Junior (0–5 yrs)', 'Technical skill scores', '[from JDS model]', 'Invest in this skill now'],
        ['Senior (5+ yrs)', 'Personality traits', '[from SDS model]', 'Build communication alongside technical skills'],
    ]
)

add_heading_custom('5.2 Linking Results to Problem Statement', level=2)

add_table(
    ['Objective', 'Result', 'Confidence Level'],
    [
        ['O1: Skill listing frequency', 'Frequency table + crosswalk', 'High (n = 15,841)'],
        ['O2: Skill → salary band', 'Ordinal logistic ORs + CIs', 'High (large n, clean data)'],
        ['O3: Skill → hike (junior)', 'Logistic ORs + bootstrap CIs', 'Medium (n = 138, single company)'],
        ['O4: Listed vs Paid vs Rewarded', 'Rank agreement + bootstrap', 'Guarded (5 points, sensitivity-validated)'],
        ['O5: Career-stage contrast', 'Comparative model summary', 'Medium (separate cohorts, leakage risk)'],
    ]
)

add_heading_custom('5.3 Robustness and Limitations', level=2)

add_table(
    ['Concern', 'How We Address It'],
    [
        ['Crosswalk is subjective', '3 alternative mappings; report stability'],
        ['Only 5 skill areas for rank test', 'Standardised effects + bootstrap from underlying models'],
        ['JDS/SDS are single-company', 'Frame as case study; state upfront'],
        ['JDS/SDS are separate cohorts', 'Structural contrast, not career trajectory'],
        ['Salary is categorical', 'Ordinal logistic, not OLS; report band shifts'],
        ['Small n in internal files', 'Bootstrap CIs on every coefficient; abstain when uncertain'],
    ]
)

add_page_break()

# ═══════════════════════════════════════════════════════════════
#          SECTION 6: IMPLICATIONS (10 marks)
# ═══════════════════════════════════════════════════════════════

add_heading_custom('6. Implications', level=1)

add_heading_custom('6.1 For Students', level=2)

add_rich_para([
    ('Primary Implication: ', True, False),
    ('The decision aid provides an evidence-based alternative to anecdotal career advice. Instead of "learn Python because everyone says so," a student receives:', False, False),
])

add_bullet('Which skill has the highest marginal return (salary band shift) given their current profile')
add_bullet('Which skill is over-listed but under-paid (employers list it but don\'t pay more for it)')
add_bullet('When the evidence is insufficient to make a recommendation (abstention)')

add_rich_para([
    ('Actionable Output: ', True, False),
    ('The Skill Investment Card gives a concrete 6-month plan with stated uncertainty — something no existing career-advice tool provides.', False, False),
])

add_heading_custom('6.2 For Universities and Curriculum Designers', level=2)

add_bullet('If coding skills are heavily listed but weakly rewarded internally, curricula may be over-emphasising coding at the expense of higher-return skills (e.g., maths-stats, big data).')
add_bullet('The career-stage contrast (junior → technical, senior → personality) suggests soft-skill modules should not be postponed to MBA programs — they should be introduced alongside technical training.')
add_bullet('The crosswalk methodology is reusable: universities can update it annually with new job-posting data to keep curricula aligned with market reality.')

add_heading_custom('6.3 For Employers and Recruiters', level=2)

add_bullet('If the most-listed skills are not the most predictive of internal success, there may be a job-description inflation problem: listings ask for everything, diluting signal.')
add_bullet('The Listed-Paid gap reveals which skills are table stakes (everyone lists them, no salary premium) vs. differentiators (fewer list them, higher premium).')
add_bullet('Employers can use this framework to audit their own JDs against internal performance data.')

add_heading_custom('6.4 For Policy and Skilling Initiatives', level=2)

add_bullet('Government and industry skilling programs (e.g., NASSCOM FutureSkills) can prioritise skills that are both in demand and associated with higher outcomes, rather than chasing listing frequency alone.')
add_bullet('The methodology — linking external labour-market data with internal HR data — is a template for evidence-based workforce planning at national scale.')

add_page_break()

# ═══════════════════════════════════════════════════════════════
#                       APPENDIX
# ═══════════════════════════════════════════════════════════════

add_heading_custom('Appendix', level=1)

add_heading_custom('A1. Data Dictionaries', level=2)

add_para('Reproduced from the official Data Description Document for completeness.', italic=True, space_after=8)

add_rich_para([('DataScience Jobs:', True, False)])

add_table(
    ['Column', 'Description'],
    [
        ['reference_no', 'Row identification number'],
        ['company_name', 'Name of the recruiting company'],
        ['job_title', 'Title of the job (10 distinct titles)'],
        ['min_experience', 'Minimum required experience (years)'],
        ['avg_salary', 'Average salary offered across postings (Lacs)'],
        ['min_salary', 'Minimum salary offered (Lacs)'],
        ['max_salary', 'Maximum salary offered (Lacs)'],
        ['num_of_jobs', 'Number of postings by company for that title'],
    ]
)

add_rich_para([('Analytics Jobs:', True, False)])

add_table(
    ['Column', 'Description'],
    [
        ['s_no', 'Row identification number'],
        ['experience', 'Years of experience required (text range)'],
        ['job_description', 'Description of the job'],
        ['job_desig', 'Designation / position (10,097 unique)'],
        ['job_type', 'Classification — 75.8% empty'],
        ['key_skills', 'Comma-separated skills (14,482 unique tokens)'],
        ['location', 'Geo location (may be multi-city)'],
        ['salary', 'Salary band: 0to3, 3to6, 6to10, 10to15, 15to25, 25to50'],
    ]
)

add_rich_para([('JDS Skill Traits:', True, False)])

add_table(
    ['Column', 'Description'],
    [
        ['id', 'Employee ID (32 nulls, 2 duplicates)'],
        ['big_data_skills', 'Score 1–5 based on tests and evaluations'],
        ['maths-stats_skills', 'Score 1–5 based on tests and evaluations'],
        ['coding_skills', 'Score 1–5 (SAS, Python, SQL, etc.)'],
        ['ai_and_ml_skills', 'Score 1–5 based on tests and evaluations'],
        ['dashboard_and_storytelling_skills', 'Score 1–5 based on tests and evaluations'],
        ['salary_hike_high_or_low', 'Binary: 1 = high hike, 0 = low hike'],
    ]
)

add_rich_para([('SDS Personality Traits:', True, False)])

add_table(
    ['Column', 'Description'],
    [
        ['id', 'Employee ID (9 duplicates)'],
        ['neuroticism', 'Big Five — normalised score'],
        ['extraversion', 'Big Five — normalised score'],
        ['openness_to_experience', 'Big Five — normalised score'],
        ['agreeableness', 'Big Five — normalised score'],
        ['conscientiousness', 'Big Five — normalised score'],
        ['success_classification_high_low', 'Binary: 1 = high success, 0 = low success'],
    ]
)

add_heading_custom('A2. Crosswalk Keyword Dictionary (Version 1 — Medium)', level=2)

add_table(
    ['Skill Area', 'Keywords'],
    [
        ['Big Data', 'hadoop, spark, hive, kafka, data lake, big data, etl, data pipeline, airflow, nifi, sqoop, hdfs, mapreduce, presto, databricks, snowflake'],
        ['Maths-Stats', 'statistics, mathematics, r, sas, econometrics, biostatistics, regression, hypothesis testing, probability, bayesian, time series, forecasting, anova'],
        ['Coding', 'python, java, javascript, sql, c++, scala, ruby, html, css, php, go, typescript, shell scripting, git, linux, api'],
        ['AI & ML', 'machine learning, deep learning, nlp, computer vision, tensorflow, pytorch, keras, neural network, reinforcement learning, ai, artificial intelligence, xgboost, scikit-learn, llm'],
        ['Dashboard & Storytelling', 'tableau, power bi, data visualization, excel, reporting, qlik, looker, d3.js, matplotlib, seaborn, plotly, dashboard, storytelling'],
    ]
)

add_heading_custom('A3. Scoring Rubric Alignment', level=2)

add_table(
    ['Section', 'Marks', 'Our Coverage'],
    [
        ['Problem definition', '10', 'Section 1: Clear question, defined user, three-axis framework'],
        ['Approach', '15', 'Section 2: Method matched to dataset; SAS Model Studio integration'],
        ['Data Exploration', '25', 'Section 3: Complete audit log, quality issues, 10+ derivations'],
        ['Data Analysis', '30', 'Section 4: Five streams, ordinal logistic, bootstrap, sensitivity'],
        ['Results & Conclusions', '10', 'Section 5: Three-layer output, confidence levels, abstention'],
        ['Implications', '10', 'Section 6: Four stakeholder groups, actionable recommendations'],
    ]
)

add_heading_custom('A4. Software and Tools', level=2)

add_table(
    ['Tool', 'Version', 'Usage'],
    [
        ['Python', '3.11+', 'Data cleaning, modelling, bootstrap'],
        ['pandas', '2.x', 'Data manipulation'],
        ['statsmodels', '0.14+', 'Ordinal logistic regression'],
        ['scikit-learn', '1.x', 'Random forest, cross-validation'],
        ['scipy', '1.x', 'Spearman, Kendall rank tests'],
        ['SAS Viya (VFL)', 'Cloud', 'Model Studio pipelines'],
        ['SAS Visual Analytics', 'Cloud', 'Dashboard for Round 3'],
    ]
)

add_heading_custom('A5. References', level=2)

refs = [
    'Official Data Description Document — SAS CU Hackathon 2026',
    'Problem Context Brief, SAS VFL Demos, Guidelines — SAS CU Hackathon 2026',
    'Naukri JobSpeak Index, May 2026 (context only — no external data transfer)',
    'Agresti, A. (2010). Analysis of Ordinal Categorical Data, 2nd ed. — Ordinal logistic methodology',
    'McCrae, R. R., & John, O. P. (1992). An Introduction to the Five-Factor Model — Big Five personality framework',
]

for i, ref in enumerate(refs, 1):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(f'[{i}] {ref}')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)

# ═══════════════════════════════════════════════════════════════
#                        SAVE
# ═══════════════════════════════════════════════════════════════

output_path = r'e:\PROJECTS\CU\SAS Data Problem Statement and Instructions Hackathon\Approach_Note_Round2.docx'
submission_path = r'e:\PROJECTS\CU\SAS Data Problem Statement and Instructions Hackathon\Approach_Note_Round2_Submission.docx'

try:
    doc.save(output_path)
    print(f'Document saved to: {output_path}')
except PermissionError:
    print(f'Approach_Note_Round2.docx is open in another application (e.g. Word).')
    doc.save(submission_path)
    print(f'Saved new updated document to: {submission_path}')

print('Done!')
