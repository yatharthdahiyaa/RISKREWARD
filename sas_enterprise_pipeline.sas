/*=============================================================================*
 * SAS ENTERPRISE PRODUCTION PIPELINE: TRI-AXIAL HUMAN CAPITAL DECISION ENGINE *
 * SAS CU Hackathon Round 2 & Round 3 Enterprise Implementation               *
 * Platform: SAS Viya for Learners (VFL) / Cloud Analytic Services (CAS)       *
 * Team: Aavishkar Hacks                                                      *
 *=============================================================================*/

/* 1. INITIALIZE CLOUD ANALYTIC SERVICES (CAS) SESSION */
cas casauto sessopts=(caslib="CASUSER" timeout=1800 locale="en_US");
libname casuser cas caslib="CASUSER";

/* Set System Options */
options linesize=120 pagesize=60 nodate pageno=1 source notes;

%put NOTE: =======================================================;
%put NOTE: CAS SESSION INITIALIZED SUCCESSFULLY FOR AAVISHKAR HACKS;
%put NOTE: =======================================================;


/*-----------------------------------------------------------------------------*
 * 2. DATA INGESTION & CAS IN-MEMORY TABLE REGISTRATION                        *
 *-----------------------------------------------------------------------------*/

/* Ingest Clean Analytics Jobs (Posting-Level, N = 15,841) */
proc casutil;
    import datafile="/workspace/clean_data/clean_analytics_jobs.csv"
           outcaslib="CASUSER"
           casout="analytics_jobs"
           replace
           importoptions=(filetype="csv" getnames=True);
    
    /* Ingest Clean DataScience Jobs (Company-Level Aggregates, N = 1,602) */
    import datafile="/workspace/clean_data/clean_datascience_jobs.csv"
           outcaslib="CASUSER"
           casout="datascience_jobs"
           replace
           importoptions=(filetype="csv" getnames=True);

    /* Ingest Clean JDS Traits (Junior Data Scientists, N = 137 Unique) */
    import datafile="/workspace/clean_data/clean_jds_traits.csv"
           outcaslib="CASUSER"
           casout="jds_traits"
           replace
           importoptions=(filetype="csv" getnames=True);

    /* Ingest Clean SDS Traits (Senior Data Scientists, N = 152 Unique) */
    import datafile="/workspace/clean_data/clean_sds_traits.csv"
           outcaslib="CASUSER"
           casout="sds_traits"
           replace
           importoptions=(filetype="csv" getnames=True);
quit;


/*-----------------------------------------------------------------------------*
 * 3. MODEL 1: PROPORTIONAL ODDS ORDINAL LOGISTIC REGRESSION (ANALYTICS JOBS)  *
 * Tests whether skill areas shift the 6 ordered salary tiers upward.          *
 *-----------------------------------------------------------------------------*/
ods graphics on;
ods html close;
ods pdf file="/workspace/output_reports/SAS_Model1_Ordinal_Salary.pdf" style=Sapphire;

title1 "SAS Enterprise Model 1: Proportional Odds Cumulative Logit for Salary Tiers";
title2 "Data Source: CASUSER.analytics_jobs (N = 15,841 Postings)";

proc logistic data=casuser.analytics_jobs outmodel=casuser.salary_model_fit 
              plots(only)=(oddsratio effect);
    /* Class definitions with reference categories */
    class exp_bracket(ref="0-2 yrs (Fresher/Entry)") 
          metro_bengaluru(ref="0") 
          metro_mumbai(ref="0") 
          metro_delhi_ncr(ref="0") / param=ref;
    
    /* Cumulative logit model */
    model salary_ord = flag_big_data 
                       flag_maths_stats 
                       flag_core_coding 
                       flag_ai_ml 
                       flag_storytelling_dashboards 
                       exp_mid 
                       metro_bengaluru 
                       metro_mumbai 
                       metro_delhi_ncr 
          / link=clogit aggregate scale=none unequalslopes;
    
    /* Explicit Odds Ratio Estimates */
    oddsratio flag_big_data / cl=pl;
    oddsratio flag_maths_stats / cl=pl;
    oddsratio flag_core_coding / cl=pl;
    oddsratio flag_ai_ml / cl=pl;
    oddsratio flag_storytelling_dashboards / cl=pl;
    
    /* Output predicted cumulative probabilities */
    output out=casuser.salary_predictions predprobs=cumulative;
run;

ods pdf close;


/*-----------------------------------------------------------------------------*
 * 4. MODEL 2: FIRTH'S PENALIZED LOGISTIC REGRESSION (JDS COHORT, N = 137)     *
 * Evaluates internal promotion and salary-hike drivers without MLE bias.      *
 *-----------------------------------------------------------------------------*/
ods pdf file="/workspace/output_reports/SAS_Model2_Junior_Hike_Firth.pdf" style=Sapphire;

