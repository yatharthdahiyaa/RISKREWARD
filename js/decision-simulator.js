/**
 * decision-simulator.js
 * Interactive Prescriptive Decision Engine & Skill Investment Simulator
 * Implements the Knapsack Human Capital Optimizer and Formal Abstention Register
 * Based on AavishkarHacks Approach Note Section 4.5 & student_decision_aid.py
 */

const DecisionSimulator = {
    // Empirical parameters for the 5 skills
    skills: {
        big_data: {
            name: "Big Data",
            paidOR: 1.340,
            paidCI: [1.184, 1.517],
            rewardedOR: 2.730,
            rewardedCI: [1.518, 8.636],
            rankListed: 4,
            rankPaid: 4,
            rankRewarded: 4,
            hoursPerPoint: 140,
            entryOR: 1.71
        },
        maths_stats: {
            name: "Maths & Statistics",
            paidOR: 1.867,
            paidCI: [1.681, 2.074],
            rewardedOR: 5.579,
            rewardedCI: [2.684, 21.620],
            rankListed: 3,
            rankPaid: 2,
            rankRewarded: 1,
            hoursPerPoint: 120,
            entryOR: 1.48
        },
        core_coding: {
            name: "Core Coding",
            paidOR: 1.410,
            paidCI: [1.311, 1.517],
            rewardedOR: 1.866,
            rewardedCI: [0.940, 4.724], // Crosses 1.0!
            rankListed: 2,
            rankPaid: 3,
            rankRewarded: 5,
            hoursPerPoint: 100,
            entryOR: 1.89
        },
        ai_ml: {
            name: "AI & Machine Learning",
            paidOR: 1.896,
            paidCI: [1.658, 2.167],
            rewardedOR: 3.652,
            rewardedCI: [1.327, 13.874],
            rankListed: 5,
            rankPaid: 1,
            rankRewarded: 2,
            hoursPerPoint: 160,
            entryOR: 0.99 // Paradox: parity at 0-3 yrs!
        },
        dashboards: {
            name: "Storytelling & Dashboards",
            paidOR: 1.163,
            paidCI: [1.085, 1.247],
            rewardedOR: 3.507,
            rewardedCI: [1.794, 17.464],
            rankListed: 1,
            rankPaid: 5,
            rankRewarded: 3,
            hoursPerPoint: 80,
            entryOR: 1.08
        }
    },

    /**
     * Evaluates formal abstention and statistical warning conditions
     */
    evaluateAbstentions: function(scores, experienceYrs) {
        const warnings = [];
        let globalAbstain = false;

        // Global Gatekeeper: Coding < 2.0 (Kabir persona condition)
        if (scores.core_coding < 2.0) {
            globalAbstain = true;
            warnings.push({
                type: "CRITICAL_ABSTAIN",
                skill: "Core Coding",
                title: "FORMAL SYSTEM ABSTENTION: Foundation Deficit",
                message: `Current Core Coding rating (${scores.core_coding.toFixed(1)}/5.0) is below the minimum baseline required by employers (<2.0). All advanced investments in AI/ML or Big Data are withheld. Student must attain coding viability first before specialized portfolio optimization.`
            });
        }

        // Skill-specific warnings
        for (const [key, skillData] of Object.entries(this.skills)) {
            const score = scores[key] || 0;

            // Condition 1: CI crosses parity (1.0)
            if (skillData.rewardedCI[0] < 1.0) {
                warnings.push({
                    type: "CI_CROSS_PARITY",
                    skill: skillData.name,
                    title: "Statistical Ambiguity Alert",
                    message: `Internal promotion odds ratio 95% BCa CI [${skillData.rewardedCI[0].toFixed(2)}, ${skillData.rewardedCI[1].toFixed(2)}] crosses 1.0. Serves as baseline entry requirement (+12.5% salary premium), but does not differentiate internal promotion hikes.`
                });
            }

            // Condition 2: Premature specialisation for freshers in AI/ML
            if (key === "ai_ml" && experienceYrs < 1.0 && score < 3.0) {
                warnings.push({
                    type: "PREMATURE_SPECIALIZATION",
                    skill: skillData.name,
                    title: "Premature Specialisation Risk",
                    message: `At entry level (0-3 yrs), AI/ML exhibits odds ratio OR=0.99 [0.81, 1.22] within role family. Employers demand verified statistical foundation and software execution before theoretical AI modeling.`
                });
            }

            // Condition 3: Saturation limit (Meera condition)
            if (score >= 4.5) {
                warnings.push({
                    type: "SATURATION_LIMIT",
                    skill: skillData.name,
                    title: "Ceiling Saturation Limit",
                    message: `Proficiency is already at mastery (${score.toFixed(1)}/5.0). Marginal gain per study hour is minimal; further study yields diminishing returns.`
                });
            }
        }

        // Global Check: Near-ceiling across all skills (Meera)
        const allNearCeiling = Object.values(scores).every(s => s >= 4.5);
        if (allNearCeiling) {
            warnings.push({
                type: "FULL_SATURATION",
                skill: "Portfolio",
                title: "Optimal Profile Reached",
                message: "Candidate profile matches the median of high-hike juniors across all 5 dimensions. Human capital should pivot toward high-visibility domain projects and senior client management."
            });
        }

        return { warnings, globalAbstain };
    },

    /**
     * Solves the Knapsack Optimization for Human Capital Hours Allocation
     */
    optimizeAllocation: function(scores, experienceYrs, totalHours) {
        const { warnings, globalAbstain } = this.evaluateAbstentions(scores, experienceYrs);

        // If global abstention triggered (e.g., Kabir), mandate coding remediation
        if (globalAbstain) {
            const codingHours = Math.min(totalHours, (3.5 - scores.core_coding) * this.skills.core_coding.hoursPerPoint);
            const codingGain = codingHours / this.skills.core_coding.hoursPerPoint;
            
            return {
                isAbstained: true,
                warnings: warnings,
                totalBudget: totalHours,
                hoursUsed: codingHours,
                hoursRemaining: totalHours - codingHours,
                allocations: [
                    {
                        key: "core_coding",
                        name: "Core Coding (Mandated Remediation)",
                        startScore: scores.core_coding,
                        gain: codingGain,
                        projectedScore: scores.core_coding + codingGain,
                        hours: codingHours,
                        roiScore: 99.9,
                        externalORShift: Math.pow(this.skills.core_coding.paidOR, codingGain),
                        internalORShift: Math.pow(this.skills.core_coding.rewardedOR, codingGain),
                        status: "REMEDIATION_REQUIRED"
                    }
                ],
                synergyUnlocked: false,
                directive: "CRITICAL: Cease advanced modeling study immediately. Focus 100% of available hours on Python/SQL fundamentals, data structures, and debugging to cross the labor-market entry threshold."
            };
        }

        // Calculate ROI per skill
        const roiList = [];
        for (const [key, skillData] of Object.entries(this.skills)) {
            const score = scores[key] || 0;
            const headroom = Math.max(0.0, 5.0 - score);
            const cost = skillData.hoursPerPoint;

            // Composite career utility weight:
            // For freshers (<=2 yrs): 60% Paid, 40% Rewarded
            // For experienced (>2 yrs): 30% Paid, 70% Rewarded
            let compScore = (experienceYrs <= 2.0)
                ? (0.6 * Math.log(skillData.paidOR) + 0.4 * Math.log(skillData.rewardedOR))
                : (0.3 * Math.log(skillData.paidOR) + 0.7 * Math.log(skillData.rewardedOR));

            // Penalty if baseline coding is low (<2.5)
            if (key !== "core_coding" && scores.core_coding < 2.5) {
                compScore *= 0.5;
            }

            const roi = headroom > 0.05 ? (compScore / cost) : 0;
            roiList.push({
                key: key,
                skillData: skillData,
                score: score,
                headroom: headroom,
                cost: cost,
                roi: roi
            });
        }

        // Sort skills by ROI descending
        roiList.sort((a, b) => b.roi - a.roi);

        let remainingHours = totalHours;
        const allocations = [];

        for (const item of roiList) {
            if (item.headroom <= 0.1 || remainingHours <= 20 || item.roi <= 0) {
                allocations.push({
                    key: item.key,
                    name: item.skillData.name,
                    startScore: item.score,
                    gain: 0.0,
                    projectedScore: item.score,
                    hours: 0,
                    roiScore: item.roi,
                    externalORShift: 1.0,
                    internalORShift: 1.0,
                    status: item.headroom <= 0.1 ? "SATURATED" : "DE-PRIORITIZED"
                });
                continue;
            }

            // Allocate up to 1.5 points gain or headroom limit
            const desiredGain = Math.min(1.5, item.headroom);
            const hoursNeeded = desiredGain * item.cost;

            let allocatedHours = 0;
            let actualGain = 0;

            if (hoursNeeded <= remainingHours) {
                allocatedHours = Math.round(hoursNeeded);
                actualGain = desiredGain;
                remainingHours -= allocatedHours;
            } else {
                allocatedHours = remainingHours;
                actualGain = allocatedHours / item.cost;
                remainingHours = 0;
            }

            const projected = Math.min(5.0, item.score + actualGain);
            const extShift = Math.pow(item.skillData.paidOR, actualGain);
            const intShift = Math.pow(item.skillData.rewardedOR, actualGain);

            allocations.push({
                key: item.key,
                name: item.skillData.name,
                startScore: item.score,
                gain: actualGain,
                projectedScore: projected,
                hours: allocatedHours,
                roiScore: item.roi,
                externalORShift: extShift,
                internalORShift: intShift,
                status: actualGain > 0 ? "PRIORITY_ACTION" : "DE-PRIORITIZED"
            });
        }

        // Sort allocations back by hours allocated descending
        allocations.sort((a, b) => b.hours - a.hours);

        // Check Synergy Multiplier (High Coding + High Storytelling)
        const projCoding = allocations.find(a => a.key === "core_coding")?.projectedScore || scores.core_coding;
        const projStory = allocations.find(a => a.key === "dashboards")?.projectedScore || scores.dashboards;
        const synergyUnlocked = (projCoding >= 3.5 && projStory >= 3.5);

        // Career Stage Directive
        let directive = "";
        if (experienceYrs <= 2.0) {
            directive = "JUNIOR COHORT DIRECTIVE: Early-career velocity is strictly governed by verified quantitative rigor (Maths & Statistics) and executable coding pipelines. Focus on mathematical depth, reproducible pipelines, and interval regression premiums.";
        } else if (experienceYrs <= 5.0) {
            directive = "MID-LEVEL COHORT DIRECTIVE: Technical proficiency reaches market baseline. High hike differentiation requires pairing robust analytics with Storytelling & Dashboards to unlock the +2.18x executive visibility multiplier.";
        } else {
            directive = "SENIOR TRANSITION DIRECTIVE: SDS Diagnostic confirms technical scores plateau at senior ranks. Career progression hinges on Conscientiousness, stakeholder trust, and strategic cross-functional communication.";
        }

        return {
            isAbstained: false,
            warnings: warnings,
            totalBudget: totalHours,
            hoursUsed: totalHours - remainingHours,
            hoursRemaining: remainingHours,
            allocations: allocations,
            synergyUnlocked: synergyUnlocked,
            directive: directive
        };
    }
};

// Export to window
if (typeof window !== "undefined") {
    window.DecisionSimulator = DecisionSimulator;
}
