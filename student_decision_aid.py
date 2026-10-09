"""
student_decision_aid.py
=======================
Interactive Prescriptive Decision Engine & Skill Investment Simulator
Based on the Tri-Axial Empirical Evidence Framework (Listed vs Paid vs Rewarded)
SAS CU Hackathon Round 2 & Round 3 Deliverable

Usage:
  python student_decision_aid.py --demo
  python student_decision_aid.py --interactive
"""

import sys
import argparse
import numpy as np

# Empirical Weights from Tri-Axial Pipeline
EMPIRICAL_PARAMETERS = {
    'Big Data': {
        'listed_share': 6.12,
        'paid_or': 1.331,
        'paid_ci': (1.176, 1.505),
        'rewarded_or': 2.730,
        'rewarded_ci': (1.327, 5.613),
        'rank_listed': 4,
        'rank_paid': 4,
        'rank_rewarded': 4,
        'learning_hours_per_point': 140
    },
    'Maths-Stats': {
        'listed_share': 9.92,
        'paid_or': 2.006,
        'paid_ci': (1.806, 2.228),
        'rewarded_or': 5.580,
        'rewarded_ci': (2.199, 14.154),
        'rank_listed': 3,
        'rank_paid': 1,
        'rank_rewarded': 1,
        'learning_hours_per_point': 120
    },
    'Core Coding': {
        'listed_share': 22.16,
        'paid_or': 1.392,
        'paid_ci': (1.294, 1.496),
        'rewarded_or': 1.866,
        'rewarded_ci': (0.963, 3.615),  # Notice: CI crosses 1.0 at 95% level!
        'rank_listed': 2,
        'rank_paid': 3,
        'rank_rewarded': 5,
        'learning_hours_per_point': 100
    },
    'AI & ML': {
        'listed_share': 5.54,
        'paid_or': 1.884,
        'paid_ci': (1.647, 2.155),
        'rewarded_or': 3.652,
        'rewarded_ci': (1.459, 9.143),
        'rank_listed': 5,
        'rank_paid': 2,
        'rank_rewarded': 2,
        'learning_hours_per_point': 160
    },
    'Storytelling & Dashboards': {
        'listed_share': 23.53,
        'paid_or': 1.190,
        'paid_ci': (1.110, 1.275),
        'rewarded_or': 3.507,
        'rewarded_ci': (1.770, 6.945),
        'rank_listed': 1,
        'rank_paid': 5,
        'rank_rewarded': 3,
        'learning_hours_per_point': 80
    }
}


def evaluate_abstention(skill_name, current_score, experience_yrs):
    """
    Evaluates whether the system should formally ABSTAIN from recommending a skill.
    """
    reasons = []
    data = EMPIRICAL_PARAMETERS[skill_name]
    
    # Condition 1: CI crosses parity (1.0)
    if data['rewarded_ci'][0] < 1.0:
        reasons.append(
            f"Statistically ambiguous internal return (95% CI: [{data['rewarded_ci'][0]:.2f}, {data['rewarded_ci'][1]:.2f}] crosses 1.0). "
            "Skill serves as baseline entry filter but does not differentiate promotions."
        )
    
    # Condition 2: Premature deep specialisation for freshers
    if skill_name == 'AI & ML' and experience_yrs < 1.0 and current_score < 3.0:
        reasons.append(
            "Premature specialisation risk: Fresher postings (<1 yr) requiring AI/ML demand verified core coding proficiency first."
        )
        
    # Condition 3: Saturation limit
    if current_score >= 4.5:
        reasons.append(
            f"Diminishing returns threshold reached (Score {current_score:.1f}/5.0). Marginal gain per study hour is minimal."
        )
        
    return reasons


