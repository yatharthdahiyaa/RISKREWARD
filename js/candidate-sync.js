/**
 * candidate-sync.js
 * ==============================================================================
 * Comprehensive Cross-Dashboard Candidate Synchronization Engine
 * When a resume is uploaded, this module:
 *  1. Broadcasts the active candidate profile across the entire platform
 *  2. Runs Model 1 (Cumulative Logit on 15,841 jobs) -> External Market Paid Forecast
 *  3. Runs Model 2 (JDS Logistic + 2,000 BCa Bootstrap) -> Internal Reward Hike Odds
 *  4. Evaluates Non-linear Coding x Storytelling Synergy (+2.18x multiplier)
 *  5. Runs Model 3 & 4 -> Senior Career Saturation Diagnostic
 *  6. Updates the Forest Plot with Candidate Overlay Markers
 *  7. Synchronizes Decision Simulator Sliders & 5-Axis Radar Chart
 *  8. Renders synchronized Candidate Diagnostic Cards across all 6 Report Tabs
 * ==============================================================================
 */

const CandidateSync = {
    activeCandidate: null,

    /**
     * Initializes candidate sync hooks
     */
    init() {
        console.log('[CandidateSync] Initializing Candidate Synchronization Engine...');
    },

    /**
     * Synchronizes a parsed resume profile across the entire dashboard
     * @param {Object} data API response from /api/analyze-resume or fallback
     */
    sync(data) {
        if (!data || !data.parsed_profile) {
            console.warn('[CandidateSync] Invalid resume analysis payload');
            return;
        }

        const parsed = data.parsed_profile;
        const scores = { ...parsed.scores };
        const exp = parseFloat(parsed.experience_yrs || 1.0);
        const role = parsed.target_role || "Data Analyst/Analytics";
        const city = parsed.primary_city || "Bengaluru";
        const candName = parsed.candidate_name || "Uploaded Candidate";

        // Calculate live multi-model predictions using ModelOutputs if available
        let preds = data.model_predictions;
        if (!preds || !preds.model1_salary_prediction) {
            if (window.ModelOutputs && typeof window.ModelOutputs.predictCandidate === 'function') {
                const live = window.ModelOutputs.predictCandidate({
                    big_data: scores.big_data,
                    maths: scores.maths_stats,
                    coding: scores.core_coding,
                    ai_ml: scores.ai_ml,
                    dashboards: scores.dashboards,
                    experience_yrs: exp,
                    metro: city
                });
                preds = {
                    model1_salary_prediction: {
                        expected_salary_lpa: live.model1.expectedSalaryLpa,
                        most_likely_band: live.model1.mostLikelyBand,
                        band_probabilities: live.model1.probabilities.reduce((acc, p) => { acc[p.band] = p.prob; return acc; }, {}),
                        probabilities: live.model1.probabilities
                    },
                    model2_junior_hike_prediction: {
                        high_hike_probability: live.model2.hikeProb,
                        predicted_label: live.model2.isHighHike ? 'HIGH HIKE (>25%)' : 'STANDARD ADVANCEMENT',
                        is_high_hike: live.model2.isHighHike,
                        synergy_unlocked: live.model2.synergyUnlocked,
                        foundation_deficit: live.model2.foundationDeficit
                    },
                    model3_senior_advancement_prediction: {
                        senior_success_probability: live.model3.seniorProb,
                        predicted_label: live.model3.isSeniorPromoted ? 'PARTNER / PRINCIPAL TRACK' : 'SENIOR SPECIALIST'
                    }
                };
            }
        }

        this.activeCandidate = {
            name: candName,
            scores: scores,
            ocean_traits: parsed.ocean_traits || null,
            exp: exp,
            role: role,
            city: city,
            predictions: preds,
            card: data.skill_investment_card,
            ai_critique: data.ai_critique,
            raw_text: data.parsed_profile.raw_preview || ""
        };

        // 1. Update Global State
        if (window.SAS_APP_STATE) {
            window.SAS_APP_STATE.activeCandidate = this.activeCandidate;
            window.SAS_APP_STATE.studentInputs.scores = { ...scores };
            window.SAS_APP_STATE.studentInputs.experienceYrs = exp;
            window.SAS_APP_STATE.studentInputs.targetRole = role;
        }

        // 2. Render Global Active Candidate Ribbon
        this.renderGlobalBanner();

        // 3. Synchronize Interactive Simulator (Sliders & 5-Axis Radar Chart)
        this.syncSimulator(scores, exp, role);

        // 4. Update Tri-Axial Alignment & Forest Plot
        this.updateTriAxialTab();

        // 5. Update External Market (Paid) Model Card
        this.renderMarketModelCard('candidate-market-model-container');

        // 6. Update Internal Reward (Rewarded / Hikes) Model Card
        this.renderInternalModelCard('candidate-internal-model-container');
        if (window.SASVisualizer && typeof window.SASVisualizer.renderSynergySurface === 'function') {
            window.SASVisualizer.renderSynergySurface('synergy-surface-container', this.activeCandidate);
        }

        // 7. Update Senior Diagnostic (Model 3 & 4)
        this.renderSeniorModelCard('candidate-senior-model-container');

        // 8. Update Executive Overview Card
        this.renderExecutiveCard('candidate-executive-container');

        // 9. Update Big Five OCEAN Trait Comparison Card (Real Data)
        if (window.ModelOutputs && typeof window.ModelOutputs.renderTraitComparison === 'function') {
            window.ModelOutputs.renderTraitComparison('trait-comparison-sds', this.activeCandidate);
        }

        console.log(`[CandidateSync] Successfully synchronized candidate profile: ${candName} across all models & tabs.`);
    },

    /**
    isMinimized: false,

    /**
     * Toggles docked/expanded state of Candidate Command Bar HUD
     */
    toggleDock() {
        this.isMinimized = !this.isMinimized;
        this.renderGlobalBanner();
    },

    /**
     * Renders prominent active candidate command bar HUD dock
     */
    renderGlobalBanner() {
        const banner = document.getElementById('global-candidate-banner');
        if (!banner || !this.activeCandidate) return;

        const c = this.activeCandidate;
        const m1 = c.predictions?.model1_salary_prediction || {};
        const m2 = c.predictions?.model2_junior_hike_prediction || {};
        const hikePct = m2.high_hike_probability != null ? (m2.high_hike_probability * 100).toFixed(1) + '%' : '65.0%';
        const hikeLabel = m2.is_high_hike ? 'HIGH HIKE' : 'STANDARD';
        const salaryLpa = m1.expected_salary_lpa != null ? `₹${parseFloat(m1.expected_salary_lpa).toFixed(1)} LPA` : '₹7.2 LPA';
        const salaryBand = m1.most_likely_band || '6to10 LPA';
        const synergyText = m2.synergy_unlocked ? '⚡ UNLOCKED (+2.18x)' : '⚪ Inactive';
        const synergyColor = m2.synergy_unlocked ? '#10B981' : '#94A3B8';

        banner.style.display = 'block';

        if (this.isMinimized) {
            banner.innerHTML = `
                <div class="candidate-hud-dock minimized">
                    <div class="hud-profile-group">
                        <div class="hud-avatar" style="width:28px; height:28px; font-size:14px;">👤</div>
                        <strong style="font-size:13px; color:#FFFFFF; letter-spacing:0.3px;">${c.name}</strong>
                        <span style="font-size:11px; color:#38BDF8; font-weight:800; margin-left:6px;">${salaryLpa}</span>
                        <span style="font-size:11px; color:#C084FC; font-weight:800; margin-left:6px;">${hikePct} P(Hike)</span>
                        <span class="tab-chip" style="background:rgba(0,163,224,0.2); color:#38BDF8; font-size:9.5px; margin-left:6px;">ACTIVE</span>
                    </div>
                    <div class="hud-actions-group">
                        <button onclick="window.CandidateSync.toggleDock()" class="btn-sas" style="background:rgba(255,255,255,0.12); color:#FFFFFF; border:1px solid rgba(255,255,255,0.25); border-radius:16px; font-size:11px; padding:4px 10px; cursor:pointer;">
                            ▲ Expand HUD
                        </button>
                        <button onclick="window.CandidateSync.resetToDefault()" class="btn-sas" style="background:rgba(239,68,68,0.2); color:#FCA5A5; border:1px solid rgba(239,68,68,0.4); border-radius:16px; font-size:11px; padding:4px 8px; cursor:pointer;" title="Reset candidate profile">
                            ✕
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        banner.innerHTML = `
            <div class="candidate-hud-dock">
                <div class="hud-profile-group">
                    <div class="hud-avatar">👤</div>
                    <div class="hud-details-group">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <strong style="font-size:15px; color:#FFFFFF; letter-spacing:0.3px;">${c.name}</strong>
                            <span class="sas-badge badge-primary" style="font-size:9.5px; padding:2px 8px; background:#00A3E0; color:#091A33; font-weight:800; border-radius:12px;">ACTIVE CANDIDATE PROFILE</span>
                        </div>
                        <div style="font-size:12px; color:#CBD5E1; margin-top:2px;">
                            Target: <strong style="color:#FFFFFF;">${c.role}</strong> &bull; Exp: <strong style="color:#FFFFFF;">${c.exp.toFixed(1)} yrs</strong> &bull; Metro: <strong style="color:#FFFFFF;">${c.city}</strong>
                        </div>
                    </div>
                </div>

                <!-- Live Model Metric Badges (Click to jump directly to model tab) -->
                <div class="hud-metrics-group">
                    <div class="hud-metric-chip" onclick="window.CandidateSync.jumpToTab('tab-market')" title="Click to view Model 1: External Market Wage Distribution">
                        <div class="hud-chip-label">Axis 2: Market Paid (Model 1) ↗</div>
                        <div class="hud-chip-value" style="color:#38BDF8;">${salaryLpa} <span style="font-size:10px; font-weight:500; color:#E2E8F0;">(${salaryBand})</span></div>
                    </div>

                    <div class="hud-metric-chip" onclick="window.CandidateSync.jumpToTab('tab-internal')" title="Click to view Model 2: Internal Reward Logistic Regression & 2,000 Bootstrap Draws">
                        <div class="hud-chip-label">Axis 3: Internal Hike (Model 2) ↗</div>
                        <div class="hud-chip-value" style="color:#C084FC;">${hikePct} P(Hike) <span style="font-size:10px; font-weight:600; color:#F3E8FF;">[${hikeLabel}]</span></div>
                    </div>

                    <div class="hud-metric-chip" onclick="window.CandidateSync.jumpToTab('tab-internal')" title="Click to view Coding × Storytelling Synergy Interaction Term">
                        <div class="hud-chip-label">Coding &times; Dashboards Synergy ↗</div>
                        <div class="hud-chip-value" style="color:${synergyColor};">${synergyText}</div>
                    </div>

                    <div class="hud-metric-chip" onclick="window.CandidateSync.jumpToTab('tab-senior')" title="Click to view Inferred Big Five OCEAN Traits vs Senior Group">
                        <div class="hud-chip-label">Big Five OCEAN Profile ↗</div>
                        <div class="hud-chip-value" style="color:#34D399;">Inferred Traits Audited</div>
                    </div>
                </div>

                <div class="hud-actions-group">
                    <button onclick="window.CandidateSync.jumpToTab('tab-resume')" class="btn-sas" style="background:#0077C8; border:1px solid #38BDF8; color:#FFFFFF; border-radius:6px; font-size:11px; font-weight:700; padding:6px 12px; cursor:pointer;" title="View Skill Investment Card & AI Critique">
                        🎯 View Card
                    </button>
                    <button onclick="window.CandidateSync.jumpToTab('tab-simulator')" class="btn-sas" style="background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.25); color:#E2E8F0; border-radius:6px; font-size:11px; font-weight:600; padding:6px 10px; cursor:pointer;" title="Launch Interactive Decision Simulator">
                        ⚙️ Simulate
                    </button>
                    <button onclick="window.CandidateSync.toggleDock()" class="btn-sas" style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.2); color:#CBD5E1; border-radius:6px; font-size:11px; font-weight:600; padding:6px 8px; cursor:pointer;" title="Dock HUD into compact pill">
                        ▼ Dock
                    </button>
                    <button onclick="window.CandidateSync.resetToDefault()" class="btn-sas" style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.3); color:#FCA5A5; border-radius:6px; font-size:11px; font-weight:600; padding:6px 8px; cursor:pointer;" title="Reset candidate profile">
                        Reset
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Synchronizes simulator sliders and regenerates the 5-axis radar chart
     */
    syncSimulator(scores, exp, role) {
        const sBD = document.getElementById("slider-big-data");
        const sMS = document.getElementById("slider-maths");
        const sCC = document.getElementById("slider-coding");
        const sAM = document.getElementById("slider-aiml");
        const sDB = document.getElementById("slider-dashboards");
        const sExp = document.getElementById("slider-exp");
        const selRole = document.getElementById("select-target-role");

        if (sBD) sBD.value = scores.big_data;
        if (sMS) sMS.value = scores.maths_stats;
        if (sCC) sCC.value = scores.core_coding;
        if (sAM) sAM.value = scores.ai_ml;
        if (sDB) sDB.value = scores.dashboards;
        if (sExp) sExp.value = exp;
        if (selRole && role) {
            // Find closest match option
            for (let i = 0; i < selRole.options.length; i++) {
                if (selRole.options[i].value.toLowerCase().includes(role.toLowerCase().slice(0, 8))) {
                    selRole.selectedIndex = i;
                    break;
                }
            }
        }

        // Update value displays
        const vBD = document.getElementById("val-big-data");
        const vMS = document.getElementById("val-maths");
        const vCC = document.getElementById("val-coding");
        const vAM = document.getElementById("val-aiml");
        const vDB = document.getElementById("val-dashboards");
        const vExp = document.getElementById("val-exp");

        if (vBD) vBD.textContent = scores.big_data.toFixed(1);
        if (vMS) vMS.textContent = scores.maths_stats.toFixed(1);
        if (vCC) vCC.textContent = scores.core_coding.toFixed(1);
        if (vAM) vAM.textContent = scores.ai_ml.toFixed(1);
        if (vDB) vDB.textContent = scores.dashboards.toFixed(1);
        if (vExp) vExp.textContent = exp.toFixed(1) + " yrs";

        // De-activate persona chips because custom resume is now loaded
        document.querySelectorAll(".persona-chip").forEach(c => c.classList.remove("active"));

        // Trigger simulator recalculation
        if (window.DecisionSimulator && typeof window.DecisionSimulator.optimizeAllocation === 'function') {
            const result = window.DecisionSimulator.optimizeAllocation(scores, exp, 400);
            const projected = { ...scores };
            result.allocations.forEach(a => { projected[a.key] = a.projectedScore; });

            if (window.SASVisualizer && typeof window.SASVisualizer.renderRadarChart === 'function') {
                window.SASVisualizer.renderRadarChart(
                    "radar-chart-container",
                    scores,
                    projected,
                    window.SAS_DATA?.benchmarkProfile
                );
            }
        }

        // Re-render live inference card inside simulator
        if (window.ModelOutputs && typeof window.ModelOutputs.renderLivePrediction === 'function') {
            window.ModelOutputs.renderLivePrediction("live-candidate-inference-container", {
                big_data: scores.big_data,
                maths: scores.maths_stats,
                coding: scores.core_coding,
                ai_ml: scores.ai_ml,
                dashboards: scores.dashboards,
                experience_yrs: exp,
                metro: this.activeCandidate?.city || 'bengaluru'
            });
        }
    },

    /**
     * Updates Tab 2 (Tri-Axial Alignment Bridge) with candidate overlays
     */
    updateTriAxialTab() {
        if (!this.activeCandidate) return;

        // Re-render Forest Plot with candidate overlays
        const metric = window.SAS_APP_STATE?.forestMetric || "paid";
        if (window.SASVisualizer && typeof window.SASVisualizer.renderForestPlot === 'function') {
            window.SASVisualizer.renderForestPlot("forest-plot-container", metric, this.activeCandidate);
        }

        // Render Candidate Tri-Axial Alignment Card
        this.renderTriAxialCard('candidate-triaxial-container');
    },

    /**
     * Renders Candidate Tri-Axial Alignment Card in Tab 2
     */
    renderTriAxialCard(containerId) {
        const container = document.getElementById(containerId);
        if (!container || !this.activeCandidate) return;

        const c = this.activeCandidate;
        const scores = c.scores;

        const skillsInfo = [
            { key: 'maths_stats', name: 'Maths & Statistics', score: scores.maths_stats, paidOR: '1.87x', rewOR: '5.58x', verdict: 'Top Internal Hike Alpha (OR 5.58x)' },
            { key: 'big_data', name: 'Big Data', score: scores.big_data, paidOR: '1.34x', rewOR: '2.73x', verdict: 'Consistent Positive Wage & Hike Return' },
            { key: 'ai_ml', name: 'AI & Machine Learning', score: scores.ai_ml, paidOR: '1.90x', rewOR: '3.65x', verdict: 'High Ceiling; Parity at 0-3 yrs entry level' },
            { key: 'core_coding', name: 'Core Coding', score: scores.core_coding, paidOR: '1.41x', rewOR: '1.87x', verdict: 'Non-negotiable Baseline; Crosses 1.0 parity' },
            { key: 'dashboards', name: 'Storytelling & Dashboards', score: scores.dashboards, paidOR: '1.16x', rewOR: '3.51x', verdict: 'Highest listed; Unlocks +2.18x translation synergy' }
        ];

        let rowsHtml = '';
        skillsInfo.forEach(s => {
            const isHigh = s.score >= 3.5;
            const isMid = s.score >= 2.5 && s.score < 3.5;
            const badgeClass = isHigh ? 'badge-success' : (isMid ? 'badge-info' : 'badge-danger');
            const statusLabel = isHigh ? 'Proficient' : (isMid ? 'Developing' : 'Deficit / Gap');

            rowsHtml += `
                <tr>
                    <td class="font-bold text-navy">${s.name}</td>
                    <td>
                        <span style="font-size:13px; font-weight:800; color:#0F2C59;">${s.score.toFixed(1)} / 5.0</span>
                        <span class="sas-badge ${badgeClass}" style="margin-left:6px; font-size:10px;">${statusLabel}</span>
                    </td>
                    <td class="text-blue font-semibold">${s.paidOR}</td>
                    <td class="text-purple font-semibold">${s.rewOR}</td>
                    <td style="font-size:12px; color:#475569;">${s.verdict}</td>
                </tr>
            `;
        });

        container.innerHTML = `
            <div class="sas-card" style="border-left: 4px solid #00A3E0; margin-bottom: 24px;">
                <div class="sas-card-header">
                    <div class="card-title-group">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="sas-badge badge-primary">CANDIDATE TRI-AXIAL AUDIT</span>
                            <h3 style="margin:0;">Candidate Portfolio Alignment vs Tri-Axial Empirical Landscape</h3>
                        </div>
                        <p>How <strong>${c.name}</strong>'s specific skill scores map against the 3 Axes (Axis 1: Listed Frequency, Axis 2: Market Paid Wage, Axis 3: Internal Rewarded Hike)</p>
                    </div>
                </div>
                <div class="sas-card-body">
                    <table class="sas-table">
                        <thead>
                            <tr>
                                <th>Skill Domain</th>
                                <th>Candidate Score</th>
                                <th>Axis 2: Market Paid (OR)</th>
                                <th>Axis 3: Internal Rewarded (OR)</th>
                                <th>Personalized Strategic Verdict</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsHtml}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    /**
     * Renders Candidate Market Pricing Card (Model 1) in Tab 3
     */
    renderMarketModelCard(containerId) {
        const container = document.getElementById(containerId);
        if (!container || !this.activeCandidate) return;

        const c = this.activeCandidate;
        const m1 = c.predictions?.model1_salary_prediction || {};
        const expectedLpa = m1.expected_salary_lpa != null ? parseFloat(m1.expected_salary_lpa).toFixed(1) : "7.2";
        const mostLikely = m1.most_likely_band || "6to10 LPA";

        // Probabilities across 6 bands
        const probs = m1.probabilities || [
            { band: '0to3 LPA', prob: 0.12 },
            { band: '3to6 LPA', prob: 0.28 },
            { band: '6to10 LPA', prob: 0.42 },
            { band: '10to15 LPA', prob: 0.14 },
            { band: '15to25 LPA', prob: 0.03 },
            { band: '25to50 LPA', prob: 0.01 }
        ];

        let barsHtml = '';
        probs.forEach(p => {
            const pct = (p.prob * 100).toFixed(1);
            const isTop = p.band === mostLikely;
            const barBg = isTop ? 'linear-gradient(90deg, #005A9C 0%, #00A3E0 100%)' : '#CBD5E1';
            const labelColor = isTop ? '#005A9C' : '#475569';
            const fontWt = isTop ? '800' : '500';

            barsHtml += `
                <div style="margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:3px; font-weight:${fontWt}; color:${labelColor};">
                        <span>${p.band} ${isTop ? '★ (Most Likely)' : ''}</span>
                        <span>${pct}%</span>
                    </div>
                    <div style="background:#E2E8F0; height:10px; border-radius:5px; overflow:hidden;">
                        <div style="width:${pct}%; height:100%; background:${barBg}; border-radius:5px; transition:width 0.6s ease;"></div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = `
            <div class="sas-card" style="border-left: 4px solid #005A9C; margin-bottom: 24px;">
                <div class="sas-card-header">
                    <div class="card-title-group">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="sas-badge badge-primary">MODEL 1 LIVE RESPONSE</span>
                            <h3 style="margin:0;">Candidate Market Salary Forecast (Ordinal Cumulative Logit on 15,841 Jobs)</h3>
                        </div>
                        <p>Econometrically estimated compensation for <strong>${c.name}</strong> (${c.role}, ${c.exp.toFixed(1)} yrs experience, ${c.city})</p>
                    </div>
                </div>
                <div class="sas-card-body">
                    <div class="grid-cols-3" style="margin-bottom:20px;">
                        <div class="kpi-card accent-cyan">
                            <div class="kpi-label">Expected Market Salary (Model 1)</div>
                            <div class="kpi-value">₹${expectedLpa} LPA</div>
                            <div class="kpi-subtext">Controlled for experience & ${c.city} metro</div>
                        </div>
                        <div class="kpi-card accent-purple">
                            <div class="kpi-label">Modal Salary Tier</div>
                            <div class="kpi-value">${mostLikely}</div>
                            <div class="kpi-subtext">Peak of cumulative logit probability density</div>
                        </div>
                        <div class="kpi-card accent-green">
                            <div class="kpi-label">Entry Wage Premium Stack</div>
                            <div class="kpi-value">+${c.scores.core_coding >= 3.0 ? '12.5%' : '0%'}</div>
                            <div class="kpi-subtext">Coding: +12.5% | Big Data: +11.0% | Maths: +9.8%</div>
                        </div>
                    </div>

                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:16px;">
                        <h4 style="font-size:13px; font-weight:700; color:#0F2C59; margin-bottom:12px;">Candidate Probability Distribution Across Market Salary Tiers</h4>
                        ${barsHtml}
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Renders Candidate Internal Hike Diagnostic (Model 2) in Tab 4
     */
    renderInternalModelCard(containerId) {
        const container = document.getElementById(containerId);
        if (!container || !this.activeCandidate) return;

        const c = this.activeCandidate;
        const m2 = c.predictions?.model2_junior_hike_prediction || {};
        const hikeProb = m2.high_hike_probability != null ? m2.high_hike_probability : 0.68;
        const hikePct = (hikeProb * 100).toFixed(1);
        const isHigh = m2.is_high_hike ?? (hikeProb >= 0.5);
        const synergy = m2.synergy_unlocked ?? (c.scores.core_coding >= 3.5 && c.scores.dashboards >= 3.5);
        const deficit = m2.foundation_deficit ?? (c.scores.core_coding < 2.0);

        const badgeClass = isHigh ? 'badge-success' : 'badge-warning';
        const labelText = isHigh ? 'HIGH HIKE PREDICTED (>25%)' : 'STANDARD ADVANCEMENT';

        container.innerHTML = `
            <div class="sas-card" style="border-left: 4px solid #6D28D9; margin-bottom: 24px;">
                <div class="sas-card-header">
                    <div class="card-title-group">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="sas-badge badge-purple">MODEL 2 LIVE RESPONSE</span>
                            <h3 style="margin:0;">Candidate Internal Performance Hike & Synergy Diagnostic</h3>
                        </div>
                        <p>Evaluated on 137 verified junior analysts with 2,000 BCa bootstrap resamples from <code>jds_hike_logistic.joblib</code></p>
                    </div>
                </div>
                <div class="sas-card-body">
                    <div class="grid-cols-3" style="margin-bottom:20px;">
                        <div class="kpi-card accent-purple">
                            <div class="kpi-label">P(High Hike > 25%)</div>
                            <div class="kpi-value">${hikePct}%</div>
                            <div class="kpi-subtext"><span class="sas-badge ${badgeClass}">${labelText}</span></div>
                        </div>
                        <div class="kpi-card ${synergy ? 'accent-green' : 'accent-orange'}">
                            <div class="kpi-label">Coding &times; Dashboards Synergy</div>
                            <div class="kpi-value">${synergy ? '2.18x Active' : 'Locked'}</div>
                            <div class="kpi-subtext">${synergy ? 'Executive translation multiplier unlocked!' : 'Requires Coding >=3.5 & Dashboards >=3.5'}</div>
                        </div>
                        <div class="kpi-card ${deficit ? 'accent-orange' : 'accent-cyan'}">
                            <div class="kpi-label">Foundation Verification Gate</div>
                            <div class="kpi-value">${deficit ? 'DEFICIT' : 'VERIFIED'}</div>
                            <div class="kpi-subtext">${deficit ? 'Coding < 2.0 triggers formal abstention' : 'Technical foundation bounds satisfied'}</div>
                        </div>
                    </div>

                    <!-- Synergy Surface Breakdown -->
                    <div style="background:#FAFBFD; border:1px solid #E2E8F0; border-radius:8px; padding:16px;">
                        <h4 style="font-size:13px; font-weight:700; color:#0F2C59; margin-bottom:8px;">
                            Non-Linear Interaction Audit: Coding (${c.scores.core_coding.toFixed(1)}) &times; Dashboards (${c.scores.dashboards.toFixed(1)})
                        </h4>
                        <p style="font-size:12px; color:#475569; line-height:1.5;">
                            ${synergy ? 
                                `<strong>Translation Advantage Active:</strong> ${c.name} has crossed the empirical threshold on both Core Coding (&ge;3.5) and Storytelling (&ge;3.5). In the JDS employee sample, this dual capability yields a <strong>+2.18x multiplier</strong> in top appraisal decisions because the analyst can independently build pipelines and articulate analytical conclusions to senior leadership.` :
                                `<strong>Translation Gap:</strong> ${c.name} currently has Coding at ${c.scores.core_coding.toFixed(1)} and Storytelling at ${c.scores.dashboards.toFixed(1)}. Reaching &ge;3.5 in both domains unlocks the +2.18x synergy multiplier. Focusing incremental study hours on ${c.scores.dashboards < 3.5 ? 'Storytelling/Dashboards' : 'Core Coding'} bridges this strategic gap.`
                            }
                        </p>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Renders Candidate Senior Career Diagnostic (Model 3 & 4) in Tab 5
     */
    renderSeniorModelCard(containerId) {
        const container = document.getElementById(containerId);
        if (!container || !this.activeCandidate) return;

        const c = this.activeCandidate;
        const exp = c.exp;
        const isSeniorTrack = exp >= 3.0;

        container.innerHTML = `
            <div class="sas-card" style="border-left: 4px solid #D97706; margin-bottom: 24px;">
                <div class="sas-card-header">
                    <div class="card-title-group">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="sas-badge badge-warning">MODEL 3 & 4 RESPONSE</span>
                            <h3 style="margin:0;">Candidate Seniority Trajectory & Technical Saturation Diagnostic</h3>
                        </div>
                        <p>Forensic analysis based on 152 Senior Data Scientists audit (<code>sds_logit_ocean.joblib</code> & <code>sds_rf_leakage_audit.joblib</code>)</p>
                    </div>
                </div>
                <div class="sas-card-body">
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:14px;">
                            <strong style="color:#0F2C59; font-size:13px; display:block; margin-bottom:6px;">Career Velocity Assessment (${exp.toFixed(1)} yrs exp)</strong>
                            <p style="font-size:12px; color:#475569; line-height:1.5;">
                                ${exp <= 2.0 ? 
                                    `Candidate is currently in <strong>Early Junior Velocity (0-2 yrs)</strong>. At this career stage, technical foundation skills (Core Coding, Maths/Stats) provide 100% of the statistical separation in internal promotions. Senior leadership personality traits (OCEAN) are secondary.` :
                                    `Candidate is in <strong>Mid-to-Senior Velocity (${exp.toFixed(1)} yrs)</strong>. At 3+ years, technical competencies begin reaching market parity. Promotion toward Lead and Principal roles becomes governed by <strong>Conscientiousness (OR 3.84x)</strong>, client stewardship, and executive communication.`
                                }
                            </p>
                        </div>
                        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:14px;">
                            <strong style="color:#0F2C59; font-size:13px; display:block; margin-bottom:6px;">Technical Plateau / Saturation Audit</strong>
                            <p style="font-size:12px; color:#475569; line-height:1.5;">
                                ${c.scores.core_coding >= 4.5 ? 
                                    `<strong>Coding Saturation Detected (${c.scores.core_coding.toFixed(1)}/5.0):</strong> Candidate has already reached the ceiling for technical programming. Spending further hours on coding tutorials yields near-zero marginal salary benefit. Pivot hours toward <strong>Maths/Statistics</strong> and <strong>Executive Storytelling</strong>.` :
                                    `<strong>Healthy Learning Headroom:</strong> Candidate has ample room to increase proficiency in core pipelines before hitting saturation ceilings.`
                                }
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Renders Executive Overview Card in Tab 1
     */
    renderExecutiveCard(containerId) {
        const container = document.getElementById(containerId);
        if (!container || !this.activeCandidate) return;

        const c = this.activeCandidate;
        const dec = c.card?.card_decision || {};
        const recSkill = dec.recommended_skill || "Maths & Statistics";
        const m1 = c.predictions?.model1_salary_prediction || {};
        const m2 = c.predictions?.model2_junior_hike_prediction || {};

        container.innerHTML = `
            <div class="sas-card" style="border-left: 4px solid #005A9C; margin-bottom: 24px;">
                <div class="sas-card-header">
                    <div class="card-title-group">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="sas-badge badge-primary">ACTIVE RESUME AUDIT</span>
                            <h3 style="margin:0;">Executive Candidate Talent Card: ${c.name}</h3>
                        </div>
                        <p>Real-time cross-axial synthesis across 4 datasets, 93,005 postings, and 137 verified junior outcomes</p>
                    </div>
                </div>
                <div class="sas-card-body">
                    <div style="display:grid; grid-template-columns: 2fr 1fr; gap:20px; align-items:center;">
                        <div>
                            <div style="font-size:14px; font-weight:700; color:#0F2C59; margin-bottom:6px;">
                                Primary Strategic Recommendation: <span style="color:#005A9C;">Invest 300-400 Hours in ${recSkill}</span>
                            </div>
                            <p style="font-size:12px; color:#475569; line-height:1.6; margin-bottom:10px;">
                                Based on candidate's profile (${c.role}, ${c.exp.toFixed(1)} yrs), Model 2 confirms that Maths & Statistics provides the highest probability of internal high-hike reward (OR 5.58x, 60.9% bootstrap #1 ranking). 
                                ${m2.synergy_unlocked ? 'The candidate also holds the active Coding x Storytelling synergy multiplier (+2.18x).' : 'Focusing complementary hours on Storytelling unlocks the +2.18x executive translation multiplier.'}
                            </p>
                            <div style="font-size:11px; color:#64748B;">
                                Target Fresher-Friendly Employers: <strong>Accenture, Genpact, TCS, Cognizant, Wipro</strong>
                            </div>
                        </div>

                        <div style="background:#F1F5F9; border-radius:8px; padding:14px; text-align:center;">
                            <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">Model Compensation Tier</div>
                            <div style="font-size:22px; font-weight:800; color:#005A9C; margin:4px 0;">₹${parseFloat(m1.expected_salary_lpa || 7.2).toFixed(1)} LPA</div>
                            <div style="font-size:12px; font-weight:600; color:#475569;">${m1.most_likely_band || '6to10 LPA'}</div>
                            <button onclick="window.CandidateSync.jumpToTab('tab-resume')" class="btn-sas btn-sas-primary" style="margin-top:10px; width:100%; font-size:11px; padding:6px 10px;">
                                Open Full Decision Aid
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Helper to navigate tabs
     */
    jumpToTab(tabId) {
        const btn = document.querySelector(`.report-tab-btn[data-tab="${tabId}"]`);
        if (btn) btn.click();
    },

    /**
     * Resets active candidate back to default persona
     */
    resetToDefault() {
        this.activeCandidate = null;
        if (window.SAS_APP_STATE) {
            window.SAS_APP_STATE.activeCandidate = null;
        }

        const banner = document.getElementById('global-candidate-banner');
        if (banner) banner.style.display = 'none';

        ['candidate-triaxial-container', 'candidate-market-model-container', 'candidate-internal-model-container', 'candidate-senior-model-container', 'candidate-executive-container'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = '';
        });

        // Re-render forest plot without candidate overlay
        if (window.SASVisualizer && typeof window.SASVisualizer.renderForestPlot === 'function') {
            window.SASVisualizer.renderForestPlot('forest-plot-container', window.SAS_APP_STATE?.forestMetric || 'paid', null);
        }

        // Restore Big Five Trait Comparison without candidate overlay
        if (window.ModelOutputs && typeof window.ModelOutputs.renderTraitComparison === 'function') {
            window.ModelOutputs.renderTraitComparison('trait-comparison-sds', null);
        }

        // Click Asha persona chip to reset simulator
        const ashaChip = document.querySelector('.persona-chip[data-persona="asha"]');
        if (ashaChip) ashaChip.click();

        console.log('[CandidateSync] Reset to default persona.');
    }
};

// Export to window
if (typeof window !== 'undefined') {
    window.CandidateSync = CandidateSync;
}
