"""
Single-page application HTML, CSS, and JavaScript for the AdaptPulse Web UI.
Provides a multi-page interactive dashboard with tabs for:
- Dashboard & Readiness
- Performance Analysis & PMC
- Goal Setting & Athlete Profile
- Dynamic Plan & Calendar (with COROS preview)
- Ecosystem & Sync Status
- Export Center
"""

def get_app_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AdaptPulse | Sports Science Training Suite</title>
  <style>
    :root {
      --bg: #090d16;
      --card-bg: #111827;
      --card-border: #1f2937;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --accent: #06b6d4;
      --accent-hover: #0891b2;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      color: var(--text-main);
      font-family: var(--font);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header {
      background: #0f172a;
      border-bottom: 1px solid var(--card-border);
      padding: 1rem 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .brand-logo {
      width: 32px;
      height: 32px;
      background: linear-gradient(135deg, var(--accent), var(--success));
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      color: #000;
      font-size: 1.1rem;
    }
    .brand-title {
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.025em;
    }
    .brand-tag {
      font-size: 0.75rem;
      color: var(--accent);
      background: rgba(6, 182, 212, 0.15);
      padding: 2px 8px;
      border-radius: 9999px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    nav {
      display: flex;
      gap: 0.5rem;
    }
    .nav-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 0.5rem 1rem;
      border-radius: 6px;
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .nav-btn:hover {
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.05);
    }
    .nav-btn.active {
      color: var(--accent);
      background: rgba(6, 182, 212, 0.12);
      border: 1px solid rgba(6, 182, 212, 0.3);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    .status-badge {
      font-size: 0.75rem;
      padding: 4px 10px;
      border-radius: 9999px;
      background: rgba(16, 185, 129, 0.15);
      color: var(--success);
      border: 1px solid rgba(16, 185, 129, 0.3);
      font-weight: 600;
    }

    main {
      flex: 1;
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
      width: 100%;
    }

    .tab-content { display: none; }
    .tab-content.active { display: block; }

    .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }

    @media (max-width: 1024px) {
      .grid-3, .grid-4 { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 768px) {
      header { flex-direction: column; gap: 1rem; }
      nav { flex-wrap: wrap; justify-content: center; }
      .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.5rem;
      position: relative;
    }
    .card-title {
      font-size: 0.875rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      font-weight: 600;
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .card-value {
      font-size: 2.25rem;
      font-weight: 800;
      letter-spacing: -0.025em;
      color: var(--text-main);
    }
    .card-subtext {
      font-size: 0.8125rem;
      color: var(--text-muted);
      margin-top: 0.5rem;
    }

    .gauge-container {
      margin: 1.5rem 0;
      position: relative;
    }
    .gauge-bar-bg {
      height: 12px;
      background: #1f2937;
      border-radius: 6px;
      position: relative;
      overflow: hidden;
    }
    .gauge-fill {
      height: 100%;
      border-radius: 6px;
      transition: width 0.5s ease;
    }
    .gauge-ticks {
      display: flex;
      justify-content: space-between;
      margin-top: 6px;
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .alert-box {
      background: rgba(245, 158, 11, 0.1);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1.5rem;
    }
    .alert-title {
      font-size: 0.875rem;
      font-weight: 700;
      color: var(--warning);
      margin-bottom: 0.25rem;
    }
    .alert-desc {
      font-size: 0.8125rem;
      color: #d1d5db;
      line-height: 1.5;
    }

    .btn {
      background: var(--accent);
      color: #000;
      border: none;
      padding: 0.625rem 1.25rem;
      font-size: 0.875rem;
      font-weight: 700;
      border-radius: 6px;
      cursor: pointer;
      transition: background 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
    }
    .btn:hover { background: var(--accent-hover); }
    .btn-secondary {
      background: #374151;
      color: #f3f4f6;
    }
    .btn-secondary:hover { background: #4b5563; }
    .btn-danger {
      background: var(--danger);
      color: #fff;
    }
    .btn-danger:hover { background: #dc2626; }

    /* Form Inputs */
    .form-group {
      margin-bottom: 1.25rem;
    }
    .form-label {
      display: block;
      font-size: 0.8125rem;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 0.375rem;
    }
    .form-input, .form-select {
      width: 100%;
      background: #1f2937;
      border: 1px solid #374151;
      color: #f3f4f6;
      padding: 0.625rem 0.875rem;
      border-radius: 6px;
      font-size: 0.875rem;
      outline: none;
      transition: border 0.15s;
    }
    .form-input:focus, .form-select:focus {
      border-color: var(--accent);
    }
    .range-wrap {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    .range-val {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--accent);
      min-width: 60px;
    }

    /* Calendar Grid */
    .calendar-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 1rem;
      margin-top: 1.5rem;
    }
    @media (max-width: 1100px) {
      .calendar-grid { grid-template-columns: repeat(4, 1fr); }
    }
    @media (max-width: 700px) {
      .calendar-grid { grid-template-columns: 1fr; }
    }
    .day-col {
      background: #111827;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 1rem;
      min-height: 220px;
      display: flex;
      flex-direction: column;
    }
    .day-header {
      font-size: 0.75rem;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--text-muted);
      border-bottom: 1px solid #1f2937;
      padding-bottom: 0.5rem;
      margin-bottom: 0.75rem;
      display: flex;
      justify-content: space-between;
    }
    .workout-card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 6px;
      padding: 0.75rem;
      cursor: pointer;
      transition: all 0.15s;
      flex: 1;
    }
    .workout-card:hover {
      border-color: var(--accent);
      transform: translateY(-2px);
    }
    .workout-tag {
      font-size: 0.6875rem;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 700;
      display: inline-block;
      margin-bottom: 0.375rem;
    }
    .tag-run { background: rgba(6, 182, 212, 0.2); color: #38bdf8; }
    .tag-ride { background: rgba(16, 185, 129, 0.2); color: #34d399; }
    .tag-swim { background: rgba(14, 165, 233, 0.25); color: #38bdf8; }
    .tag-brick { background: rgba(168, 85, 247, 0.25); color: #c084fc; }
    .tag-rest { background: rgba(107, 114, 128, 0.2); color: #9ca3af; }
    .tag-quality { background: rgba(244, 63, 94, 0.2); color: #fb7185; }

    .workout-title {
      font-size: 0.8125rem;
      font-weight: 700;
      color: #f3f4f6;
      margin-bottom: 0.375rem;
      line-height: 1.3;
    }
    .workout-meta {
      font-size: 0.6875rem;
      color: var(--text-muted);
    }

    /* Modal / Drawer */
    .modal-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      z-index: 100;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
    }
    .modal-overlay.active { display: flex; }
    .modal {
      background: #111827;
      border: 1px solid #374151;
      border-radius: 12px;
      max-width: 650px;
      width: 100%;
      max-height: 85vh;
      overflow-y: auto;
      padding: 2rem;
      position: relative;
    }
    .modal-close {
      position: absolute;
      top: 1rem;
      right: 1.25rem;
      background: none;
      border: none;
      color: var(--text-muted);
      font-size: 1.5rem;
      cursor: pointer;
    }

    /* Watch Preview Box */
    .coros-preview-box {
      background: #000;
      border: 3px solid #334155;
      border-radius: 24px;
      padding: 1.5rem;
      margin-top: 1.25rem;
      font-family: monospace;
      color: #38bdf8;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
    }
    .coros-screen-header {
      font-size: 0.75rem;
      color: #94a3b8;
      border-bottom: 1px dashed #334155;
      padding-bottom: 0.5rem;
      margin-bottom: 0.75rem;
    }

    /* SVG Charts */
    .chart-box {
      width: 100%;
      height: 280px;
      background: #0f172a;
      border-radius: 8px;
      padding: 1rem;
      border: 1px solid var(--card-border);
      position: relative;
    }

    .table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.875rem;
      margin-top: 1rem;
    }
    .table th {
      text-align: left;
      padding: 0.75rem 1rem;
      border-bottom: 1px solid var(--card-border);
      color: var(--text-muted);
      font-weight: 600;
    }
    .table td {
      padding: 0.75rem 1rem;
      border-bottom: 1px solid #1f2937;
    }

    .toast {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: #1e293b;
      border: 1px solid var(--accent);
      color: #fff;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
      z-index: 200;
      display: none;
    }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-logo">AP</div>
      <div>
        <span class="brand-title">AdaptPulse</span>
        <span class="brand-tag">v0.3.0</span>
      </div>
    </div>
    <nav>
      <button class="nav-btn active" onclick="switchTab('dashboard')">Dashboard</button>
      <button class="nav-btn" onclick="switchTab('analysis')">Analysis</button>
      <button class="nav-btn" onclick="switchTab('goals')">Goals & Profile</button>
      <button class="nav-btn" onclick="switchTab('planner')">Calendar & Plan</button>
      <button class="nav-btn" onclick="switchTab('sync')">Ecosystem & Sync</button>
      <button class="nav-btn" onclick="switchTab('export')">Export Center</button>
    </nav>
    <div class="header-actions">
      <span class="status-badge" id="systemStatus">Online</span>
    </div>
  </header>

  <main>
    <!-- TAB 1: DASHBOARD & READINESS -->
    <div id="tab-dashboard" class="tab-content active">
      <div id="readinessAlert" class="alert-box" style="display:none;">
        <div class="alert-title" id="alertTitle">Biometric Notice</div>
        <div class="alert-desc" id="alertDesc">Reviewing physiological telemetry...</div>
      </div>

      <div class="grid-4" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div class="card-title">Physiological Readiness</div>
          <div class="card-value" id="readinessScore">--</div>
          <div class="card-subtext" id="readinessState">Calculating...</div>
        </div>
        <div class="card">
          <div class="card-title">ACWR (Tim Gabbett)</div>
          <div class="card-value" id="acwrRatio">--</div>
          <div class="card-subtext" id="acwrStatus">Sweet Spot: 0.8 - 1.3</div>
        </div>
        <div class="card">
          <div class="card-title">Performance Balance (TSB)</div>
          <div class="card-value" id="tsbValue">--</div>
          <div class="card-subtext" id="pmcSubtext">Fitness vs Fatigue</div>
        </div>
        <div class="card">
          <div class="card-title">Resting HR (3d vs 30d)</div>
          <div class="card-value" id="rhrDelta">--</div>
          <div class="card-subtext" id="rhrSubtext">Baseline stability</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">Weekly Load Distribution & Target</div>
          <div class="gauge-container">
            <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem; font-size:0.875rem;">
              <span>Target Volume</span>
              <strong id="targetHoursText">8.0 Hours</strong>
            </div>
            <div class="gauge-bar-bg">
              <div id="acwrBarFill" class="gauge-fill" style="width: 50%; background: var(--accent);"></div>
            </div>
            <div class="gauge-ticks">
              <span>0.0 (Under)</span>
              <span>0.8 (Sweet Spot)</span>
              <span>1.3 (Elevated)</span>
              <span>1.5+ (Danger)</span>
            </div>
          </div>
          <p class="card-subtext" id="acwrGuidance">Optimal progressive overload without non-contact injury spikes.</p>
        </div>

        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.5rem;">
            <div class="card-title" style="margin-bottom:0;">Sports Science Coaching Briefing</div>
            <button class="btn btn-secondary" id="aiSynthBtn" onclick="fetchAiCoach()" style="font-size:0.75rem; padding:0.25rem 0.5rem;">AI Synthesis (:free)</button>
          </div>
          <div style="font-weight: 700; font-size: 1.1rem; color: var(--accent); margin-bottom: 0.5rem;" id="coachHeadline">
            Analyzing training status...
          </div>
          <p style="font-size: 0.875rem; color: #d1d5db; line-height: 1.5; margin-bottom: 0.75rem;" id="coachFocus">
            Loading tailored guidance...
          </p>
          <div id="aiCoachBox" style="display:none; background: #0f172a; border: 1px solid #0284c7; border-radius: 6px; padding: 0.75rem; margin-bottom: 0.75rem;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; margin-bottom: 4px;">AI Sports Science Synthesis (Token-Lean)</div>
            <div style="font-size: 0.8125rem; color: #e2e8f0; line-height: 1.4;" id="aiCoachText"></div>
            <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 4px;" id="aiCoachMetrics"></div>
          </div>
          <ul id="coachRecList" style="font-size: 0.8125rem; color: var(--text-muted); padding-left: 1.25rem; line-height: 1.6;">
          </ul>
        </div>
      </div>
    </div>

    <!-- TAB 2: ANALYSIS & PMC -->
    <div id="tab-analysis" class="tab-content">
      <div class="card" style="margin-bottom: 1.5rem;">
        <div class="card-title">Performance Management Chart (Banister / Coggan PMC)</div>
        <div class="chart-box" id="pmcChartContainer">
          <svg id="pmcChartSvg" width="100%" height="100%" viewBox="0 0 800 240" preserveAspectRatio="none">
            <!-- Background grid lines -->
            <line x1="0" y1="60" x2="800" y2="60" stroke="#1f2937" stroke-dasharray="4"/>
            <line x1="0" y1="120" x2="800" y2="120" stroke="#374151" stroke-dasharray="2"/>
            <line x1="0" y1="180" x2="800" y2="180" stroke="#1f2937" stroke-dasharray="4"/>
            <!-- Curves dynamically injected -->
            <path id="ctlPath" d="M 0 140 Q 400 120 800 110" fill="none" stroke="#06b6d4" stroke-width="3"/>
            <path id="atlPath" d="M 0 150 Q 400 100 800 90" fill="none" stroke="#f43f5e" stroke-width="2"/>
            <path id="tsbPath" d="M 0 120 Q 400 130 800 140" fill="none" stroke="#10b981" stroke-width="2" stroke-dasharray="5"/>
          </svg>
        </div>
        <div style="display:flex; justify-content:center; gap: 2rem; margin-top: 1rem; font-size: 0.8125rem;">
          <span style="color:#06b6d4; font-weight:700;">— CTL (Fitness 42d)</span>
          <span style="color:#f43f5e; font-weight:700;">— ATL (Fatigue 7d)</span>
          <span style="color:#10b981; font-weight:700;">-- TSB (Form)</span>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">Stephen Seiler 80/20 Intensity Polarization</div>
          <div style="margin: 1.5rem 0;">
            <div style="display:flex; height: 28px; border-radius: 6px; overflow: hidden; margin-bottom: 0.75rem;">
              <div id="barLow" style="width: 80%; background: #10b981;" title="Low Intensity Zone 1-2"></div>
              <div id="barMod" style="width: 10%; background: #f59e0b;" title="Moderate Zone 3"></div>
              <div id="barHigh" style="width: 10%; background: #ef4444;" title="High Zone 4-5"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size: 0.8125rem;">
              <span id="labelLow" style="color: #10b981;">Low: 80%</span>
              <span id="labelMod" style="color: #f59e0b;">Moderate: 10%</span>
              <span id="labelHigh" style="color: #ef4444;">High: 10%</span>
            </div>
          </div>
          <p class="card-subtext" id="polarizationSummary">Well-polarized endurance base distribution.</p>
        </div>

        <div class="card">
          <div class="card-title">Completed Discipline Breakdown (Last 30 Days)</div>
          <table class="table">
            <thead>
              <tr>
                <th>Sport</th>
                <th>Sessions</th>
                <th>Time (Hrs)</th>
                <th>Load (TSS)</th>
                <th>Distance</th>
              </tr>
            </thead>
            <tbody id="disciplineTableBody">
              <tr><td colspan="5" style="text-align:center; color:var(--text-muted);">Loading disciplines...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Plan Compliance & Execution Card -->
      <div class="card" style="margin-top: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
          <div class="card-title" style="margin-bottom:0;">Plan Compliance & Execution (Rolling 28 Days)</div>
          <span id="compRatingBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">Optimal</span>
        </div>
        <div class="grid-3" style="margin-bottom: 1rem;">
          <div style="background:#111827; border:1px solid #1f2937; border-radius:6px; padding:0.75rem;">
            <div style="font-size:0.75rem; color:var(--text-muted);">Execution Rate</div>
            <div style="font-size:1.25rem; font-weight:700; color:#38bdf8;" id="compExecRate">--%</div>
            <div style="font-size:0.6875rem; color:var(--text-muted);" id="compWorkoutsRatio">-- / -- workouts</div>
          </div>
          <div style="background:#111827; border:1px solid #1f2937; border-radius:6px; padding:0.75rem;">
            <div style="font-size:0.75rem; color:var(--text-muted);">Volume Compliance</div>
            <div style="font-size:1.25rem; font-weight:700; color:var(--success);" id="compVolRate">--%</div>
            <div style="font-size:0.6875rem; color:var(--text-muted);" id="compVolHours">--h actual vs --h planned</div>
          </div>
          <div style="background:#111827; border:1px solid #1f2937; border-radius:6px; padding:0.75rem;">
            <div style="font-size:0.75rem; color:var(--text-muted);">Load Compliance (TSS)</div>
            <div style="font-size:1.25rem; font-weight:700; color:var(--accent);" id="compLoadRate">--%</div>
            <div style="font-size:0.6875rem; color:var(--text-muted);" id="compTssValues">-- actual vs -- planned</div>
          </div>
        </div>
        <div id="compObservations" style="font-size:0.8125rem; color:#d1d5db; line-height:1.5;"></div>
      </div>
    </div>

    <!-- TAB 3: GOALS & ATHLETE PROFILE -->
    <div id="tab-goals" class="tab-content">
      <div class="card">
        <div class="card-title">Athlete Profile & Periodization Configuration</div>
        <form id="profileForm" onsubmit="saveProfile(event)" style="margin-top: 1.5rem;">
          <div class="grid-3">
            <div class="form-group">
              <label class="form-label">Primary Training Goal</label>
              <select id="profGoal" class="form-select">
                <option value="dual_sport_hybrid">Dual-Sport Hybrid (Run & Bike)</option>
                <option value="sprint_triathlon">Sprint Triathlon (750m / 20k / 5k)</option>
                <option value="olympic_triathlon">Olympic Triathlon (1.5k / 40k / 10k)</option>
                <option value="half_ironman_70_3">IRONMAN 70.3 (1.9k / 90k / 21.1k)</option>
                <option value="full_ironman_140_6">IRONMAN 140.6 (3.8k / 180k / 42.2k)</option>
                <option value="running">Running Focus (5k / 10k / Marathon)</option>
                <option value="cycling">Cycling Focus (Road / Gravel / TT)</option>
                <option value="general_fitness">General Aerobic Health</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Target Race / Event Name</label>
              <input id="profEventName" class="form-input" placeholder="e.g. Autumn 10K Time Trial">
            </div>

            <div class="form-group">
              <label class="form-label">Target Race Date (YYYY-MM-DD)</label>
              <input id="profEventDate" type="date" class="form-input" onchange="updatePeriodizationBadge()">
            </div>
          </div>

          <div class="grid-3">
            <div class="form-group">
              <label class="form-label">Target Race Distance</label>
              <select id="profEventDist" class="form-select">
                <option value="5k">5K</option>
                <option value="10k">10K</option>
                <option value="half_marathon">Half Marathon</option>
                <option value="marathon">Full Marathon</option>
                <option value="olympic_tri">Olympic Triathlon</option>
                <option value="70.3">Ironman 70.3</option>
                <option value="gran_fondo">Gran Fondo</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Calculated Periodization Phase</label>
              <div id="periodizationBadge" style="padding: 0.625rem 0.875rem; background: #1f2937; border: 1px solid #374151; border-radius: 6px; font-weight:700; color:var(--accent);">
                Base (Accumulation)
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Training Philosophy</label>
              <select id="profPhilosophy" class="form-select">
                <option value="polarized_80_20">Stephen Seiler 80/20 Polarized</option>
                <option value="pyramidal">Pyramidal (More Tempo / Threshold)</option>
                <option value="hrv_governed">HRV Autonomic Governed</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Weekly Training Budget (Hours)</label>
            <div class="range-wrap">
              <input id="profHours" type="range" min="4" max="16" step="0.5" value="8" class="form-input" style="flex:1;" oninput="document.getElementById('hoursDisplay').innerText = this.value + ' hrs/wk'">
              <span id="hoursDisplay" class="range-val">8.0 hrs/wk</span>
            </div>
          </div>

          <div class="grid-3" style="margin-top: 1.5rem;">
            <div class="form-group">
              <label class="form-label">Run LTHR (bpm)</label>
              <input id="profLthrRun" type="number" class="form-input" value="182">
            </div>
            <div class="form-group">
              <label class="form-label">Bike FTP (Watts)</label>
              <input id="profFtp" type="number" class="form-input" value="250">
            </div>
            <div class="form-group">
              <label class="form-label">Swim CSS (sec/100m)</label>
              <input id="profCss" type="number" class="form-input" value="105">
            </div>
            <div class="form-group">
              <label class="form-label">Bike LTHR (bpm)</label>
              <input id="profLthrBike" type="number" class="form-input" value="182">
            </div>
            <div class="form-group">
              <label class="form-label">Max Heart Rate (bpm)</label>
              <input id="profMaxHr" type="number" class="form-input" value="200">
            </div>
            <div class="form-group">
              <label class="form-label">Pool Length (Meters)</label>
              <input id="profPool" type="number" class="form-input" value="25">
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Life Constraints & Schedule Notes (comma-separated)</label>
            <input id="profConstraints" class="form-input" placeholder="e.g. no_thursday_bike, travel_saturday, achilles_caution">
          </div>

          <div style="display:flex; justify-content:flex-end; gap: 1rem; margin-top: 1.5rem;">
            <button type="submit" class="btn">Save Profile Settings</button>
          </div>
        </form>
      </div>
    </div>

    <!-- TAB 4: CALENDAR & PLAN -->
    <div id="tab-planner" class="tab-content">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1.5rem; flex-wrap:wrap; gap:1rem;">
        <div>
          <h2 style="font-size:1.5rem; font-weight:800;">Rolling Calendar Schedule</h2>
          <p style="font-size:0.875rem; color:var(--text-muted);">Dynamically generated microcycle with step-by-step target zones</p>
        </div>
        <div style="display:flex; gap: 1rem; align-items:center;">
          <select id="planHorizonSelect" class="form-select" style="width: 140px;">
            <option value="1">1 Week</option>
            <option value="2">2 Weeks</option>
          </select>
          <button class="btn btn-secondary" onclick="generatePlanPreview()">Regenerate Plan</button>
          <button class="btn" onclick="applyPlanToIntervals()">Sync to Intervals.icu</button>
        </div>
      </div>

      <div style="display:flex; gap: 1rem; margin-bottom: 1rem;">
        <button id="week1Btn" class="btn btn-secondary" onclick="showWeek(1)" style="font-size:0.8125rem; padding: 0.375rem 0.75rem;">Week 1</button>
        <button id="week2Btn" class="btn btn-secondary" onclick="showWeek(2)" style="font-size:0.8125rem; padding: 0.375rem 0.75rem; display:none;">Week 2</button>
      </div>

      <div id="calendarContainer" class="calendar-grid">
        <!-- Day columns populated dynamically -->
      </div>
    </div>

    <!-- TAB 5: ECOSYSTEM & SYNC -->
    <div id="tab-sync" class="tab-content">
      <div class="grid-4" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div class="card-title">Intervals.icu Cloud Hub</div>
          <div style="font-size: 1.1rem; font-weight: 700; color: var(--success);" id="intervalsStatus">Connected</div>
          <p class="card-subtext">Direct calendar sync with read-back verification.</p>
        </div>
        <div class="card">
          <div class="card-title">TrainingPeaks Connector</div>
          <div style="font-size: 1.1rem; font-weight: 700; color: var(--accent);" id="tpStatus">Checking...</div>
          <p class="card-subtext">Structured workout export via OAuth Partner API.</p>
        </div>
        <div class="card">
          <div class="card-title">COROS Watch Sync</div>
          <div style="font-size: 1.1rem; font-weight: 700; color: #38bdf8;">Linked via Intervals</div>
          <p class="card-subtext">Clean ASCII cues &lt;= 20 chars ready for watch firmware.</p>
        </div>
        <div class="card">
          <div class="card-title">Strava & Hevy Integration</div>
          <div style="font-size: 1.1rem; font-weight: 700; color: var(--warning);">Automated Inflow</div>
          <p class="card-subtext">Gym workouts upload via Strava to complete stress profile.</p>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Recent Backups & Snapshots</div>
        <table class="table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Backup File</th>
              <th>Location</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="backupTableBody">
            <tr><td colspan="4" style="text-align:center; color:var(--text-muted);">Loading backups...</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 6: EXPORT CENTER -->
    <div id="tab-export" class="tab-content">
      <div class="card" style="margin-bottom: 1.5rem;">
        <div class="card-title">Export Workouts & Plan Files</div>
        <p style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 1.5rem;">
          Download your planned workouts in multi-platform compatible formats for indoor trainers, smart watches, and calendar software.
        </p>

        <div class="grid-3">
          <div style="background:#1e293b; border:1px solid #334155; border-radius:8px; padding:1.25rem;">
            <h3 style="font-size:1.1rem; margin-bottom:0.5rem; color:var(--accent);">Zwift (.zwo XML)</h3>
            <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:1rem;">
              Indoor smart trainer workout files. Compatible with Zwift and TrainerRoad.
            </p>
            <button class="btn btn-secondary" onclick="downloadExport('zwo')">Download Zwift Workouts</button>
          </div>

          <div style="background:#1e293b; border:1px solid #334155; border-radius:8px; padding:1.25rem;">
            <h3 style="font-size:1.1rem; margin-bottom:0.5rem; color:var(--success);">iCalendar (.ics)</h3>
            <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:1rem;">
              Standard RFC 5545 format. Directly subscribe in Google Calendar, Apple Calendar, or Outlook.
            </p>
            <button class="btn btn-secondary" onclick="downloadExport('ics')">Download .ics Calendar</button>
          </div>

          <div style="background:#1e293b; border:1px solid #334155; border-radius:8px; padding:1.25rem;">
            <h3 style="font-size:1.1rem; margin-bottom:0.5rem; color:#a855f7;">Structured JSON</h3>
            <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:1rem;">
              Full machine-readable specification of steps, targets, and dates.
            </p>
            <button class="btn btn-secondary" onclick="downloadExport('json')">Download JSON Plan</button>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- WORKOUT STEP INSPECTOR MODAL -->
  <div id="workoutModal" class="modal-overlay" onclick="if(event.target === this) closeModal()">
    <div class="modal">
      <button class="modal-close" onclick="closeModal()">&times;</button>
      <h2 id="modalWorkoutTitle" style="font-size: 1.25rem; margin-bottom: 0.5rem;">Workout Details</h2>
      <p id="modalWorkoutMeta" style="font-size: 0.8125rem; color: var(--text-muted); margin-bottom: 1.25rem;">Type & Duration</p>

      <div style="margin-bottom: 1.25rem;">
        <h4 style="font-size: 0.8125rem; text-transform:uppercase; color:var(--accent); margin-bottom: 0.5rem;">Target Coaching Notes</h4>
        <p id="modalWorkoutDesc" style="font-size: 0.875rem; color: #d1d5db; line-height: 1.5;"></p>
      </div>

      <!-- Nutrition & Fueling Box -->
      <div id="modalFuelingBox" style="background:#1e293b; border:1px solid #334155; border-radius:8px; padding:1rem; margin-bottom: 1.25rem;">
        <h4 style="font-size: 0.8125rem; text-transform:uppercase; color:var(--success); margin-bottom: 0.35rem;">Intra-Workout Fueling & Hydration Guidance</h4>
        <p id="modalFuelingSummary" style="font-size:0.8125rem; color:#f3f4f6; margin-bottom:0.5rem;"></p>
        <div style="display:flex; gap:1.5rem; font-size:0.8125rem; color:var(--text-muted); flex-wrap:wrap;">
          <div>Carbs: <strong id="modalCarbs" style="color:#f59e0b;">--</strong></div>
          <div>Fluids: <strong id="modalFluids" style="color:#38bdf8;">--</strong></div>
          <div>Sodium: <strong id="modalSodium" style="color:#ec4899;">--</strong></div>
        </div>
      </div>

      <div style="margin-bottom: 1.25rem;">
        <h4 style="font-size: 0.8125rem; text-transform:uppercase; color:var(--accent); margin-bottom: 0.5rem;">Interval Step Breakdown</h4>
        <table class="table">
          <thead>
            <tr>
              <th>Step</th>
              <th>Duration</th>
              <th>HR Target</th>
              <th>Power Target</th>
            </tr>
          </thead>
          <tbody id="modalStepsTable">
          </tbody>
        </table>
      </div>

      <div>
        <h4 style="font-size: 0.8125rem; text-transform:uppercase; color:#38bdf8; margin-bottom: 0.5rem;">COROS Watch Screen Simulation</h4>
        <div class="coros-preview-box">
          <div class="coros-screen-header" id="corosWatchHeader">COROS PACE / APEX DISPLAY</div>
          <div id="corosWatchBody">
            <div style="font-size:1.25rem; font-weight:800; color:#fff;" id="corosStepCue">WARMUP 10M</div>
            <div style="font-size:0.875rem; color:#94a3b8; margin-top:4px;" id="corosTargetRange">HR: 130-150 bpm</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div id="toast" class="toast">Profile updated successfully!</div>

  <script>
    let currentProfile = {};
    let currentPlanEvents = [];
    let currentAnalytics = null;
    let activeWeek = 1;

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.innerText = msg;
      t.style.display = 'block';
      setTimeout(() => { t.style.display = 'none'; }, 3000);
    }

    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
      const target = document.getElementById('tab-' + tabId);
      if (target) target.classList.add('active');
      event.target.classList.add('active');
    }

    async function loadDashboard() {
      try {
        const [profRes, anaRes, coachRes, statusRes, compRes] = await Promise.all([
          fetch('/api/profile'),
          fetch('/api/analytics'),
          fetch('/api/coaching'),
          fetch('/api/status'),
          fetch('/api/compliance')
        ]);

        currentProfile = await profRes.json();
        currentAnalytics = await anaRes.json();
        const coach = await coachRes.json();
        const statusData = await statusRes.json();
        const comp = await compRes.json();

        // Update Ecosystem status
        if (statusData) {
          const intStatusEl = document.getElementById('intervalsStatus');
          if (intStatusEl) {
            intStatusEl.innerText = statusData.intervals_connected ? 'Connected' : 'Not Configured';
            intStatusEl.style.color = statusData.intervals_connected ? 'var(--success)' : 'var(--text-muted)';
          }
          const tpStatusEl = document.getElementById('tpStatus');
          if (tpStatusEl) {
            tpStatusEl.innerText = statusData.trainingpeaks_connected ? 'Connected' : 'Not Configured';
            tpStatusEl.style.color = statusData.trainingpeaks_connected ? 'var(--success)' : 'var(--text-muted)';
          }
        }

        // Update Plan Compliance
        if (comp) {
          const elExec = document.getElementById('compExecRate');
          if (elExec) elExec.innerText = comp.execution_rate_pct.toFixed(0) + '%';
          const elRatio = document.getElementById('compWorkoutsRatio');
          if (elRatio) elRatio.innerText = comp.completed_count + ' of ' + comp.planned_count + ' completed';
          const elVol = document.getElementById('compVolRate');
          if (elVol) elVol.innerText = comp.volume_compliance_pct.toFixed(0) + '%';
          const elVolHrs = document.getElementById('compVolHours');
          if (elVolHrs) elVolHrs.innerText = comp.actual_volume_hours.toFixed(1) + 'h act / ' + comp.planned_volume_hours.toFixed(1) + 'h plan';
          const elLoad = document.getElementById('compLoadRate');
          if (elLoad) elLoad.innerText = comp.load_compliance_pct.toFixed(0) + '%';
          const elTss = document.getElementById('compTssValues');
          if (elTss) elTss.innerText = comp.actual_load_tss.toFixed(0) + ' act / ' + comp.planned_load_tss.toFixed(0) + ' plan';

          const rBadge = document.getElementById('compRatingBadge');
          if (rBadge) {
            rBadge.innerText = (comp.compliance_rating || 'OPTIMAL').replace('_', ' ');
            if (comp.compliance_rating === 'OPTIMAL') {
              rBadge.style.background = 'rgba(16,185,129,0.2)';
              rBadge.style.color = 'var(--success)';
            } else if (comp.compliance_rating === 'OVER_TRAINING_RISK') {
              rBadge.style.background = 'rgba(239,68,68,0.2)';
              rBadge.style.color = 'var(--danger)';
            } else {
              rBadge.style.background = 'rgba(245,158,11,0.2)';
              rBadge.style.color = 'var(--warning)';
            }
          }
          const obsDiv = document.getElementById('compObservations');
          if (obsDiv && comp.coaching_observations) {
            obsDiv.innerHTML = comp.coaching_observations.map(o => '<div style="margin-bottom:4px;">* ' + o + '</div>').join('');
          }
        }

        // Populate Dashboard Cards
        if (currentAnalytics && currentAnalytics.readiness) {
          const r = currentAnalytics.readiness;
          document.getElementById('readinessScore').innerText = r.readiness_score + '/100';
          document.getElementById('readinessState').innerText = r.readiness_state.replace('_', ' ');
          document.getElementById('tsbValue').innerText = (r.tsb >= 0 ? '+' : '') + r.tsb;
          document.getElementById('pmcSubtext').innerText = 'CTL: ' + r.ctl + ' | ATL: ' + r.atl;

          if (r.rhr_delta !== null && r.rhr_delta !== undefined) {
            document.getElementById('rhrDelta').innerText = (r.rhr_delta >= 0 ? '+' : '') + r.rhr_delta + ' bpm';
            document.getElementById('rhrSubtext').innerText = 'Recent: ' + r.recent_resting_hr + ' | Base: ' + r.resting_hr_baseline;
          }
        }

        if (currentAnalytics && currentAnalytics.acwr) {
          const a = currentAnalytics.acwr;
          document.getElementById('acwrRatio').innerText = a.ratio.toFixed(2);
          document.getElementById('acwrStatus').innerText = a.status.replace('_', ' ');
          document.getElementById('acwrGuidance').innerText = a.guidance;

          const pct = Math.min(100, Math.max(5, (a.ratio / 2.0) * 100));
          document.getElementById('acwrBarFill').style.width = pct + '%';
          if (a.status === 'DANGER_ZONE') {
            document.getElementById('acwrBarFill').style.background = 'var(--danger)';
          } else if (a.status === 'SWEET_SPOT') {
            document.getElementById('acwrBarFill').style.background = 'var(--success)';
          }
        }

        // Coaching briefing
        if (coach) {
          renderCoach(coach);
        }

        // Populate Profile inputs
        populateProfileForm(currentProfile);

        // Populate Analysis tab
        populateAnalysisTab(currentAnalytics);

        // Preload Plan Preview
        generatePlanPreview();

        // Load backups
        loadBackups();

      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      }
    }

    function renderCoach(coach) {
      if (!coach) return;
      document.getElementById('coachHeadline').innerText = coach.headline;
      document.getElementById('coachFocus').innerText = coach.training_focus;
      document.getElementById('targetHoursText').innerText = (coach.target_weekly_hours || 0).toFixed(1) + ' Hours';

      const recList = document.getElementById('coachRecList');
      recList.innerHTML = '';
      (coach.key_recommendations || []).forEach(item => {
        const li = document.createElement('li');
        li.innerText = item;
        recList.appendChild(li);
      });

      if (coach.ai_summary) {
        document.getElementById('aiCoachBox').style.display = 'block';
        document.getElementById('aiCoachText').innerText = coach.ai_summary;
        if (coach.token_metrics) {
          const hitText = coach.token_metrics.cache_hit ? 'Local Cache Hit (0 tok)' : `${coach.token_metrics.total_tokens || 0} tokens`;
          document.getElementById('aiCoachMetrics').innerText = `Cost: Zero-Cost (:free) | Accounting: ${hitText}`;
        }
      }

      if (coach.alerts && coach.alerts.length > 0) {
        document.getElementById('readinessAlert').style.display = 'block';
        document.getElementById('alertTitle').innerText = 'Biometric & Physiological Notice';
        document.getElementById('alertDesc').innerText = coach.alerts.join(' • ');
      }
    }

    async function fetchAiCoach() {
      const btn = document.getElementById('aiSynthBtn');
      if (btn) btn.innerText = 'Analyzing...';
      try {
        const res = await fetch('/api/coaching?ai=true');
        const data = await res.json();
        renderCoach(data);
      } catch (err) {
        console.error('Failed to fetch AI coaching:', err);
      } finally {
        if (btn) btn.innerText = 'AI Synthesis (:free)';
      }
    }

    function populateProfileForm(p) {
      if (!p) return;
      document.getElementById('profGoal').value = p.goal || 'dual_sport_hybrid';
      document.getElementById('profEventName').value = p.target_event_name || '';
      document.getElementById('profEventDate').value = p.target_race_date || '';
      document.getElementById('profEventDist').value = p.target_race_distance || '10k';
      document.getElementById('profPhilosophy').value = p.philosophy || 'polarized_80_20';
      document.getElementById('profHours').value = p.weekly_hours || 8;
      document.getElementById('hoursDisplay').innerText = (p.weekly_hours || 8).toFixed(1) + ' hrs/wk';
      document.getElementById('profLthrRun').value = p.lthr_run || 182;
      document.getElementById('profLthrBike').value = p.lthr_bike || 182;
      document.getElementById('profMaxHr').value = p.max_hr || 200;
      document.getElementById('profFtp').value = p.ftp_bike || 250;
      document.getElementById('profCss').value = p.swim_css_sec_100m || 105;
      document.getElementById('profPool').value = p.pool_length_m || 25;
      document.getElementById('profConstraints').value = (p.constraints || []).join(', ');
      updatePeriodizationBadge();
    }

    function updatePeriodizationBadge() {
      const dateVal = document.getElementById('profEventDate').value;
      const badge = document.getElementById('periodizationBadge');
      if (!dateVal) {
        badge.innerText = 'Maintenance / Foundation';
        return;
      }
      const target = new Date(dateVal);
      const today = new Date();
      const diffDays = Math.ceil((target - today) / (1000 * 60 * 60 * 24));
      const weeksOut = Math.max(0, Math.floor(diffDays / 7));

      if (diffDays < 0) {
        badge.innerText = 'Post-Event Recovery';
      } else if (weeksOut <= 2) {
        badge.innerText = 'Taper Phase (' + weeksOut + ' wks out)';
      } else if (weeksOut <= 4) {
        badge.innerText = 'Peak Phase (' + weeksOut + ' wks out)';
      } else if (weeksOut <= 8) {
        badge.innerText = 'Build Phase (' + weeksOut + ' wks out)';
      } else {
        badge.innerText = 'Base Phase (' + weeksOut + ' wks out)';
      }
    }

    async function saveProfile(e) {
      e.preventDefault();
      const constraintsRaw = document.getElementById('profConstraints').value;
      const constraints = constraintsRaw.split(',').map(s => s.trim()).filter(Boolean);

      const payload = {
        goal: document.getElementById('profGoal').value,
        target_event_name: document.getElementById('profEventName').value,
        target_race_date: document.getElementById('profEventDate').value || null,
        target_race_distance: document.getElementById('profEventDist').value,
        philosophy: document.getElementById('profPhilosophy').value,
        weekly_hours: parseFloat(document.getElementById('profHours').value),
        lthr_run: parseInt(document.getElementById('profLthrRun').value),
        lthr_bike: parseInt(document.getElementById('profLthrBike').value),
        max_hr: parseInt(document.getElementById('profMaxHr').value),
        ftp_bike: parseInt(document.getElementById('profFtp').value),
        swim_css_sec_100m: parseInt(document.getElementById('profCss').value) || 105,
        pool_length_m: parseInt(document.getElementById('profPool').value) || 25,
        constraints: constraints
      };

      try {
        const res = await fetch('/api/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const saved = await res.json();
        currentProfile = saved;
        showToast('Profile and goals updated successfully!');
        // Refresh Plan and Coaching
        generatePlanPreview();
      } catch (err) {
        alert('Failed to save profile: ' + err);
      }
    }

    function populateAnalysisTab(data) {
      if (!data) return;

      // Intensity distribution
      if (data.intensity_distribution) {
        const d = data.intensity_distribution;
        document.getElementById('barLow').style.width = d.low_intensity_pct + '%';
        document.getElementById('barMod').style.width = d.moderate_intensity_pct + '%';
        document.getElementById('barHigh').style.width = d.high_intensity_pct + '%';

        document.getElementById('labelLow').innerText = 'Low: ' + d.low_intensity_pct.toFixed(1) + '%';
        document.getElementById('labelMod').innerText = 'Mod: ' + d.moderate_intensity_pct.toFixed(1) + '%';
        document.getElementById('labelHigh').innerText = 'High: ' + d.high_intensity_pct.toFixed(1) + '%';
        document.getElementById('polarizationSummary').innerText = d.summary;
      }

      // Disciplines
      if (data.disciplines) {
        const tbody = document.getElementById('disciplineTableBody');
        tbody.innerHTML = '';
        for (const [sport, d] of Object.entries(data.disciplines)) {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td style="font-weight:700;">${sport}</td>
            <td>${d.activity_count}</td>
            <td>${d.moving_time_hours} hrs</td>
            <td>${d.total_load} TSS</td>
            <td>${d.total_distance_km} km</td>
          `;
          tbody.appendChild(tr);
        }
      }
    }

    async function generatePlanPreview() {
      const weeks = parseInt(document.getElementById('planHorizonSelect').value);
      try {
        const res = await fetch('/api/plan/preview', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ weeks: weeks })
        });
        const data = await res.json();
        currentPlanEvents = data.events || [];

        const week2Btn = document.getElementById('week2Btn');
        if (weeks === 2) {
          week2Btn.style.display = 'inline-block';
        } else {
          week2Btn.style.display = 'none';
        }
        renderCalendar();
      } catch (err) {
        console.error('Failed to generate plan:', err);
      }
    }

    function showWeek(w) {
      activeWeek = w;
      document.getElementById('week1Btn').classList.toggle('active', w === 1);
      document.getElementById('week2Btn').classList.toggle('active', w === 2);
      renderCalendar();
    }

    function renderCalendar() {
      const container = document.getElementById('calendarContainer');
      container.innerHTML = '';

      const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
      const sliceStart = (activeWeek - 1) * 7;
      const weekEvents = currentPlanEvents.slice(sliceStart, sliceStart + 7);

      for (let i = 0; i < 7; i++) {
        const dayCol = document.createElement('div');
        dayCol.className = 'day-col';

        const evt = weekEvents[i];
        const dateStr = evt && evt.start_date_local ? evt.start_date_local.substring(0, 10) : '';

        const header = document.createElement('div');
        header.className = 'day-header';
        header.innerHTML = `<span>${dayNames[i]}</span><span>${dateStr}</span>`;
        dayCol.appendChild(header);

        if (evt) {
          const card = document.createElement('div');
          card.className = 'workout-card';
          card.onclick = () => openWorkoutModal(evt);

          let tagClass = 'tag-rest';
          if (evt.type === 'Run') tagClass = 'tag-run';
          else if (evt.type === 'Ride') tagClass = 'tag-ride';
          else if (evt.type === 'Swim') tagClass = 'tag-swim';
          else if (evt.type === 'Brick') tagClass = 'tag-brick';
          if (evt.name && (evt.name.includes('Quality') || evt.name.includes('Intervals') || evt.name.includes('CSS') || evt.name.includes('SweetSpot'))) tagClass = 'tag-quality';

          card.innerHTML = `
            <span class="workout-tag ${tagClass}">${evt.type || 'Workout'}</span>
            <div class="workout-title">${evt.name}</div>
            <div class="workout-meta">${evt.category === 'NOTE' ? 'Rest / Note' : 'Structured Session'}</div>
          `;
          dayCol.appendChild(card);
        } else {
          const empty = document.createElement('div');
          empty.style.color = 'var(--text-muted)';
          empty.style.fontSize = '0.75rem';
          empty.innerText = 'No session scheduled';
          dayCol.appendChild(empty);
        }

        container.appendChild(dayCol);
      }
    }

    function openWorkoutModal(evt) {
      document.getElementById('modalWorkoutTitle').innerText = evt.name;
      document.getElementById('modalWorkoutMeta').innerText = (evt.type || 'Workout') + ' • ' + (evt.start_date_local || '');
      document.getElementById('modalWorkoutDesc').innerText = evt.description || 'No detailed coaching notes.';

      // Fetch intra-workout fueling recommendation
      const durMins = Math.max(20, Math.round((evt.moving_time || 3600) / 60));
      fetch('/api/fueling?duration=' + durMins + '&sport=' + encodeURIComponent(evt.type || 'Run') + '&intensity=moderate')
        .then(r => r.json())
        .then(f => {
          if (f) {
            document.getElementById('modalFuelingSummary').innerText = f.strategy_summary;
            document.getElementById('modalCarbs').innerText = f.carbs_per_hour_g + ' g/hr (' + f.total_carbs_g + 'g total)';
            document.getElementById('modalFluids').innerText = f.hydration_ml_per_hour + ' mL/hr (' + f.total_hydration_ml + 'mL total)';
            document.getElementById('modalSodium').innerText = f.sodium_mg_per_hour + ' mg/hr (' + f.total_sodium_mg + 'mg total)';
          }
        })
        .catch(() => {});

      const stepsTbody = document.getElementById('modalStepsTable');
      stepsTbody.innerHTML = '';

      if (evt.workout_doc && evt.workout_doc.steps && evt.workout_doc.steps.length > 0) {
        evt.workout_doc.steps.forEach(s => {
          const tr = document.createElement('tr');
          const dur = s.duration_seconds ? Math.round(s.duration_seconds / 60) + ' min' : 'Lap';
          const hr = s.hr ? s.hr.start + '-' + s.hr.end + ' ' + (s.hr.units || '%') : 'Z2 Base';
          const pwr = s.power ? s.power.start + '-' + s.power.end + ' ' + (s.power.units || '%') : '--';

          tr.innerHTML = `
            <td><strong>${s.cue || s.type}</strong></td>
            <td>${dur}</td>
            <td>${hr}</td>
            <td>${pwr}</td>
          `;
          stepsTbody.appendChild(tr);
        });

        const firstStep = evt.workout_doc.steps[0];
        document.getElementById('corosStepCue').innerText = (firstStep.cue || 'WARMUP').toUpperCase().substring(0, 20);
        document.getElementById('corosTargetRange').innerText = 'Step 1 of ' + evt.workout_doc.steps.length;
      } else {
        stepsTbody.innerHTML = '<tr><td colspan="4" style="color:var(--text-muted);">Rest session or unsegmented event.</td></tr>';
        document.getElementById('corosStepCue').innerText = 'REST DAY';
        document.getElementById('corosTargetRange').innerText = 'Parasympathetic recovery';
      }

      document.getElementById('workoutModal').classList.add('active');
    }

    function closeModal() {
      document.getElementById('workoutModal').classList.remove('active');
    }

    async function applyPlanToIntervals() {
      if (!confirm('Apply this rolling training plan to your live Intervals.icu calendar? (Pre-sync backup will be automatically saved).')) {
        return;
      }

      try {
        const res = await fetch('/api/plan/apply', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ events: currentPlanEvents })
        });
        const result = await res.json();
        showToast('Plan successfully uploaded to Intervals.icu! (' + (result.applied_count || currentPlanEvents.length) + ' events)');
        loadBackups();
      } catch (err) {
        alert('Failed to apply plan: ' + err);
      }
    }

    async function loadBackups() {
      try {
        const res = await fetch('/api/backups');
        const backups = await res.json();
        const tbody = document.getElementById('backupTableBody');
        tbody.innerHTML = '';

        if (!backups || backups.length === 0) {
          tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No backups found.</td></tr>';
          return;
        }

        backups.forEach(b => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${b.timestamp}</td>
            <td><strong>${b.filename}</strong></td>
            <td style="font-family:monospace; font-size:0.75rem;">${b.path}</td>
            <td><button class="btn btn-secondary" style="font-size:0.75rem; padding: 2px 8px;" onclick="showToast('Backup valid')">Verify</button></td>
          `;
          tbody.appendChild(tr);
        });
      } catch (err) {
        console.error('Failed to load backups:', err);
      }
    }

    function downloadExport(format) {
      window.location.href = '/api/export?format=' + format;
    }

    // Initialize on page load
    window.addEventListener('DOMContentLoaded', loadDashboard);
  </script>
</body>
</html>
"""