def optimize_skill_investment(current_scores, experience_yrs, total_hours=400):
    """
    Solves greedy knapsack human capital allocation under time constraints.
    """
    allocations = {}
    remaining_hours = total_hours
    
    # Compute ROI: Composite Return / Hours per Point
    roi_scores = {}
    for skill, score in current_scores.items():
        data = EMPIRICAL_PARAMETERS[skill]
        # Composite career weight: Paid OR * Rewarded OR
        # For freshers, Paid has 60% weight, Rewarded 40%
        # For experienced, Rewarded has 70% weight, Paid 30%
        if experience_yrs <= 2.0:
            comp_score = 0.6 * np.log(data['paid_or']) + 0.4 * np.log(data['rewarded_or'])
        else:
            comp_score = 0.3 * np.log(data['paid_or']) + 0.7 * np.log(data['rewarded_or'])
            
        headroom = max(0.0, 5.0 - score)
        cost = data['learning_hours_per_point']
        
        # Penalize if baseline coding is critically low (<2.5)
        if skill != 'Core Coding' and current_scores.get('Core Coding', 0) < 2.5:
            comp_score *= 0.5
            
        roi_scores[skill] = (comp_score / cost, headroom, cost)
        
    # Sort skills by ROI descending
    sorted_skills = sorted(roi_scores.keys(), key=lambda s: roi_scores[s][0], reverse=True)
    
    for skill in sorted_skills:
        roi, headroom, cost = roi_scores[skill]
        if headroom <= 0.1 or remaining_hours <= 20:
            allocations[skill] = (0.0, 0)
            continue
            
        # Target up to 1.5 score increase or headroom limit
        desired_increase = min(1.5, headroom)
        hours_needed = desired_increase * cost
        
        if hours_needed <= remaining_hours:
            allocations[skill] = (desired_increase, hours_needed)
            remaining_hours -= hours_needed
        else:
            possible_increase = remaining_hours / cost
            allocations[skill] = (possible_increase, remaining_hours)
            remaining_hours = 0
            
    return allocations


def generate_decision_card(persona_name, experience_yrs, current_scores, target_role, budget_hours=400):
    """
    Generates the publication-quality Decision Card.
    """
    print("=" * 80)
    print(f"        SKILL INVESTMENT DECISION CARD: {persona_name.upper()}")
    print("=" * 80)
    print(f"Candidate Profile : Experience: {experience_yrs} yrs | Target Role: {target_role}")
    print(f"Learning Budget   : {budget_hours} hours over 6 months")
    print("-" * 80)
    print("CURRENT PROFICIENCY BASELINE:")
    for skill, score in current_scores.items():
        bar = "#" * int(score * 4) + "-" * (20 - int(score * 4))
        print(f"  * {skill:26s}: [{bar}] {score:.1f}/5.0")
    print("-" * 80)
    
    # Run optimization
    alloc = optimize_skill_investment(current_scores, experience_yrs, budget_hours)
    
    print("OPTIMAL 6-MONTH ALLOCATION ROADMAP:")
    top_recommended = []
    for skill, (delta, hours) in alloc.items():
        if delta > 0.1:
            top_recommended.append((skill, delta, hours))
            data = EMPIRICAL_PARAMETERS[skill]
            new_score = min(5.0, current_scores[skill] + delta)
            print(f"\n  [PRIORITY ACTION] {skill.upper()}: +{delta:.1f} pts ({int(hours)} Study Hours)")
            print(f"    * Projected Proficiency: {current_scores[skill]:.1f} -> {new_score:.1f}/5.0")
            print(f"    * External Salary Odds Ratio Shift: {data['paid_or']:.2f}x (95% CI: [{data['paid_ci'][0]:.2f}, {data['paid_ci'][1]:.2f}])")
            print(f"    * Internal Hike Odds Ratio Shift  : {data['rewarded_or']:.2f}x (95% CI: [{data['rewarded_ci'][0]:.2f}, {data['rewarded_ci'][1]:.2f}])")
            
            # Synergy commentary
            if skill == 'Storytelling & Dashboards' and current_scores.get('Core Coding', 0) >= 3.0:
                print("    * SYNERGY MULTIPLIER: High Coding + High Storytelling unlocks executive visibility bonus (+2.18x hike probability).")
                
    print("\n" + "-" * 80)
    print("FORMAL ABSTENTION & STATISTICAL WARNING REGISTER:")
    abstentions_found = 0
    for skill in current_scores.keys():
        reasons = evaluate_abstention(skill, current_scores[skill], experience_yrs)
        for r in reasons:
            abstentions_found += 1
            print(f"  [ABSTAIN / WARNING] {skill}:")
            print(f"    -> {r}")
            
    if abstentions_found == 0:
        print("  * No active abstention flags triggered for current profile.")
        
    print("-" * 80)
    print("CAREER-STAGE TRANSITION DIRECTIVE:")
    if experience_yrs <= 2.0:
        print("  * JUNIOR FOCUS: Your career velocity is strictly governed by verified quantitative/technical skills.")
        print("    Focus on objective execution, math foundations, and reproducible pipelines.")
    else:
        print("  * SENIOR TRANSITION: Our SDS cohort diagnostic reveals that beyond mid-level, technical skills")
        print("    reach parity. Advancement depends on Conscientiousness and client-facing communication.")
    print("=" * 80 + "\n")


