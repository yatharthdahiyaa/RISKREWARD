/**
 * charts.js
 * High-Precision SVG & Canvas Data Visualizations for SAS Viya Visual Analytics
 * Renders:
 * 1. Multi-Profile Radar Chart (Current vs Projected vs High-Hike Benchmark)
 * 2. Tri-Axial Alignment Forest Plot (Odds Ratios with 95% Confidence Intervals)
 * 3. Salary Band Ordinal Waterfall & Experience Distribution
 * 4. Coding x Storytelling Synergy Matrix
 */

const SASVisualizer = {
    /**
     * Renders an interactive 5-axis SVG Radar Chart
     */
    renderRadarChart: function(containerId, currentScores, projectedScores, benchmarkScores) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const width = 460;
        const height = 400;
        const cx = width / 2;
        const cy = height / 2 + 10;
        const radius = 135;

        const skills = [
            { key: 'big_data', label: 'Big Data' },
            { key: 'maths_stats', label: 'Maths-Stats' },
            { key: 'core_coding', label: 'Core Coding' },
            { key: 'ai_ml', label: 'AI & ML' },
            { key: 'dashboards', label: 'Storytelling' }
        ];

        const totalAxes = skills.length;
        const angleStep = (Math.PI * 2) / totalAxes;

        // Compute coordinate for given axis and value (0 to 5)
        function getCoords(index, val) {
            const angle = index * angleStep - Math.PI / 2;
            const r = (val / 5.0) * radius;
            return {
                x: cx + r * Math.cos(angle),
                y: cy + r * Math.sin(angle)
            };
        }

        let svg = `<svg viewBox="0 0 ${width} ${height}" class="radar-svg" style="width:100%; height:auto; overflow:visible;">`;

        // Background Web Circles (1 to 5)
        for (let level = 1; level <= 5; level++) {
            let pts = [];
            for (let i = 0; i < totalAxes; i++) {
                const c = getCoords(i, level);
                pts.push(`${c.x},${c.y}`);
            }
            svg += `<polygon points="${pts.join(' ')}" fill="none" stroke="#D1D9E6" stroke-width="${level === 5 ? 1.5 : 1}" stroke-dasharray="${level === 5 ? 'none' : '3,3'}" />`;
            // Level label
            svg += `<text x="${cx + 6}" y="${cy - (level / 5.0) * radius + 4}" fill="#718096" font-size="10" font-family="'Segoe UI', sans-serif">${level}.0</text>`;
        }

        // Radial Spokes & Axis Labels
        for (let i = 0; i < totalAxes; i++) {
            const end = getCoords(i, 5.0);
            svg += `<line x1="${cx}" y1="${cy}" x2="${end.x}" y2="${end.y}" stroke="#CBD5E0" stroke-width="1.2" />`;

            // Label Position
            const labelAngle = i * angleStep - Math.PI / 2;
            const labelR = radius + 28;
            const lx = cx + labelR * Math.cos(labelAngle);
            const ly = cy + labelR * Math.sin(labelAngle) + 4;
            const anchor = Math.abs(Math.cos(labelAngle)) < 0.2 ? 'middle' : (Math.cos(labelAngle) > 0 ? 'start' : 'end');

            svg += `<text x="${lx}" y="${ly}" text-anchor="${anchor}" fill="#1A365D" font-size="12" font-weight="600" font-family="'Segoe UI', sans-serif">${skills[i].label}</text>`;
        }

        // Polygon 1: High-Hike Benchmark (dashed gray / blue)
        if (benchmarkScores) {
            let benchPts = [];
            for (let i = 0; i < totalAxes; i++) {
                const k = skills[i].key;
                const val = benchmarkScores[k] || 5.0;
                const c = getCoords(i, val);
                benchPts.push(`${c.x},${c.y}`);
            }
            svg += `<polygon points="${benchPts.join(' ')}" fill="rgba(160, 174, 192, 0.15)" stroke="#718096" stroke-width="2" stroke-dasharray="5,4" />`;
        }

        // Polygon 2: Current Proficiency (Solid SAS Light Blue)
        let currPts = [];
        for (let i = 0; i < totalAxes; i++) {
            const k = skills[i].key;
            const val = currentScores[k] || 1.0;
            const c = getCoords(i, val);
            currPts.push(`${c.x},${c.y}`);
        }
        svg += `<polygon points="${currPts.join(' ')}" fill="rgba(0, 90, 156, 0.22)" stroke="#005A9C" stroke-width="2.5" />`;

        // Points for Current
        for (let i = 0; i < totalAxes; i++) {
            const k = skills[i].key;
            const val = currentScores[k] || 1.0;
            const c = getCoords(i, val);
            svg += `<circle cx="${c.x}" cy="${c.y}" r="4" fill="#005A9C" stroke="#FFFFFF" stroke-width="1.5" />`;
        }

        // Polygon 3: Projected Proficiency after Allocation (Vibrant Amber / Emerald)
        if (projectedScores) {
            let projPts = [];
            for (let i = 0; i < totalAxes; i++) {
                const k = skills[i].key;
                const val = projectedScores[k] || currentScores[k] || 1.0;
                const c = getCoords(i, val);
                projPts.push(`${c.x},${c.y}`);
            }
            svg += `<polygon points="${projPts.join(' ')}" fill="rgba(0, 163, 224, 0.3)" stroke="#00A3E0" stroke-width="3" />`;

            // Points for Projected
            for (let i = 0; i < totalAxes; i++) {
                const k = skills[i].key;
                const val = projectedScores[k] || currentScores[k] || 1.0;
                const c = getCoords(i, val);
                svg += `<circle cx="${c.x}" cy="${c.y}" r="5" fill="#FF6A13" stroke="#FFFFFF" stroke-width="2" />`;
                svg += `<text x="${c.x + 8}" y="${c.y - 6}" fill="#D94E00" font-size="11" font-weight="bold">${val.toFixed(1)}</text>`;
            }
        }

        svg += `</svg>`;

        // Radar Legend
        const legend = `
            <div class="radar-legend" style="display:flex; justify-content:center; gap:16px; margin-top:8px; font-size:12px; flex-wrap:wrap;">
                <span style="display:inline-flex; align-items:center; gap:6px;">
                    <span style="width:14px; height:14px; background:rgba(0, 90, 156, 0.5); border:2px solid #005A9C; border-radius:3px;"></span>
                    Current Baseline
                </span>
                <span style="display:inline-flex; align-items:center; gap:6px;">
                    <span style="width:14px; height:14px; background:rgba(0, 163, 224, 0.5); border:2px solid #00A3E0; border-radius:3px;"></span>
                    Projected (+6 Mo)
                </span>
                <span style="display:inline-flex; align-items:center; gap:6px;">
                    <span style="width:14px; height:2px; border-top:2px dashed #718096;"></span>
                    High-Hike Benchmark (Median)
                </span>
            </div>
        `;

        container.innerHTML = svg + legend;
    },

    /**
     * Renders Enterprise SVG Forest Plot with Confidence Intervals, Whiskers, and Popover Tooltips
     */
    renderForestPlot: function(containerId, metricType = "paid", candidateData = null) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const candidate = candidateData || window.SAS_APP_STATE?.activeCandidate;
        const data = SAS_DATA.triAxial;
        const width = 820;
        const rowHeight = 52;
        const height = data.length * rowHeight + 105;
        const margin = { top: 45, right: 150, bottom: 50, left: 200 };

        const isPaid = metricType === "paid";
        const maxVal = isPaid ? 2.6 : 24.0;
        const minVal = isPaid ? 0.7 : 0.6;

        function xPos(val) {
            const logMin = Math.log(minVal);
            const logMax = Math.log(maxVal);
            const logVal = Math.log(Math.max(minVal, Math.min(maxVal, val)));
            const plotWidth = width - margin.left - margin.right;
            return margin.left + ((logVal - logMin) / (logMax - logMin)) * plotWidth;
        }

        let svg = `<svg id="forest-plot-svg" viewBox="0 0 ${width} ${height}" style="width:100%; height:auto; font-family:Inter, sans-serif;">`;

        // Subtle background grid
        const ticks = isPaid ? [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.4] : [0.8, 1.0, 2.0, 3.5, 5.5, 10.0, 20.0];
        ticks.forEach(t => {
            const tx = xPos(t);
            svg += `<line x1="${tx}" y1="${margin.top}" x2="${tx}" y2="${height - margin.bottom}" stroke="var(--border-light, #E2E8F0)" stroke-dasharray="2,2" opacity="0.6" />`;
            svg += `<line x1="${tx}" y1="${height - margin.bottom}" x2="${tx}" y2="${height - margin.bottom + 6}" stroke="var(--text-muted, #94A3B8)" />`;
            svg += `<text x="${tx}" y="${height - margin.bottom + 20}" text-anchor="middle" fill="var(--text-muted, #718096)" font-size="10.5" font-weight="600">${t}x</text>`;
        });

        // Parity Line (Odds Ratio = 1.0)
        const parityX = xPos(1.0);
        svg += `<line x1="${parityX}" y1="${margin.top}" x2="${parityX}" y2="${height - margin.bottom}" stroke="#EF4444" stroke-width="2" stroke-dasharray="4,4" />`;
        svg += `<rect x="${parityX - 48}" y="${margin.top - 22}" width="96" height="18" rx="4" fill="rgba(239, 68, 68, 0.15)" stroke="#EF4444" stroke-width="1" />`;
        svg += `<text x="${parityX}" y="${margin.top - 9}" text-anchor="middle" fill="#EF4444" font-size="10" font-weight="800">PARITY (OR = 1.0)</text>`;

        // Rows for each skill
        data.forEach((item, idx) => {
            const y = margin.top + idx * rowHeight + 24;
            const or = isPaid ? item.paidOR : item.rewardedOR;
            const ciLow = isPaid ? item.paidCILower : item.rewardedCILower;
            const ciHigh = isPaid ? item.paidCIUpper : item.rewardedCIUpper;

            const crossesParity = ciLow <= 1.0 && ciHigh >= 1.0;
            const isSignificant = !crossesParity;

            const xOR = xPos(or);
            const xLow = xPos(ciLow);
            const xHigh = xPos(ciHigh);

            // Whisker and diamond styling
            const whiskerColor = isPaid 
                ? (isSignificant ? "var(--sas-cyan-accent, #00A3E0)" : "#94A3B8")
                : (isSignificant ? "#8B5CF6" : "#94A3B8");

            const diamondColor = isPaid
                ? (isSignificant ? "#0077C8" : "#64748B")
                : (isSignificant ? "#6D28D9" : "#64748B");

            // Descriptions for hover tooltip
            const desc = isPaid
                ? (item.id === 'core_coding' ? "Python & SQL proficiency yields +12.5% entry salary separation controlling for experience and metro location." :
                   item.id === 'big_data' ? "Distributed computing capabilities (PySpark, Snowflake) generate +11.0% market premium across all 3 crosswalk regimes." :
                   item.id === 'maths_stats' ? "Solid statistical and econometric depth adds +9.8% entry premium, holding all role family controls constant." :
                   item.id === 'ai_ml' ? "At entry level (0-3 yrs), AI skills demonstrate parity (OR = 0.99 [0.81, 1.22]) within the same job family." :
                   "Tableau and Power BI pay +14.2% (OR 1.61), whereas basic standalone Excel spreadsheets incur an entry discount.")
                : (item.id === 'maths_stats' ? "Decisive #1 predictor of promotion velocity (OR = 5.58x, p < 0.001), capturing 60.9% of all 2,000 bootstrap draws." :
                   item.id === 'ai_ml' ? "Strong internal promotion velocity (OR = 3.65x) when grounded with foundational coding fluency." :
                   item.id === 'dashboards' ? "Executive stakeholder visibility driver (OR = 3.51x); unlocks +2.18x synergy when paired with coding." :
                   item.id === 'big_data' ? "Solid internal advancement driver (OR = 2.73x) across enterprise cloud analytics architectures." :
                   "Confidence interval crosses 1.0 parity (OR = 1.87x [0.94, 4.72]) because entry analysts are already at the proficiency ceiling (median 5.0).");

            const pVal = isPaid 
                ? (item.id === 'ai_ml' ? "p = 0.91 (Parity)" : "p < 0.001 (Significant)")
                : (item.id === 'core_coding' ? "p = 0.065 (Crosses 1.0)" : "p < 0.001 (Significant)");

            svg += `
                <g class="forest-row-group" 
                   data-skill="${encodeURIComponent(item.name)}"
                   data-or="${or.toFixed(2)}x"
                   data-cilow="${ciLow.toFixed(2)}"
                   data-cihigh="${ciHigh.toFixed(2)}"
                   data-axis="${isPaid ? 'Axis 2: Market Paid (Salary)' : 'Axis 3: Internal Rewarded (Hikes)'}"
                   data-pval="${encodeURIComponent(pVal)}"
                   data-desc="${encodeURIComponent(desc)}">
                    
                    <!-- Background hover highlight band -->
                    <rect x="10" y="${y - 18}" width="${width - 20}" height="${rowHeight - 6}" rx="6" fill="rgba(0, 119, 200, 0.04)" class="forest-row-hover-bg" />

                    <!-- Skill Name Label -->
                    <text x="${margin.left - 16}" y="${y + 2}" text-anchor="end" fill="var(--text-primary, #0F2C59)" font-size="12.5" font-weight="700">
                        ${item.name}
                    </text>
                    <text x="${margin.left - 16}" y="${y + 14}" text-anchor="end" fill="var(--text-muted, #64748B)" font-size="9.5">
                        ${isSignificant ? '✓ Significant (p < 0.05)' : '○ Parity / Baseline'}
                    </text>

                    <!-- Confidence Interval Horizontal Whisker Line -->
                    <line x1="${xLow}" y1="${y}" x2="${xHigh}" y2="${y}" stroke="${whiskerColor}" stroke-width="3" stroke-linecap="round" class="whisker-line" />

                    <!-- Whisker End Caps -->
                    <line x1="${xLow}" y1="${y - 6}" x2="${xLow}" y2="${y + 6}" stroke="${whiskerColor}" stroke-width="2.5" />
                    <line x1="${xHigh}" y1="${y - 6}" x2="${xHigh}" y2="${y + 6}" stroke="${whiskerColor}" stroke-width="2.5" />

                    <!-- Center Point Estimate Marker (Diamond) -->
                    <polygon points="${xOR},${y - 6} ${xOR + 6},${y} ${xOR},${y + 6} ${xOR - 6},${y}" 
                             fill="${diamondColor}" stroke="#FFFFFF" stroke-width="1.5" class="point-marker" />

                    <!-- Text value and confidence interval -->
                    <text x="${xHigh + 12}" y="${y + 4}" fill="var(--text-primary, #1E293B)" font-size="11" font-weight="700">
                        ${or.toFixed(2)}x <tspan font-weight="500" fill="var(--text-muted, #64748B)">[${ciLow.toFixed(2)}, ${ciHigh.toFixed(2)}]</tspan>
                    </text>
            `;

            // Candidate Overlay if active
            if (candidate && candidate.scores) {
                const cScore = candidate.scores[item.id] ?? 3.0;
                let candORPos = or;
                if (!isPaid) {
                    candORPos = Math.max(minVal, Math.min(maxVal, Math.pow(or, (cScore - 1.0) / 3.0)));
                } else {
                    candORPos = cScore >= 3.0 ? or : 1.0;
                }
                const candX = xPos(candORPos);
                svg += `
                    <circle cx="${candX}" cy="${y}" r="6" fill="#F59E0B" stroke="#78350F" stroke-width="2" class="candidate-marker" />
                `;
            }

            svg += `</g>`;
        });

        // Legend
        svg += `
            <g transform="translate(${margin.left}, ${height - 12})">
                <polygon points="6,-4 11,0 6,4 1,0" fill="${isPaid ? '#0077C8' : '#8B5CF6'}" stroke="#FFFFFF" stroke-width="1" />
                <text x="16" y="3" fill="var(--text-secondary, #475569)" font-size="10.5" font-weight="600">Model Point Estimate (OR)</text>

                <line x1="180" y1="0" x2="210" y2="0" stroke="var(--sas-cyan-accent, #00A3E0)" stroke-width="2.5" />
                <line x1="180" y1="-4" x2="180" y2="4" stroke="var(--sas-cyan-accent, #00A3E0)" stroke-width="2" />
                <line x1="210" y1="-4" x2="210" y2="4" stroke="var(--sas-cyan-accent, #00A3E0)" stroke-width="2" />
                <text x="218" y="3" fill="var(--text-secondary, #475569)" font-size="10.5" font-weight="600">95% Confidence Interval (BCa / Likelihood)</text>

                <line x1="470" y1="0" x2="495" y2="0" stroke="#EF4444" stroke-width="2" stroke-dasharray="3,3" />
                <text x="502" y="3" fill="#EF4444" font-size="10.5" font-weight="700">Null Parity (OR = 1.0)</text>
            </g>
        `;

        if (candidate) {
            svg += `
                <g transform="translate(${width - margin.right}, ${height - 12})">
                    <circle cx="-6" cy="0" r="5" fill="#F59E0B" stroke="#78350F" stroke-width="1.5" />
                    <text x="4" y="3" fill="var(--text-primary, #1E293B)" font-size="10.5" font-weight="700">${candidate.name || 'Candidate'} Overlay</text>
                </g>
            `;
        }

        svg += `</svg>`;
        container.innerHTML = svg;
        this.attachForestHoverListeners(container);
    },

    attachForestHoverListeners: function(container) {
        let tooltip = document.getElementById('forest-popover-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'forest-popover-tooltip';
            tooltip.className = 'forest-popover-card';
            tooltip.style.display = 'none';
            document.body.appendChild(tooltip);
        }

        const rows = container.querySelectorAll('.forest-row-group');
        rows.forEach(row => {
            row.addEventListener('mouseenter', (e) => {
                const skill = decodeURIComponent(row.getAttribute('data-skill') || '');
                const or = row.getAttribute('data-or') || '';
                const ciLow = row.getAttribute('data-cilow') || '';
                const ciHigh = row.getAttribute('data-cihigh') || '';
                const axis = row.getAttribute('data-axis') || '';
                const pval = decodeURIComponent(row.getAttribute('data-pval') || '');
                const desc = decodeURIComponent(row.getAttribute('data-desc') || '');

                tooltip.innerHTML = `
                    <div style="font-size:10px; font-weight:800; color:var(--sas-cyan-accent, #00A3E0); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">
                        ${axis}
                    </div>
                    <div style="font-size:14px; font-weight:800; color:var(--text-primary); margin-bottom:6px;">
                        ${skill}
                    </div>
                    <div style="display:flex; justify-content:space-between; background:rgba(0,0,0,0.06); padding:6px 8px; border-radius:4px; font-size:11.5px; margin-bottom:6px;">
                        <span>Odds Ratio: <strong style="color:var(--sas-blue-primary, #005A9C);">${or}</strong></span>
                        <span>95% CI: <strong>[${ciLow}, ${ciHigh}]</strong></span>
                    </div>
                    <div style="font-size:11px; font-weight:700; color:#059669; margin-bottom:4px;">
                        Stat: ${pval}
                    </div>
                    <div style="font-size:11.5px; color:var(--text-secondary); line-height:1.45;">
                        ${desc}
                    </div>
                `;
                tooltip.style.display = 'block';
                this.positionTooltip(e, tooltip);
            });

            row.addEventListener('mousemove', (e) => {
                this.positionTooltip(e, tooltip);
            });

            row.addEventListener('mouseleave', () => {
                tooltip.style.display = 'none';
            });
        });
    },

    positionTooltip: function(e, tooltip) {
        const x = Math.min(window.innerWidth - 340, e.clientX + 16);
        const y = Math.max(10, e.clientY - 40);
        tooltip.style.left = `${x}px`;
        tooltip.style.top = `${y}px`;
    },

    /**
     * Renders Interactive 2D Skill Synergy Surface (Coding x Storytelling Heatmap)
     */
    renderSynergySurface: function(containerId, candidateData = null) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const candidate = candidateData || window.SAS_APP_STATE?.activeCandidate;
        const candCoding = candidate?.scores?.core_coding ?? 3.5;
        const candStory = candidate?.scores?.dashboards ?? 3.0;

        const steps = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0];
        const cellSize = 42;
        const width = 520;
        const height = 480;
        const margin = { top: 40, right: 30, bottom: 65, left: 75 };

        function computeHikeProb(coding, story) {
            const isSynergy = (coding >= 3.5 && story >= 3.5);
            const zCoding = (coding - 2.5) / 1.1;
            const zStory = (story - 2.5) / 1.1;
            let logit = -1.20 + (0.55 * zCoding) + (0.75 * zStory);
            if (isSynergy) {
                logit += 0.425 * (zCoding * zStory) + 0.65;
            }
            const p = 1 / (1 + Math.exp(-logit));
            return Math.min(0.96, Math.max(0.08, p));
        }

        function getColor(prob) {
            if (prob < 0.25) return "#0F2C59";
            if (prob < 0.40) return "#1E40AF";
            if (prob < 0.55) return "#0284C7";
            if (prob < 0.70) return "#059669";
            if (prob < 0.85) return "#10B981";
            return "#F59E0B";
        }

        let svg = `<svg id="synergy-surface-svg" viewBox="0 0 ${width} ${height}" style="width:100%; max-width:520px; height:auto; font-family:Inter, sans-serif;">`;

        // Title and Axis headers
        svg += `
            <text x="${width / 2}" y="20" text-anchor="middle" fill="var(--text-primary, #0F2C59)" font-size="12.5" font-weight="800">
                P(High Promotion Hike &gt; 25%) Response Surface
            </text>
        `;

        // Draw Cells (Y goes from 5.0 down to 1.0, X goes from 1.0 to 5.0)
        steps.slice().reverse().forEach((sVal, rIdx) => {
            const y = margin.top + rIdx * cellSize;

            // Y-Axis label
            svg += `<text x="${margin.left - 10}" y="${y + cellSize / 2 + 4}" text-anchor="end" fill="var(--text-primary, #1E293B)" font-size="11" font-weight="600">${sVal.toFixed(1)}</text>`;

            steps.forEach((cVal, cIdx) => {
                const x = margin.left + cIdx * cellSize;
                const prob = computeHikeProb(cVal, sVal);
                const color = getColor(prob);
                const isSynergy = (cVal >= 3.5 && sVal >= 3.5);

                svg += `
                    <g class="synergy-grid-cell"
                       data-coding="${cVal.toFixed(1)}"
                       data-story="${sVal.toFixed(1)}"
                       data-prob="${(prob * 100).toFixed(1)}%"
                       data-synergy="${isSynergy ? 'UNLOCKED (+2.18x)' : 'LOCKED'}">
                        <rect x="${x}" y="${y}" width="${cellSize - 2}" height="${cellSize - 2}" rx="4" fill="${color}" />
                        <text x="${x + cellSize / 2 - 1}" y="${y + cellSize / 2 + 4}" fill="#FFFFFF" font-size="10" font-weight="700" text-anchor="middle">
                            ${(prob * 100).toFixed(0)}%
                        </text>
                    </g>
                `;
            });
        });

        // X-Axis labels
        steps.forEach((cVal, cIdx) => {
            const x = margin.left + cIdx * cellSize;
            svg += `<text x="${x + cellSize / 2 - 1}" y="${margin.top + steps.length * cellSize + 18}" text-anchor="middle" fill="var(--text-primary, #1E293B)" font-size="11" font-weight="600">${cVal.toFixed(1)}</text>`;
        });

        // Axis Titles
        svg += `
            <text x="${margin.left + (steps.length * cellSize) / 2}" y="${height - 20}" text-anchor="middle" fill="var(--text-primary, #0F2C59)" font-size="12" font-weight="700">
                Core Coding Proficiency &rarr;
            </text>
            <text x="18" y="${margin.top + (steps.length * cellSize) / 2}" text-anchor="middle" fill="var(--text-primary, #0F2C59)" font-size="12" font-weight="700" transform="rotate(-90, 18, ${margin.top + (steps.length * cellSize) / 2})">
                &larr; Storytelling / Dashboards
            </text>
        `;

        // Highlight Synergy Zone (top-right 4x4 cells: coding >= 3.5 and story >= 3.5)
        const synStartX = margin.left + 5 * cellSize;
        const synStartY = margin.top;
        const synW = 4 * cellSize - 2;
        const synH = 4 * cellSize - 2;

        svg += `
            <rect x="${synStartX}" y="${synStartY}" width="${synW}" height="${synH}" rx="6" 
                  fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-dasharray="6,4" />
            <rect x="${synStartX + synW - 145}" y="${synStartY + 6}" width="140" height="20" rx="4" fill="rgba(245, 158, 11, 0.9)" />
            <text x="${synStartX + synW - 75}" y="${synStartY + 20}" fill="#000000" font-size="9.5" font-weight="800" text-anchor="middle">
                ⚡ +2.18x SYNERGY ZONE
            </text>
        `;

        // Active Candidate Marker
        if (candidate) {
            const cClamp = Math.max(1.0, Math.min(5.0, candCoding));
            const sClamp = Math.max(1.0, Math.min(5.0, candStory));

            const candX = margin.left + ((cClamp - 1.0) / 4.0) * ((steps.length - 1) * cellSize) + (cellSize / 2) - 1;
            const candY = margin.top + ((5.0 - sClamp) / 4.0) * ((steps.length - 1) * cellSize) + (cellSize / 2);

            const isCandSynergy = (candCoding >= 3.5 && candStory >= 3.5);

            svg += `
                <g class="candidate-marker-group" pointer-events="none">
                    <circle cx="${candX}" cy="${candY}" r="9" fill="#F59E0B" stroke="#FFFFFF" stroke-width="2.5" class="candidate-pulse-dot" />
                    <rect x="${candX - 55}" y="${candY - 28}" width="110" height="20" rx="4" fill="var(--bg-elevated, #FFFFFF)" stroke="#F59E0B" stroke-width="1.5" />
                    <text x="${candX}" y="${candY - 14}" text-anchor="middle" fill="var(--text-primary, #0F2C59)" font-size="10" font-weight="800">
                        ${candidate.name || 'Candidate'}: (${candCoding.toFixed(1)}, ${candStory.toFixed(1)})
                    </text>
                </g>
            `;
        }

        svg += `</svg>`;

        const html = `
            <div class="synergy-surface-wrapper">
                ${svg}
                <div style="display:flex; justify-content:center; gap:16px; font-size:11px; color:var(--text-secondary); margin-top:6px; flex-wrap:wrap;">
                    <span style="display:inline-flex; align-items:center; gap:5px;">
                        <span style="width:12px; height:12px; background:#0F2C59; border-radius:2px;"></span> &lt;25% Low Hike
                    </span>
                    <span style="display:inline-flex; align-items:center; gap:5px;">
                        <span style="width:12px; height:12px; background:#0284C7; border-radius:2px;"></span> 40-55% Moderate
                    </span>
                    <span style="display:inline-flex; align-items:center; gap:5px;">
                        <span style="width:12px; height:12px; background:#059669; border-radius:2px;"></span> 55-70% High
                    </span>
                    <span style="display:inline-flex; align-items:center; gap:5px;">
                        <span style="width:12px; height:12px; background:#F59E0B; border-radius:2px;"></span> &gt;80% Peak (+2.18x Synergy)
                    </span>
                </div>
            </div>
        `;

        container.innerHTML = html;
        this.attachSynergyHoverListeners(container);
    },

    attachSynergyHoverListeners: function(container) {
        let tooltip = document.getElementById('synergy-cell-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'synergy-cell-tooltip';
            tooltip.className = 'synergy-tooltip-card';
            tooltip.style.display = 'none';
            document.body.appendChild(tooltip);
        }

        const cells = container.querySelectorAll('.synergy-grid-cell');
        cells.forEach(cell => {
            cell.addEventListener('mouseenter', (e) => {
                const coding = cell.getAttribute('data-coding');
                const story = cell.getAttribute('data-story');
                const prob = cell.getAttribute('data-prob');
                const synergy = cell.getAttribute('data-synergy');
                const isSyn = synergy.includes('UNLOCKED');

                tooltip.innerHTML = `
                    <div style="font-size:10px; font-weight:800; color:#10B981; text-transform:uppercase; margin-bottom:2px;">
                        Skill Coordinate: (${coding}, ${story})
                    </div>
                    <div style="font-size:14px; font-weight:800; color:var(--text-primary); margin-bottom:4px;">
                        P(Hike &gt; 25%): <span style="color:${isSyn ? '#F59E0B' : '#00A3E0'};">${prob}</span>
                    </div>
                    <div style="font-size:11px; font-weight:700; color:${isSyn ? '#059669' : '#64748B'};">
                        Synergy Multiplier: ${isSyn ? '⚡ UNLOCKED (+2.18x)' : '🔒 Base Trajectory'}
                    </div>
                    <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">
                        Coding: ${coding}/5.0 | Storytelling: ${story}/5.0
                    </div>
                `;
                tooltip.style.display = 'block';
                this.positionTooltip(e, tooltip);
            });

            cell.addEventListener('mousemove', (e) => {
                this.positionTooltip(e, tooltip);
            });

            cell.addEventListener('mouseleave', () => {
                tooltip.style.display = 'none';
            });
        });
    },

    /**
     * Renders Interactive ROC Curve with dynamic threshold scrubber & live confusion matrix recalculation
     */
    renderInteractiveROC: function(rocContainerId, cmContainerId, model = 'jds') {
        const rocContainer = document.getElementById(rocContainerId);
        if (!rocContainer) return;

        const data = window.ModelOutputs?.data;
        if (!data) return;

        const points = model === 'jds'
            ? data.model2_jds_hike.roc_curve_points
            : data.model3_sds_leakage.roc_curve_points;

        const auc = model === 'jds'
            ? data.model2_jds_hike.model_metrics.train_auc
            : data.model3_sds_leakage.logistic_ocean.auc;

        const width = 380, height = 300;
        const margin = { top: 25, right: 25, bottom: 45, left: 50 };
        const pw = width - margin.left - margin.right;
        const ph = height - margin.top - margin.bottom;

        function x(v) { return margin.left + v * pw; }
        function y(v) { return margin.top + (1 - v) * ph; }

        let pathD = '';
        points.forEach((pt, i) => {
            const cmd = i === 0 ? 'M' : 'L';
            pathD += `${cmd} ${x(pt.fpr)},${y(pt.tpr)} `;
        });

        const color = model === 'jds' ? '#0077C8' : '#6D28D9';

        let svg = `
            <svg id="roc-interactive-svg" viewBox="0 0 ${width} ${height}" style="width:100%; height:auto; font-family:Inter, sans-serif;">
                <!-- Grid Lines -->
                <line x1="${x(0)}" y1="${y(0)}" x2="${x(1)}" y2="${y(0)}" stroke="var(--border-light, #E2E8F0)" />
                <line x1="${x(0)}" y1="${y(0.5)}" x2="${x(1)}" y2="${y(0.5)}" stroke="var(--border-light, #E2E8F0)" stroke-dasharray="2,2" />
                <line x1="${x(0)}" y1="${y(1)}" x2="${x(1)}" y2="${y(1)}" stroke="var(--border-light, #E2E8F0)" stroke-dasharray="2,2" />
                <line x1="${x(0.5)}" y1="${y(0)}" x2="${x(0.5)}" y2="${y(1)}" stroke="var(--border-light, #E2E8F0)" stroke-dasharray="2,2" />
                <line x1="${x(1)}" y1="${y(0)}" x2="${x(1)}" y2="${y(1)}" stroke="var(--border-light, #E2E8F0)" />
                <line x1="${x(0)}" y1="${y(0)}" x2="${x(0)}" y2="${y(1)}" stroke="var(--border-light, #E2E8F0)" />

                <!-- Random Chance Diagonal -->
                <line x1="${x(0)}" y1="${y(0)}" x2="${x(1)}" y2="${y(1)}" stroke="#94A3B8" stroke-width="1.5" stroke-dasharray="4,4" />

                <!-- ROC Trajectory -->
                <path d="${pathD}" fill="none" stroke="${color}" stroke-width="3" />

                <!-- AUC Badge -->
                <rect x="${x(0.52)}" y="${y(0.28)}" width="90" height="24" rx="4" fill="rgba(0, 119, 200, 0.15)" stroke="${color}" stroke-width="1.5" />
                <text x="${x(0.52) + 45}" y="${y(0.28) + 16}" fill="${color}" font-size="12" font-weight="800" text-anchor="middle">
                    AUC = ${auc.toFixed(4)}
                </text>

                <!-- Current Operating Point Crosshairs & Marker -->
                <line id="roc-crosshair-x" x1="${x(0.18)}" y1="${y(0)}" x2="${x(0.18)}" y2="${y(0.87)}" stroke="#00A3E0" stroke-width="1.5" stroke-dasharray="3,3" />
                <line id="roc-crosshair-y" x1="${x(0)}" y1="${y(0.87)}" x2="${x(0.18)}" y2="${y(0.87)}" stroke="#00A3E0" stroke-width="1.5" stroke-dasharray="3,3" />
                <circle id="roc-operating-dot" cx="${x(0.18)}" cy="${y(0.87)}" r="7" fill="#F59E0B" stroke="#FFFFFF" stroke-width="2.5" class="roc-operating-marker" />

                <!-- Axis Labels -->
                <text x="${width / 2}" y="${height - 8}" text-anchor="middle" fill="var(--text-secondary, #475569)" font-size="11" font-weight="600">
                    False Positive Rate (1 - Specificity) &rarr;
                </text>
                <text x="14" y="${height / 2}" text-anchor="middle" fill="var(--text-secondary, #475569)" font-size="11" font-weight="600" transform="rotate(-90, 14, ${height / 2})">
                    &larr; True Positive Rate (Sensitivity)
                </text>
            </svg>
        `;

        const scrubberControls = `
            <div class="roc-scrubber-box">
                <div class="roc-scrubber-header">
                    <div>
                        <span style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Classification Cutoff (&tau;):</span>
                        <strong id="roc-cutoff-val" style="font-size:15px; color:var(--sas-cyan-accent, #00A3E0); margin-left:6px;">0.50</strong>
                    </div>
                    <button class="btn-sas btn-sas-secondary" id="btn-youden-optimal" style="padding:3px 10px; font-size:11px; font-weight:700;">
                        🎯 Set Youden's Optimal (&tau; = 0.52)
                    </button>
                </div>
                <input type="range" id="roc-threshold-slider" min="0.10" max="0.90" step="0.01" value="0.50" style="width:100%; accent-color:#0077C8; cursor:ew-resize;">
                <div style="display:flex; justify-content:space-between; font-size:10px; color:var(--text-muted); margin-top:2px;">
                    <span>0.10 (High Sensitivity)</span>
                    <span id="roc-youden-index" style="font-weight:700; color:#059669;">Youden's J = 0.690</span>
                    <span>0.90 (High Specificity)</span>
                </div>
                <div class="roc-metrics-bar" id="roc-metrics-chips">
                    <div class="roc-metric-chip">
                        <div class="chip-label">Sensitivity</div>
                        <div class="chip-val" id="roc-sens-val">87.7%</div>
                    </div>
                    <div class="roc-metric-chip">
                        <div class="chip-label">Specificity</div>
                        <div class="chip-val" id="roc-spec-val">81.3%</div>
                    </div>
                    <div class="roc-metric-chip">
                        <div class="chip-label">Precision</div>
                        <div class="chip-val" id="roc-prec-val">84.2%</div>
                    </div>
                    <div class="roc-metric-chip">
                        <div class="chip-label">Accuracy</div>
                        <div class="chip-val" id="roc-acc-val">84.7%</div>
                    </div>
                    <div class="roc-metric-chip">
                        <div class="chip-label">F1-Score</div>
                        <div class="chip-val" id="roc-f1-val">0.859</div>
                    </div>
                </div>
            </div>
        `;

        rocContainer.innerHTML = svg + scrubberControls;

        // Wire up slider listeners to recalculate confusion matrix and move marker
        this.wireRocScrubberListeners(points, cmContainerId);
    },

    wireRocScrubberListeners: function(points, cmContainerId) {
        const slider = document.getElementById('roc-threshold-slider');
        const cutoffLabel = document.getElementById('roc-cutoff-val');
        const youdenLabel = document.getElementById('roc-youden-index');
        const dot = document.getElementById('roc-operating-dot');
        const crossX = document.getElementById('roc-crosshair-x');
        const crossY = document.getElementById('roc-crosshair-y');
        const youdenBtn = document.getElementById('btn-youden-optimal');

        if (!slider) return;

        const pw = 380 - 50 - 25;
        const ph = 300 - 25 - 45;
        function x(v) { return 50 + v * pw; }
        function y(v) { return 25 + (1 - v) * ph; }

        const updateState = (tau) => {
            if (cutoffLabel) cutoffLabel.textContent = tau.toFixed(2);

            // Interpolate point along ROC curve as function of threshold
            // At tau = 0.50, standard point is around idx = 25 (FPR 0.187, TPR 0.877)
            const idx = Math.min(points.length - 1, Math.max(0, Math.round((1.0 - tau) * (points.length - 1))));
            const pt = points[idx] || points[Math.floor(points.length / 2)];

            if (dot) {
                dot.setAttribute('cx', x(pt.fpr));
                dot.setAttribute('cy', y(pt.tpr));
            }
            if (crossX) {
                crossX.setAttribute('x1', x(pt.fpr));
                crossX.setAttribute('x2', x(pt.fpr));
                crossX.setAttribute('y1', y(0));
                crossX.setAttribute('y2', y(pt.tpr));
            }
            if (crossY) {
                crossY.setAttribute('x1', x(0));
                crossY.setAttribute('x2', x(pt.fpr));
                crossY.setAttribute('y1', y(pt.tpr));
                crossY.setAttribute('y2', y(pt.tpr));
            }

            // Empirical counts across N = 137 juniors (Actual HIGH = 73, Actual LOW = 64)
            const tp = Math.round(73 * pt.tpr);
            const fn = 73 - tp;
            const fp = Math.round(64 * pt.fpr);
            const tn = 64 - fp;

            const sens = tp / 73;
            const spec = tn / 64;
            const prec = (tp + fp) > 0 ? tp / (tp + fp) : 1.0;
            const acc = (tp + tn) / 137;
            const f1 = (prec + sens) > 0 ? (2 * prec * sens) / (prec + sens) : 0;
            const youdenJ = sens + spec - 1;

            if (youdenLabel) youdenLabel.textContent = `Youden's J = ${youdenJ.toFixed(3)}`;

            const sensVal = document.getElementById('roc-sens-val');
            const specVal = document.getElementById('roc-spec-val');
            const precVal = document.getElementById('roc-prec-val');
            const accVal = document.getElementById('roc-acc-val');
            const f1Val = document.getElementById('roc-f1-val');

            if (sensVal) sensVal.textContent = `${(sens * 100).toFixed(1)}%`;
            if (specVal) specVal.textContent = `${(spec * 100).toFixed(1)}%`;
            if (precVal) precVal.textContent = `${(prec * 100).toFixed(1)}%`;
            if (accVal) accVal.textContent = `${(acc * 100).toFixed(1)}%`;
            if (f1Val) f1Val.textContent = f1.toFixed(3);

            // Dynamically refresh Confusion Matrix table in #confusion-matrix-jds
            const cmEl = document.getElementById(cmContainerId);
            if (cmEl) {
                cmEl.innerHTML = `
                    <div style="display:flex; flex-direction:column; align-items:center; width:100%;">
                        <div style="font-size:13px; font-weight:700; color:var(--text-primary); margin-bottom:10px;">
                            JDS Hike Model Confusion Matrix (N = 137 at &tau; = ${tau.toFixed(2)})
                        </div>
                        <table style="border-collapse:collapse; text-align:center; font-size:13px; width:100%; max-width:320px;">
                            <tr>
                                <td style="padding:6px 10px;"></td>
                                <td style="padding:6px 10px; font-weight:700; color:var(--sas-blue-primary, #005A9C);">Pred: LOW</td>
                                <td style="padding:6px 10px; font-weight:700; color:var(--sas-blue-primary, #005A9C);">Pred: HIGH</td>
                            </tr>
                            <tr>
                                <td style="padding:6px 10px; font-weight:700; color:var(--sas-purple, #6D28D9);">Actual: LOW</td>
                                <td style="padding:8px 12px; background:rgba(16, 185, 129, 0.18); font-weight:800; color:#065F46; border:1px solid #A7F3D0; border-radius:4px;">
                                    ${tn} <span style="font-size:10px; font-weight:600;">(TN)</span>
                                </td>
                                <td style="padding:8px 12px; background:rgba(239, 68, 68, 0.18); font-weight:800; color:#991B1B; border:1px solid #FECACA; border-radius:4px;">
                                    ${fp} <span style="font-size:10px; font-weight:600;">(FP)</span>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding:6px 10px; font-weight:700; color:var(--sas-purple, #6D28D9);">Actual: HIGH</td>
                                <td style="padding:8px 12px; background:rgba(239, 68, 68, 0.18); font-weight:800; color:#991B1B; border:1px solid #FECACA; border-radius:4px;">
                                    ${fn} <span style="font-size:10px; font-weight:600;">(FN)</span>
                                </td>
                                <td style="padding:8px 12px; background:rgba(16, 185, 129, 0.18); font-weight:800; color:#065F46; border:1px solid #A7F3D0; border-radius:4px;">
                                    ${tp} <span style="font-size:10px; font-weight:600;">(TP)</span>
                                </td>
                            </tr>
                        </table>
                    </div>
                `;
            }
        };

        slider.addEventListener('input', () => {
            updateState(parseFloat(slider.value));
        });

        if (youdenBtn) {
            youdenBtn.addEventListener('click', () => {
                slider.value = '0.52';
                updateState(0.52);
            });
        }

        // Initialize state at 0.50
        updateState(0.50);
    },


    /**
     * Renders Tri-Axial Alignment Divergence Matrix & Correlations
     */
    renderTriAxialTable: function(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const data = SAS_DATA.triAxial;
        let html = `
            <div class="table-responsive">
                <table class="sas-table">
                    <thead>
                        <tr>
                            <th>Skill Domain</th>
                            <th>Axis 1: Listed Share</th>
                            <th>Axis 2: Market Paid (OR)</th>
                            <th>Axis 3: Internal Rewarded (OR)</th>
                            <th>Rank Discordance (Δ)</th>
                            <th>Crosswalk Verdict</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        data.forEach(row => {
            const discordanceBadge = row.discordanceDelta >= 4 
                ? `<span class="sas-badge badge-danger">High Mismatch (Δ=${row.discordanceDelta})</span>` 
                : (row.discordanceDelta >= 2 
                    ? `<span class="sas-badge badge-warning">Moderate (Δ=${row.discordanceDelta})</span>` 
                    : `<span class="sas-badge badge-success">Aligned (Δ=${row.discordanceDelta})</span>`);

            html += `
                <tr>
                    <td class="font-bold text-navy">
                        ${row.name}
                        <div class="text-xs text-muted">${row.canonicalSkills}</div>
                    </td>
                    <td>
                        <div class="font-semibold">${row.listedSharePct.toFixed(1)}%</div>
                        <div class="text-xs text-muted">Rank #${row.rankListed} (${row.listedCount.toLocaleString()} postings)</div>
                    </td>
                    <td>
                        <div class="font-semibold text-blue">${row.paidOR.toFixed(2)}x</div>
                        <div class="text-xs text-muted">95% CI: [${row.paidCILower.toFixed(2)}, ${row.paidCIUpper.toFixed(2)}] (Rank #${row.rankPaid})</div>
                    </td>
                    <td>
                        <div class="font-semibold text-purple">${row.rewardedOR.toFixed(2)}x</div>
                        <div class="text-xs text-muted">95% BCa: [${row.rewardedCILower.toFixed(2)}, ${row.rewardedCIUpper.toFixed(2)}] (Rank #${row.rankRewarded})</div>
                    </td>
                    <td>${discordanceBadge}</td>
                    <td class="text-sm font-medium">${row.verdict}</td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = html;
    }
};

// Export to window
if (typeof window !== "undefined") {
    window.SASVisualizer = SASVisualizer;
}