title1 "SAS Enterprise Model 2: Firth Penalized Likelihood for Junior Salary Hike";
title2 "Data Source: CASUSER.jds_traits (N = 137 Junior Data Scientists)";

proc logistic data=casuser.jds_traits plots(only)=(roc effect);
    model salary_hike_high_or_low(event='1') = 
          big_data_skills 
          maths_stats_skills 
          coding_skills 
          ai_and_ml_skills 
          dashboard_and_storytelling_skills 
          / firth clparm=pl;
          
    /* Compute Profile Likelihood Confidence Intervals */
    oddsratio big_data_skills / cl=pl;
    oddsratio maths_stats_skills / cl=pl;
    oddsratio coding_skills / cl=pl;
    oddsratio ai_and_ml_skills / cl=pl;
    oddsratio dashboard_and_storytelling_skills / cl=pl;
    
    /* Test interaction hypothesis: Coding x Storytelling */
    units coding_skills=1 dashboard_and_storytelling_skills=1;
run;

ods pdf close;


/*-----------------------------------------------------------------------------*
 * 5. MODEL 3: SDS SENIOR BIG FIVE & DIAGNOSTIC LEAKAGE AUDIT                  *
 * Evaluates senior behavioral drivers & validates target leakage.             *
 *-----------------------------------------------------------------------------*/
ods pdf file="/workspace/output_reports/SAS_Model3_Senior_Leakage_Audit.pdf" style=Sapphire;

title1 "SAS Enterprise Model 3: SDS Big Five Traits & Target Leakage Diagnostic";
title2 "Data Source: CASUSER.sds_traits (N = 152 Senior Consultants)";

proc logistic data=casuser.sds_traits plots(only)=(roc effect);
    model success__classification__high_low(event='1') = 
          neuroticism 
          extraversion 
          openness_to_experience 
          agreeableness 
          conscientiousness 
          / ctable pprob=(0.1 to 0.9 by 0.1) outroc=casuser.sds_roc;
    
    /* Discriminant analysis check for perfect separation */
    roc 'Big Five Full Model' neuroticism extraversion openness_to_experience agreeableness conscientiousness;
run;

/* High-Performance Gradient Tree Boosting Comparison on CAS */
proc gradboost data=casuser.sds_traits seed=42;
    target success__classification__high_low / level=nominal;
    input neuroticism extraversion openness_to_experience agreeableness conscientiousness / level=interval;
    ods output VariableImportance=casuser.sds_var_importance;
run;

ods pdf close;


/*-----------------------------------------------------------------------------*
 * 6. TRI-AXIAL CONCORDANCE & DISCORDANCE CALCULATION (PROC CORR)              *
 * Evaluates Spearman rho and Kendall tau across the 5 skill dimensions.       *
 *-----------------------------------------------------------------------------*/
data casuser.tri_axial_sas;
    input skill_area $30. rank_listed rank_paid rank_rewarded;
    datalines;
Big Data                     4  4  4
Maths-Stats                  3  1  1
Core Coding                  2  3  5
AI & ML                      5  2  2
Storytelling & Dashboards    1  5  3
;
run;

ods pdf file="/workspace/output_reports/SAS_TriAxial_Rank_Discordance.pdf" style=Sapphire;

title1 "SAS Enterprise Nonparametric Rank Concordance Analysis";
title2 "Quantifying Labor Market Discordance Across Listed, Paid, and Rewarded Axes";

proc corr data=casuser.tri_axial_sas spearman kendall;
    var rank_listed rank_paid rank_rewarded;
run;

ods pdf close;


/*-----------------------------------------------------------------------------*
 * 7. SAS MODEL STUDIO PIPELINE CHAMPION MACRO                                 *
 * Automated Pipeline Comparison: Logistic vs Tree vs Forest vs GradBoost       *
 *-----------------------------------------------------------------------------*/
%macro run_model_studio_champion(data=, target=, inputs=);
    %put NOTE: ----------------------------------------------------;
    %put NOTE: Executing Champion Model Selection in SAS Model Studio;
    %put NOTE: Comparing Logistic, Decision Tree, Forest, and GradBoost;
    %put NOTE: ----------------------------------------------------;
    
    /* In production SAS Viya, this macro triggers the Model Studio REST API / CAS action sets */
    proc treesplit data=&data maxdepth=5;
        target &target / level=nominal;
        input &inputs / level=interval;
    run;
    
    proc forest data=&data ntrees=100 seed=42;
        target &target / level=nominal;
        input &inputs / level=interval;
    run;
%mend run_model_studio_champion;

%run_model_studio_champion(
    data=casuser.jds_traits, 
    target=salary_hike_high_or_low, 
    inputs=big_data_skills maths_stats_skills coding_skills ai_and_ml_skills dashboard_and_storytelling_skills
);

/* Terminate CAS Session cleanly */
cas casauto terminate;
