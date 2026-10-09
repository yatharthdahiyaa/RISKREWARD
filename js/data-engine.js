/**
 * data-engine.js
 * Comprehensive Empirical Data Engine for SAS Viya Visual Analytics Dashboard
 * Project: Listed, Paid, Rewarded (AavishkarHacks Approach Note & Empirical Pipeline)
 */

const SAS_DATA = {
    metadata: {
        projectTitle: "Skill Investment Intelligence: Measuring What Employers List, Pay, and Reward",
        shortTitle: "Listed, Paid, Rewarded",
        tagline: "A Verified, Uncertainty-Aware Next-Skill Decision Aid Built from Four Datasets",
        team: "Aavishkar Hacks",
        teamLead: "Sachin Punetha",
        members: ["Sachin Punetha (Lead)", "Yatharth Dahiya", "Jayant Kumar Bana", "Shivam Rawat"],
        affiliation: "SAS CU Hackathon 2026 | Round 2 (70%) & Round 3 (30%) Submission",
        platform: "SAS Viya® for Learners 2026 | Cloud Analytic Services (CAS)",
        casSession: "CASUSER.casauto (Active, Multi-Threaded In-Memory Engine)",
        dataVintages: "2024-25 Sample Data (Evaluated in 2026 Macroeconomic Context)",
        datasetsAudited: 4,
        totalPostings: 93005,
        granularPostings: 15841,
        juniorCohort: 137,
        seniorCohort: 152,
        bootstrapDraws: 2000
    },

    // Tri-Axial Empirical Framework Parameters (5 Core Skill Areas)
    triAxial: [
        {
            id: "big_data",
            name: "Big Data",
            canonicalSkills: "Hadoop, Spark, PySpark, Hive, Kafka, Snowflake, Data Lake, NoSQL, Redshift, ETL",
            listedCount: 970,
            listedSharePct: 6.12,
            rankListed: 4,
            zListed: -0.838,
            paidOR: 1.340,
            paidCILower: 1.184,
            paidCIUpper: 1.517,
            rankPaid: 4,
            zPaid: -0.594,
            salaryPremiumPct: 11.0,
            salaryPremiumCI: [7.2, 14.9],
            rewardedOR: 2.730,
            rewardedCILower: 1.518,
            rewardedCIUpper: 8.636,
            rankRewarded: 4,
            zRewarded: -0.535,
            rankRewardedDrawsPct: 12.4,
            discordanceDelta: 0,
            verdict: "Agree — Paid and Rewarded (+11.0% market premium, 2.73x promotion odds)",
            hoursPerPoint: 140,
            entryLevelOR: 1.71,
            seniorLevelOR: 1.22
        },
        {
            id: "maths_stats",
            name: "Maths & Statistics",
            canonicalSkills: "Statistics, Probability, Mathematics, Econometrics, Hypothesis Testing, Regression, Time Series, R, SAS",
            listedCount: 1571,
            listedSharePct: 9.92,
            rankListed: 3,
            zListed: -0.404,
            paidOR: 1.867,
            paidCILower: 1.681,
            paidCIUpper: 2.074,
            rankPaid: 2,
            zPaid: 1.010,
            salaryPremiumPct: 9.8,
            salaryPremiumCI: [5.6, 14.1],
            rewardedOR: 5.579,
            rewardedCILower: 2.684,
            rewardedCIUpper: 21.620,
            rankRewarded: 1,
            zRewarded: 1.532,
            rankRewardedDrawsPct: 65.2,
            discordanceDelta: 2,
            verdict: "Decisive Disconnect — Heavily Rewarded (5.58x, #1 Rank in 65% of Draws) despite modest listing",
            hoursPerPoint: 120,
            entryLevelOR: 1.48,
            seniorLevelOR: 2.05
        },
        {
            id: "core_coding",
            name: "Core Coding",
            canonicalSkills: "Python, SQL, Algorithms, Data Structures, Git, Linux, Java, C++, OOP, Backend Integration",
            listedCount: 3511,
            listedSharePct: 22.16,
            rankListed: 2,
            zListed: 0.995,
            paidOR: 1.410,
            paidCILower: 1.311,
            paidCIUpper: 1.517,
            rankPaid: 3,
            zPaid: -0.380,
            salaryPremiumPct: 12.5,
            salaryPremiumCI: [8.1, 17.0],
            rewardedOR: 1.866,
            rewardedCILower: 0.940,
            rewardedCIUpper: 4.724,
            rankRewarded: 5,
            zRewarded: -1.161,
            rankRewardedDrawsPct: 4.8,
            discordanceDelta: 3,
            verdict: "Paid More Than Rewarded — Essential Entry Filter (+12.5%), but Ceiling Effect on promotions (CI crosses 1.0)",
            hoursPerPoint: 100,
            entryLevelOR: 1.89,
            seniorLevelOR: 1.15
        },
        {
            id: "ai_ml",
            name: "AI & Machine Learning",
            canonicalSkills: "Machine Learning, Deep Learning, NLP, Computer Vision, Neural Networks, PyTorch, TensorFlow, Scikit-Learn",
            listedCount: 878,
            listedSharePct: 5.54,
            rankListed: 5,
            zListed: -0.904,
            paidOR: 1.896,
            paidCILower: 1.658,
            paidCIUpper: 2.167,
            rankPaid: 1,
            zPaid: 1.096,
            salaryPremiumPct: 14.2,
            salaryPremiumCI: [9.8, 18.7],
            rewardedOR: 3.652,
            rewardedCILower: 1.327,
            rewardedCIUpper: 13.874,
            rankRewarded: 2,
            zRewarded: 0.134,
            rankRewardedDrawsPct: 18.6,
            discordanceDelta: 5,
            verdict: "The Entry-Level Paradox — High overall premium, but Parity at 0-3 yrs (OR=0.99). Doors open, but no within-role wage bonus.",
            hoursPerPoint: 160,
            entryLevelOR: 0.99,
            seniorLevelOR: 2.34
        },
        {
            id: "storytelling_dashboards",
            name: "Storytelling & Dashboards",
            canonicalSkills: "Tableau, Power BI, Data Visualization, Dashboards, Business Intelligence, Executive Reporting, Storytelling",
            listedCount: 3728,
            listedSharePct: 23.53,
            rankListed: 1,
            zListed: 1.152,
            paidOR: 1.163,
            paidCILower: 1.085,
            paidCIUpper: 1.247,
            rankPaid: 5,
            zPaid: -1.132,
            salaryPremiumPct: 4.2,
            salaryPremiumCI: [1.1, 7.4],
            rewardedOR: 3.507,
            rewardedCILower: 1.794,
            rewardedCIUpper: 17.464,
            rankRewarded: 3,
            zRewarded: 0.029,
            rankRewardedDrawsPct: 14.1,
            discordanceDelta: 6,
            verdict: "The Frequency Trap — #1 Most Listed (23.5%), but #5 Lowest Salary Premium (1.16x). Unlocks 2.18x synergy when paired with Coding.",
            hoursPerPoint: 80,
            entryLevelOR: 1.08,
            seniorLevelOR: 1.32
        }
    ],

    // Non-Parametric Rank Correlations (Empirical proof of labor market divergence)
    correlations: {
        spearmanListedPaid: -0.70,
        spearmanListedRewarded: -0.30,
        spearmanPaidRewarded: 0.50,
        kendallListedPaid: -0.60,
        kendallListedRewarded: -0.20,
        kendallPaidRewarded: 0.20,
        synergyCodingStorytelling: {
            interactionCoef: 0.425,
            pValue: 0.292,
            hikeMultiplier: 2.18
        }
    },

    // 4 Datasets Forensic Audit Log
    dataAudit: [
        {
            dataset: "Analytics Jobs.csv",
            rawCount: "15,841",
            cleanCount: "15,841",
            granularity: "Individual Posting Level",
            primaryKey: "s_no (100% Unique, 0 Collisions)",
            missingProfile: "job_type: 75.8% missing (12,012 nulls); salary: 0% missing; experience: 0% missing",
            statisticalRole: "Core External Labor Market Engine (Listed Frequency & Ordinal Salary Logistic Regression)"
        },
        {
            dataset: "DataScience Jobs.csv",
            rawCount: "1,602",
            cleanCount: "1,602",
            granularity: "Company-Level Aggregates",
            primaryKey: "reference_no (100% Unique)",
            missingProfile: "0% missing; 93,005 aggregate job vacancies documented",
            statisticalRole: "Macro Labor Volume Benchmarking & Market Concentration Index (HHI = 212.8, highly competitive)"
        },
        {
            dataset: "JDS Skill Traits.xlsx",
            rawCount: "171 (Grid)",
            cleanCount: "137 unique juniors",
            granularity: "Junior Analyst Employee Level",
            primaryKey: "emp_id (32 ghost/header rows dropped, 2 duplicate ID pairs averaged)",
            missingProfile: "Evaluated 1-5 skill trait scale is 100% complete across all 5 domains",
            statisticalRole: "Internal Company Performance & Salary Hike Model (Firth's Penalized GLM & BCa Bootstrap B=2,000)"
        },
        {
            dataset: "SDS Personality Traits.xlsx",
            rawCount: "161",
            cleanCount: "152 unique seniors",
            granularity: "Senior Consultant Employee Level",
            primaryKey: "emp_id (9 duplicate ID pairs averaged)",
            missingProfile: "Big Five OCEAN personality scores (range 17-68) 100% complete",
            statisticalRole: "Senior Diagnostic Audit, Target Leakage Discovery (AUC=1.0) & Career-Stage Divergence"
        }
    ],

    // Crosswalk Sensitivity Regime Results (Table 12 & Table 15 from Approach Note)
    crosswalkSensitivity: {
        baseline: [
            { skill: "Big Data", entryOR: 1.71, ci: [1.40, 2.08], robust: "Paid in 3/3" },
            { skill: "Maths & Stats", entryOR: 1.48, ci: [1.25, 1.74], robust: "Paid in 3/3" },
            { skill: "Core Coding", entryOR: 1.89, ci: [1.58, 2.26], robust: "Paid in 3/3" },
            { skill: "AI & ML", entryOR: 0.99, ci: [0.81, 1.22], robust: "Not Paid at Entry (Crosses 1.0)" },
            { skill: "Storytelling & Dashboards", entryOR: 1.08, ci: [0.94, 1.23], robust: "Not Paid at Entry (Crosses 1.0)" }
        ],
        strict: [
            { skill: "Big Data", entryOR: 1.64, ci: [1.34, 2.01], robust: "Paid in 3/3" },
            { skill: "Maths & Stats", entryOR: 1.54, ci: [1.30, 1.83], robust: "Paid in 3/3" },
            { skill: "Core Coding", entryOR: 1.81, ci: [1.52, 2.16], robust: "Paid in 3/3" },
            { skill: "AI & ML", entryOR: 1.10, ci: [0.88, 1.37], robust: "Not Paid at Entry (Crosses 1.0)" },
            { skill: "Storytelling & Dashboards", entryOR: 1.04, ci: [0.90, 1.20], robust: "Not Paid at Entry (Crosses 1.0)" }
        ],
        broad: [
            { skill: "Big Data", entryOR: 1.59, ci: [1.29, 1.95], robust: "Paid in 3/3" },
            { skill: "Maths & Stats", entryOR: 1.45, ci: [1.22, 1.71], robust: "Paid in 3/3" },
            { skill: "Core Coding", entryOR: 1.76, ci: [1.47, 2.10], robust: "Paid in 3/3" },
            { skill: "AI & ML", entryOR: 1.19, ci: [0.96, 1.48], robust: "Not Paid at Entry (Crosses 1.0)" },
            { skill: "Storytelling & Dashboards", entryOR: 1.11, ci: [0.97, 1.27], robust: "Not Paid at Entry (Crosses 1.0)" }
        ]
    },

    // Salary Bands Breakdown (15,841 Postings)
    salaryBands: [
        { band: "0 to 3 LPA", count: 4893, pct: 30.89, mid: 1.5 },
        { band: "3 to 6 LPA", count: 4945, pct: 31.22, mid: 4.5 },
        { band: "6 to 10 LPA", count: 2884, pct: 18.21, mid: 8.0 },
        { band: "10 to 15 LPA", count: 1832, pct: 11.56, mid: 12.5 },
        { band: "15 to 25 LPA", count: 981, pct: 6.19, mid: 20.0 },
        { band: "25 to 50 LPA", count: 306, pct: 1.93, mid: 37.5 }
    ],

    // Experience Brackets Breakdown (15,841 Postings)
    experienceBands: [
        { bracket: "0-2 yrs (Fresher/Entry)", count: 2715, pct: 17.14 },
        { bracket: "3-5 yrs (Junior)", count: 6842, pct: 43.19 },
        { bracket: "6-8 yrs (Mid-Level)", count: 3824, pct: 24.14 },
        { bracket: "9-12 yrs (Senior)", count: 1845, pct: 11.65 },
        { bracket: "12+ yrs (Lead/Principal)", count: 615, pct: 3.88 }
    ],

    // Geographic Metro Concentration
    metros: [
        { name: "Bengaluru", count: 4721, sharePct: 29.8 },
        { name: "Mumbai / Navi Mumbai", count: 2314, sharePct: 14.6 },
        { name: "Delhi-NCR (Gurgaon/Noida)", count: 2598, sharePct: 16.4 },
        { name: "Hyderabad", count: 1842, sharePct: 11.6 },
        { name: "Pune", count: 1629, sharePct: 10.3 },
        { name: "Chennai", count: 1104, sharePct: 7.0 },
        { name: "Other Locations", count: 1633, sharePct: 10.3 }
    ],

    // Senior Personality Traits & Leakage Audit Data
    sdsAudit: {
        totalSeniors: 152,
        highSuccessCount: 68,
        lowSuccessCount: 84,
        models: [
            { name: "Firth Penalized Logit (All 5 OCEAN)", auc: 0.969, accuracy: "93.4%", status: "Suspiciously High" },
            { name: "Random Forest Classifier (100 Trees)", auc: 1.000, accuracy: "100.0%", status: "Saturated Leakage" },
            { name: "Simple Additive Sum Cutoff (>194)", auc: 0.961, accuracy: "92.5%", status: "Artifact of Construction" }
        ],
        traits: [
            { trait: "Conscientiousness", highMean: 48.6, lowMean: 35.2, or: 3.84, ci: [2.12, 6.95], pVal: "<0.001" },
            { trait: "Openness", highMean: 45.1, lowMean: 34.8, or: 2.91, ci: [1.74, 4.88], pVal: "<0.001" },
            { trait: "Agreeableness", highMean: 42.8, lowMean: 33.6, or: 2.45, ci: [1.51, 3.98], pVal: "<0.001" },
            { trait: "Extraversion", highMean: 41.5, lowMean: 34.1, or: 2.12, ci: [1.32, 3.41], pVal: "0.002" },
            { trait: "Emotional Stability (Low Neuroticism)", highMean: 44.2, lowMean: 36.4, or: 1.95, ci: [1.21, 3.14], pVal: "0.006" }
        ],
        takeaway: "Jury Defense: We proved SDS target leakage rather than blindly publishing 100% accuracy. Seniors succeed on Conscientiousness & executive composure, whereas Juniors advance on rigorous technical execution."
    },

    // Benchmark Student Personas from Approach Note Table 20 & Student Decision Aid
    personas: {
        asha: {
            name: "Asha (Final-Year Fresher)",
            title: "Data Analyst Aspirant (Maths-Weak, Coding-Solid)",
            experienceYrs: 0.0,
            targetRole: "Data Analyst (0-3 yrs)",
            totalHours: 400,
            scores: {
                big_data: 3.2,
                maths_stats: 3.0,
                core_coding: 4.6,
                ai_ml: 4.2,
                dashboards: 3.0
            },
            notes: "Matches Table 20 in Approach Note: Strong in coding and ML theory, but lagging in statistics foundations and business dashboarding."
        },
        rohan: {
            name: "Rohan (ML Enthusiast Fresher)",
            title: "Data Scientist / ML Engineer Aspirant",
            experienceYrs: 0.0,
            targetRole: "Junior Data Scientist (0-3 yrs)",
            totalHours: 350,
            scores: {
                big_data: 3.6,
                maths_stats: 3.8,
                core_coding: 4.2,
                ai_ml: 4.9,
                dashboards: 2.8
            },
            notes: "Matches Table 20 in Approach Note: AI/ML is already saturated (4.9). Recommends Maths & Stats (61%) and Dashboards (37%)."
        },
        meera: {
            name: "Meera (High-Performing Junior)",
            title: "Early-Career Analyst (Near-Ceiling Profile)",
            experienceYrs: 2.5,
            targetRole: "Senior Analytics Specialist",
            totalHours: 200,
            scores: {
                big_data: 4.6,
                maths_stats: 4.9,
                core_coding: 4.9,
                ai_ml: 4.9,
                dashboards: 4.8
            },
            notes: "Matches Table 20 in Approach Note: Within 0.3 of typical high-hike profile across all domains. Diminishing returns; formal saturation trigger."
        },
        kabir: {
            name: "Kabir (Coding-Deficient Aspirant)",
            title: "Data Engineer Aspirant with Sub-Baseline Coding",
            experienceYrs: 0.5,
            targetRole: "Data Engineer (0-3 yrs)",
            totalHours: 400,
            scores: {
                big_data: 3.5,
                maths_stats: 3.5,
                core_coding: 1.5,
                ai_ml: 3.5,
                dashboards: 3.5
            },
            notes: "Matches Table 20 in Approach Note: Core coding (1.5) is critically below empirical entry threshold (<2.0). Triggers formal ABSTENTION."
        },
        vikram: {
            name: "Vikram (Mid-Level Data Scientist)",
            title: "Customer-Facing Analytics Lead",
            experienceYrs: 5.5,
            targetRole: "Principal Data Scientist",
            totalHours: 300,
            scores: {
                big_data: 4.2,
                maths_stats: 4.0,
                core_coding: 4.5,
                ai_ml: 4.1,
                dashboards: 3.2
            },
            notes: "Mid-level transition: Technical skills at high baseline; requires Storytelling & Dashboards to unlock senior executive visibility bonus."
        }
    },

    // Typical High-Hike Profile Benchmark (JDS high-hike cohort median)
    benchmarkProfile: {
        big_data: 3.8,
        maths_stats: 5.0,
        core_coding: 5.0,
        ai_ml: 5.0,
        dashboards: 5.0
    }
};

// Export to window if running in browser
if (typeof window !== "undefined") {
    window.SAS_DATA = SAS_DATA;
}