def run_benchmark_personas():
    """
    Demonstrates the Decision Card across three benchmark student personas.
    """
    # Persona 1: Final-Year Fresher
    generate_decision_card(
        persona_name="Persona 1: Final-Year Fresher (Math-Heavy, Coding-Weak)",
        experience_yrs=0.0,
        current_scores={
            'Big Data': 1.5,
            'Maths-Stats': 4.2,
            'Core Coding': 2.2,
            'AI & ML': 2.0,
            'Storytelling & Dashboards': 2.0
        },
        target_role="Entry-Level Data Scientist",
        budget_hours=400
    )
    
    # Persona 2: Junior Data Analyst (2 Yrs Exp, Seeking Promotion)
    generate_decision_card(
        persona_name="Persona 2: Early-Career Analyst (Coding Strong, Storytelling Weak)",
        experience_yrs=2.0,
        current_scores={
            'Big Data': 3.0,
            'Maths-Stats': 3.2,
            'Core Coding': 4.3,
            'AI & ML': 2.8,
            'Storytelling & Dashboards': 2.1
        },
        target_role="Senior Analytics Consultant",
        budget_hours=350
    )
    
    # Persona 3: Senior Consultant Transition
    generate_decision_card(
        persona_name="Persona 3: Mid-Level Data Scientist (Targeting Principal/Customer-Facing)",
        experience_yrs=5.5,
        current_scores={
            'Big Data': 4.2,
            'Maths-Stats': 4.0,
            'Core Coding': 4.5,
            'AI & ML': 4.1,
            'Storytelling & Dashboards': 3.2
        },
        target_role="Customer-Facing Senior Data Scientist",
        budget_hours=300
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Empirical Skill Investment Decision Aid")
    parser.add_argument('--demo', action='store_true', help="Run automated benchmark student personas")
    parser.add_argument('--interactive', action='store_true', help="Interactive CLI prompt")
    
    args = parser.parse_args()
    
    if args.interactive:
        print("--- Interactive Student Profile Input ---")
        exp = float(input("Years of Experience (e.g., 0.0 for fresher): "))
        print("Enter current proficiency scores (1.0 to 5.0):")
        scores = {}
        for s in ['Big Data', 'Maths-Stats', 'Core Coding', 'AI & ML', 'Storytelling & Dashboards']:
            scores[s] = float(input(f"  {s}: "))
        budget = float(input("Total Study Hours available (e.g., 400): "))
        role = input("Target Career Role: ")
        generate_decision_card("Custom User", exp, scores, role, budget)
    else:
        run_benchmark_personas()
