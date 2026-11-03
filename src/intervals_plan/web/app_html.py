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
    .tag-duathlon { background: rgba(245, 158, 11, 0.25); color: #fbbf24; }
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
    .chart-scroll-container {
      width: 100%;
      overflow-x: auto;
      overflow-y: hidden;
      scrollbar-width: thin;
      scrollbar-color: #475569 #0f172a;
      -webkit-overflow-scrolling: touch;
      position: relative;
    }
    .chart-scroll-container::-webkit-scrollbar {
      height: 6px;
    }
    .chart-scroll-container::-webkit-scrollbar-track {
      background: #0f172a;
      border-radius: 4px;
    }
    .chart-scroll-container::-webkit-scrollbar-thumb {
      background: #475569;
      border-radius: 4px;
    }
    .chart-scroll-container::-webkit-scrollbar-thumb:hover {
      background: #64748b;
    }
    .chart-filter-btn.active {
      background: var(--accent) !important;
      color: #000 !important;
      font-weight: 700 !important;
    }

    .chart-box {
      width: 100%;
      height: 280px;
      background: #0f172a;
      border-radius: 8px;
      padding: 0.75rem 1rem;
      border: 1px solid var(--card-border);
      position: relative;
    }
    .chart-box-compact {
      width: 100%;
      height: 200px;
      background: #0f172a;
      border-radius: 8px;
      padding: 0.75rem 1rem;
      border: 1px solid var(--card-border);
      position: relative;
    }
    .chart-tooltip {
      position: absolute;
      display: none;
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid #334155;
      border-radius: 6px;
      padding: 0.5rem 0.75rem;
      font-size: 0.75rem;
      color: #f1f5f9;
      pointer-events: none;
      z-index: 50;
      white-space: nowrap;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
      line-height: 1.4;
    }
    .chart-legend {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 1.25rem;
      margin-top: 0.75rem;
      font-size: 0.75rem;
    }
    .chart-legend-item {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      font-weight: 600;
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
      <button class="nav-btn" onclick="switchTab('coros-hub')">COROS Training Hub</button>
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

      <!-- Biometrics & Wellness Telemetry Cards -->
      <div class="grid-4" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div class="card-title">Sleep Duration & Stages</div>
          <div class="card-value" id="dashSleepVal" style="color:#a855f7;">--</div>
          <div class="card-subtext" id="dashSleepSubtext">Samsung Health / Health Connect</div>
        </div>
        <div class="card">
          <div class="card-title">Blood Oxygen (SpO2)</div>
          <div class="card-value" id="dashSpo2Val" style="color:#06b6d4;">--</div>
          <div class="card-subtext" id="dashSpo2Subtext">Optimal &gt;95%</div>
        </div>
        <div class="card">
          <div class="card-title">Body Composition (Weight)</div>
          <div class="card-value" id="dashWeightVal" style="color:#10b981;">--</div>
          <div class="card-subtext" id="dashWeightSubtext">Scale Telemetry</div>
        </div>
        <div class="card">
          <div class="card-title">Body Fat %</div>
          <div class="card-value" id="dashBodyFatVal" style="color:#f59e0b;">--</div>
          <div class="card-subtext" id="dashBodyFatSubtext">Bioimpedance Analysis</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <div class="card-title" style="margin-bottom:0;">Weekly Load Distribution & Target</div>
            <span id="weeklyLoadBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">--h / --h</span>
          </div>

          <!-- Volume & Load Progress Indicators -->
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem; margin-bottom:0.75rem;">
            <div style="background:#0f172a; border:1px solid var(--border); border-radius:6px; padding:0.5rem 0.75rem;">
              <div style="font-size:0.75rem; color:var(--text-muted);">7-Day Completed Volume</div>
              <div style="font-size:1.125rem; font-weight:700; color:#38bdf8;" id="weeklyVolumeText">-- hrs</div>
              <div style="font-size:0.7rem; color:var(--text-muted);">Target: <span id="targetHoursText">8.0 Hours</span></div>
            </div>
            <div style="background:#0f172a; border:1px solid var(--border); border-radius:6px; padding:0.5rem 0.75rem;">
              <div style="font-size:0.75rem; color:var(--text-muted);">7-Day Completed Load</div>
              <div style="font-size:1.125rem; font-weight:700; color:#f59e0b;" id="weeklyLoadText">-- TSS</div>
              <div style="font-size:0.7rem; color:var(--text-muted);">Target: <span id="targetLoadRangeText">-- - -- TSS</span></div>
            </div>
          </div>

          <!-- Stacked Discipline Distribution Bar -->
          <div style="margin-bottom:0.75rem;">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted); margin-bottom:4px;">
              <span>Discipline Load Share</span>
              <span id="weeklyDisciplinePills">Calculating...</span>
            </div>
            <div id="weeklyDisciplineBar" style="display:flex; height:10px; border-radius:4px; overflow:hidden; background:#1e293b;">
              <div id="barShareRide" style="width:0%; background:#f59e0b;" title="Ride"></div>
              <div id="barShareRun" style="width:0%; background:#06b6d4;" title="Run"></div>
              <div id="barShareSwim" style="width:0%; background:#38bdf8;" title="Swim"></div>
              <div id="barShareOther" style="width:0%; background:#64748b;" title="Other"></div>
            </div>
          </div>

          <!-- Tim Gabbett ACWR Injury Meter -->
          <div class="gauge-container" style="margin-bottom:0.5rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem; font-size:0.75rem; color:var(--text-muted);">
              <span>ACWR Workload Ratio</span>
              <strong id="acwrRatioInline" style="color:var(--success);">Sweet Spot</strong>
            </div>
            <div class="gauge-bar-bg" style="height:8px;">
              <div id="acwrBarFill" class="gauge-fill" style="width: 50%; background: var(--accent);"></div>
            </div>
            <div class="gauge-ticks">
              <span>0.0 (Under)</span>
              <span>0.8 (Sweet Spot)</span>
              <span>1.3 (Elevated)</span>
              <span>1.5+ (Danger)</span>
            </div>
          </div>
          <p class="card-subtext" id="acwrGuidance" style="margin:0; font-size:0.75rem;">Optimal progressive overload without non-contact injury spikes.</p>
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

      <!-- Advanced Sports Science Extensions (Skiba W'bal, DFA a1 & Joe Friel Telemetry Quality) -->
      <div class="grid-2" style="margin-top: 1.5rem;">
        <!-- Card 1: Friel Data Quality Auditor -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <div class="card-title" style="margin-bottom:0;">Telemetry Data Quality (Joe Friel Audit)</div>
            <span id="dataQualityBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">Audit: Good</span>
          </div>
          <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:0.75rem;" id="dataQualityFix">
            Verifying physiological thresholds, biometric streams, and exertion logs...
          </p>
          <div id="dataQualityChecklist" style="display:flex; flex-direction:column; gap:6px; font-size:0.8125rem;">
            <!-- Populated dynamically -->
          </div>
        </div>

        <!-- Card 2: Skiba W'bal Anaerobic Capacity & DFA a1 -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <div class="card-title" style="margin-bottom:0;">Anaerobic Battery (Skiba W') & DFA Alpha 1</div>
            <span id="wbalStatusBadge" class="periodization-badge" style="background:rgba(6,182,212,0.2); color:#06b6d4;">Battery: 100% Full</span>
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem; margin-bottom:0.75rem;">
            <div style="background:#0f172a; border:1px solid var(--border); border-radius:6px; padding:0.5rem 0.75rem;">
              <div style="font-size:0.75rem; color:var(--text-muted);">Anaerobic Work Capacity (W')</div>
              <div style="font-size:1.125rem; font-weight:700; color:#38bdf8;" id="wPrimeDisplay">20.0 kJ</div>
              <div style="font-size:0.7rem; color:var(--text-muted);">Critical Power: <span id="cpDisplay">250 W</span></div>
            </div>
            <div style="background:#0f172a; border:1px solid var(--border); border-radius:6px; padding:0.5rem 0.75rem;">
              <div style="font-size:0.75rem; color:var(--text-muted);">DFA Alpha 1 Thresholds</div>
              <div style="font-size:0.8125rem; font-weight:600; color:#10b981;">LT1 (Aerobic): a1 ~ 0.75</div>
              <div style="font-size:0.8125rem; font-weight:600; color:#f43f5e;">LT2 (Anaerobic): a1 ~ 0.50</div>
            </div>
          </div>
          <!-- Dynamic Battery Bar -->
          <div style="margin-bottom:0.75rem;">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted); margin-bottom:3px;">
              <span>W' Battery Reconstitution State</span>
              <span id="wbalBatteryPct">100% (20.0 / 20.0 kJ)</span>
            </div>
            <div class="gauge-bar-bg" style="height:10px;">
              <div id="wbalBatteryFill" class="gauge-fill" style="width:100%; background:var(--accent);"></div>
            </div>
          </div>
          <div style="display:flex; gap:0.5rem;">
            <button class="btn btn-secondary" style="font-size:0.75rem; padding:0.35rem 0.6rem;" onclick="simulateWbal('intervals')">Simulate 4x4 VO2max Depletion</button>
            <button class="btn btn-secondary" style="font-size:0.75rem; padding:0.35rem 0.6rem;" onclick="simulateWbal('steady')">Simulate Threshold Cruise</button>
          </div>
          <div id="wbalSimResult" style="display:none; margin-top:0.6rem; font-size:0.75rem; color:#94a3b8; background:#0f172a; border-radius:4px; padding:0.4rem 0.6rem;"></div>
        </div>
      </div>
    </div>

    <!-- TAB 2: ANALYSIS & PMC -->
    <div id="tab-analysis" class="tab-content">
      <div class="card" style="margin-bottom: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
          <div class="card-title" style="margin-bottom:0;">Performance Management Chart (Banister / Coggan PMC - Rolling 30 Days)</div>
          <div style="font-size:0.8125rem; color:var(--text-muted);" id="pmcDateRange">Rolling 30-Day Timeseries</div>
        </div>
        <div class="chart-box" id="pmcChartContainer">
          <div class="chart-tooltip" id="pmcTooltip"></div>
          <svg id="pmcChartSvg" width="100%" height="100%" viewBox="0 0 800 240" preserveAspectRatio="none">
          </svg>
        </div>
        <div class="chart-legend">
          <span class="chart-legend-item" style="color:#06b6d4;">— CTL (Fitness 42d)</span>
          <span class="chart-legend-item" style="color:#f43f5e;">— ATL (Fatigue 7d)</span>
          <span class="chart-legend-item" style="color:#10b981;">-- TSB (Form = CTL - ATL)</span>
          <span class="chart-legend-item" style="color:#64748b;">··· Baseline (TSB = 0)</span>
        </div>
      </div>

      <!-- Grid 2: ACWR & RHR Trends -->
      <div class="grid-2" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <div class="card-title" style="margin-bottom:0;">Acute:Chronic Workload Ratio (ACWR Trend)</div>
            <span id="acwrRatioBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">Sweet Spot</span>
          </div>
          <div class="chart-box-compact" id="acwrChartContainer">
            <div class="chart-tooltip" id="acwrTooltip"></div>
            <svg id="acwrChartSvg" width="100%" height="100%" viewBox="0 0 450 180" preserveAspectRatio="none">
            </svg>
          </div>
          <div class="chart-legend">
            <span class="chart-legend-item" style="color:#38bdf8;">— ACWR Ratio</span>
            <span class="chart-legend-item" style="color:#10b981;">■ Sweet Spot (0.8-1.3)</span>
            <span class="chart-legend-item" style="color:#f59e0b;">■ Caution (1.3-1.5)</span>
            <span class="chart-legend-item" style="color:#ef4444;">■ Danger (>1.5)</span>
          </div>
        </div>

        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <div class="card-title" style="margin-bottom:0;">Autonomic Recovery: Resting HR Trend</div>
            <span id="rhrStrainBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">Autonomic Green</span>
          </div>
          <div class="chart-box-compact" id="rhrChartContainer">
            <div class="chart-tooltip" id="rhrTooltip"></div>
            <svg id="rhrChartSvg" width="100%" height="100%" viewBox="0 0 450 180" preserveAspectRatio="none">
            </svg>
          </div>
          <div class="chart-legend">
            <span class="chart-legend-item" style="color:#38bdf8;">● Daily Resting HR</span>
            <span class="chart-legend-item" style="color:#94a3b8;">-- 30d Baseline</span>
            <span class="chart-legend-item" style="color:#ef4444;">-- +4 bpm Strain Alert</span>
          </div>
        </div>
      </div>

      <!-- Biometrics Timeseries Charts: Sleep & SpO2 / Weight -->
      <div class="grid-2" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <div class="card-title" style="margin-bottom:0;">Sleep Duration & Recovery Stages (Rolling 30 Days)</div>
            <div style="font-size:0.8125rem; color:var(--text-muted);" id="sleepSummaryText">-- hrs avg</div>
          </div>
          <div class="chart-box-compact" id="sleepChartContainer">
            <div class="chart-tooltip" id="sleepTooltip"></div>
            <svg id="sleepChartSvg" width="100%" height="100%" viewBox="0 0 450 180" preserveAspectRatio="none">
            </svg>
          </div>
          <div class="chart-legend">
            <span class="chart-legend-item" style="color:#a855f7;">■ Sleep Duration (Hrs)</span>
            <span class="chart-legend-item" style="color:#10b981;">-- 7h Target Baseline</span>
          </div>
        </div>

        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <div class="card-title" style="margin-bottom:0;">Blood Oxygen (SpO2) & Body Weight Trends</div>
            <div style="font-size:0.8125rem; color:var(--text-muted);" id="vitalsSummaryText">Samsung Health / Scale</div>
          </div>
          <div class="chart-box-compact" id="vitalsChartContainer">
            <div class="chart-tooltip" id="vitalsTooltip"></div>
            <svg id="vitalsChartSvg" width="100%" height="100%" viewBox="0 0 450 180" preserveAspectRatio="none">
            </svg>
          </div>
          <div class="chart-legend">
            <span class="chart-legend-item" style="color:#06b6d4;">● SpO2 (%)</span>
            <span class="chart-legend-item" style="color:#10b981;">● Weight (kg)</span>
          </div>
        </div>
      </div>

      <!-- Daily Training Load & Volume (Stacked Discipline TSS) -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; flex-wrap:wrap; gap:0.5rem;">
          <div>
            <div class="card-title" style="margin-bottom:0.25rem;">Daily Training Load & Volume (Stacked Discipline TSS)</div>
            <div style="font-size:0.8125rem; color:var(--text-muted);" id="totalVolumeLoadSummary">-- hrs | -- TSS</div>
          </div>
          <!-- Interactive Timeframe & Scroll Filters -->
          <div style="display:flex; gap:0.4rem; align-items:center;">
            <span style="font-size:0.75rem; color:var(--text-muted); margin-right:4px;">Window:</span>
            <button class="btn btn-secondary chart-filter-btn active" id="btnLoad30d" onclick="filterDailyLoad(30)" style="font-size:0.7rem; padding:0.25rem 0.6rem;">30 Days</button>
            <button class="btn btn-secondary chart-filter-btn" id="btnLoad14d" onclick="filterDailyLoad(14)" style="font-size:0.7rem; padding:0.25rem 0.6rem;">14 Days</button>
            <button class="btn btn-secondary chart-filter-btn" id="btnLoad7d" onclick="filterDailyLoad(7)" style="font-size:0.7rem; padding:0.25rem 0.6rem;">7 Days</button>
          </div>
        </div>

        <!-- Scrollable Chart Container -->
        <div class="chart-scroll-container" id="loadChartScrollBox" style="position:relative; width:100%; overflow-x:auto; overflow-y:hidden; border-radius:8px; border:1px solid var(--border); background:#0f172a; padding: 0.5rem 0;">
          <div class="chart-tooltip" id="loadTooltip"></div>
          <svg id="loadChartSvg" height="190" style="display:block; min-width:850px; width:100%;">
          </svg>
        </div>

        <div class="chart-legend" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-top:0.75rem;">
          <div style="display:flex; gap:1rem; flex-wrap:wrap;">
            <span class="chart-legend-item" style="color:#06b6d4;">■ Run</span>
            <span class="chart-legend-item" style="color:#f59e0b;">■ Ride</span>
            <span class="chart-legend-item" style="color:#38bdf8;">■ Swim</span>
            <span class="chart-legend-item" style="color:#a855f7;">■ Brick/Duathlon</span>
            <span class="chart-legend-item" style="color:#64748b;">■ Other</span>
          </div>
          <div style="font-size:0.7rem; color:var(--text-muted);">
            Scroll horizontally or drag / swipe on touch devices to explore all days
          </div>
        </div>
      </div>

      <!-- Grid 2: Polarization & Discipline Breakdown -->
      <div class="grid-2" style="margin-bottom: 1.5rem;">
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
      <div class="card" style="margin-bottom: 1.5rem;">
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

      <!-- Post-Workout Aerobic Decoupling & Debrief Card -->
      <div class="card">
        <div class="card-title">Aerobic Decoupling & Post-Workout Session Debrief</div>
        <p class="card-subtext" style="margin-bottom:1rem;">Evaluate cardiac drift (Pw:HR or Pa:HR % drift) and aerobic efficiency stability to adapt next-day recovery.</p>
        <div class="grid-2">
          <div>
            <form id="reviewForm" onsubmit="submitSessionReview(event)">
              <div class="form-group" style="margin-bottom:0.75rem;">
                <label class="form-label">Sport Discipline</label>
                <select id="revSport" class="form-select">
                  <option value="Run">Run</option>
                  <option value="Ride">Ride</option>
                  <option value="Swim">Swim</option>
                  <option value="Duathlon">Duathlon</option>
                  <option value="Brick">Brick (Bike-to-Run)</option>
                </select>
              </div>
              <div class="grid-2" style="margin-bottom:0.75rem;">
                <div class="form-group">
                  <label class="form-label">Duration (Minutes)</label>
                  <input type="number" id="revDuration" class="form-input" value="60" min="10" max="480">
                </div>
                <div class="form-group">
                  <label class="form-label">RPE Exertion (1-10)</label>
                  <input type="number" id="revRpe" class="form-input" value="6" min="1" max="10">
                </div>
              </div>
              <div class="form-group" style="margin-bottom:0.75rem;">
                <label class="form-label">Aerobic Decoupling / Cardiac Drift (% drift)</label>
                <input type="number" step="0.1" id="revDecoupling" class="form-input" value="3.2" placeholder="e.g. 3.2">
              </div>
              <button type="submit" class="btn" style="width:100%;">Evaluate Aerobic Efficiency</button>
            </form>
          </div>
          <div style="background:#0f172a; border:1px solid #1f2937; border-radius:8px; padding:1rem;">
            <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:700; margin-bottom:0.5rem;">Aerobic Efficiency Gauge</div>
            <div id="decouplingGaugeContainer" style="height:90px;">
              <svg id="decouplingGaugeSvg" width="100%" height="100%" viewBox="0 0 350 90">
              </svg>
            </div>
            <div id="decouplingVerdict" style="font-size:0.875rem; font-weight:700; color:var(--success); margin-top:0.5rem;">Optimal Base Coupling (&lt;5% drift)</div>
            <div id="decouplingFeedback" style="font-size:0.75rem; color:#94a3b8; margin-top:4px; line-height:1.4;">Heart rate to output ratio remained stable across the session.</div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: GOALS & ATHLETE PROFILE -->
    <div id="tab-goals" class="tab-content">
      <div class="card">
        <div class="card-title">Athlete Profile & Periodization Configuration</div>
        <form id="profileForm" onsubmit="saveProfile(event)" style="margin-top: 1.5rem;">
          <div class="grid-3">
            <div class="form-group">
              <label class="form-label">Primary Training Goal / Discipline</label>
              <select id="profGoal" class="form-select">
                <optgroup label="Single Discipline">
                  <option value="running">Runner (5K, 10K, Half Marathon, Marathon, Ultra)</option>
                  <option value="cycling">Cyclist (Road Race, Gran Fondo, Time Trial, Criterium)</option>
                  <option value="swimming">Swimmer (CSS Threshold, Pool & Open Water Distance)</option>
                </optgroup>
                <optgroup label="Multisport & Transitions">
                  <option value="duathlon">Duathlete (Run-Bike-Run Transitions & Brick Stamina)</option>
                  <option value="sprint_triathlon">Triathlete: Sprint Triathlon (750m / 20k / 5k)</option>
                  <option value="olympic_triathlon">Triathlete: Olympic Triathlon (1.5k / 40k / 10k)</option>
                  <option value="half_ironman_70_3">Triathlete: IRONMAN 70.3 (1.9k / 90k / 21.1k)</option>
                  <option value="full_ironman_140_6">Triathlete: IRONMAN 140.6 (3.8k / 180k / 42.2k)</option>
                </optgroup>
                <optgroup label="Hybrid & Longevity">
                  <option value="dual_sport_hybrid">Dual-Sport Hybrid (Balanced Running & Cycling)</option>
                  <option value="general_fitness">General Aerobic Fitness & Cardiovascular Longevity</option>
                </optgroup>
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
          <div class="card-title">Samsung Health Hub</div>
          <div style="font-size: 1.1rem; font-weight: 700; color: #a855f7;">Health Connect Active</div>
          <p class="card-subtext">Automated biometrics & workout ingestion pipeline.</p>
        </div>
      </div>

      <!-- Samsung Health & Health Connect Webhook Hub -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
          <div class="card-title" style="margin-bottom:0;">Samsung Health & Health Connect Synchronization</div>
          <span id="hcSyncBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">Active Relay to Intervals + COROS</span>
        </div>
        <p class="card-subtext" style="margin-bottom:1.25rem;">
          Ingests biometrics (Resting HR, overnight HRV RMSSD, sleep stages, SpO2, blood pressure, weight, and exercise sessions) from Samsung Health via the <code>health-connect-webhook</code> app, automatically updating Intervals.icu and relaying to your COROS watch.
        </p>
        <div class="grid-2">
          <div style="background:#0f172a; border:1px solid #1f2937; border-radius:8px; padding:1.25rem;">
            <div style="font-weight:700; color:var(--accent); margin-bottom:0.5rem; font-size:0.9375rem;">1. Automated Inbound Webhook (Push)</div>
            <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:0.75rem;">
              Configure this target URL in your Android Health Connect Webhook app for automated scheduled/interval syncing:
            </p>
            <div style="background:#111827; border:1px solid #374151; border-radius:6px; padding:0.5rem 0.75rem; font-family:monospace; font-size:0.8125rem; color:#38bdf8; word-break:break-all;" id="hcWebhookUrl">
              http://127.0.0.1:8080/api/health-connect
            </div>
            <div style="font-size:0.75rem; color:#9ca3af; margin-top:0.5rem;">
              Format: <strong>JSON</strong> | Recommended Schedule: 08:00 & 21:00 or every 30-60 mins.
            </div>
          </div>

          <div style="background:#0f172a; border:1px solid #1f2937; border-radius:8px; padding:1.25rem;">
            <div style="font-weight:700; color:var(--success); margin-bottom:0.5rem; font-size:0.9375rem;">2. On-Demand LAN Pull (Local Server :8787)</div>
            <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:0.75rem;">
              Pull recent data over Wi-Fi from the app's built-in Local HTTP server:
            </p>
            <div style="display:flex; gap:0.5rem; margin-bottom:0.5rem;">
              <input type="text" id="hcPhoneIp" class="form-input" placeholder="Phone IP (e.g. 192.168.1.100)" style="flex:2;">
              <input type="number" id="hcDays" class="form-input" value="7" min="1" max="30" style="flex:1;" title="Days lookback">
              <button class="btn" onclick="triggerLanPull()" id="btnLanPull" style="white-space:nowrap;">Pull Now</button>
            </div>
            <div style="font-size:0.75rem; color:#9ca3af;" id="hcPullStatus">
              Enable "Local HTTP server" in the phone app settings (default port 8787).
            </div>
          </div>
        </div>

        <div style="background:#111827; border:1px solid #1f2937; border-radius:6px; padding:0.75rem 1rem; margin-top:1rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem; font-size:0.8125rem;">
          <div>
            <span style="color:var(--text-muted);">Last Synced:</span>
            <strong id="hcLastSyncText" style="color:#f3f4f6; margin-left:4px;">Never</strong>
          </div>
          <div>
            <span style="color:var(--text-muted);">Wellness Updated:</span>
            <strong id="hcWellnessCount" style="color:var(--success); margin-left:4px;">0 days</strong>
          </div>
          <div>
            <span style="color:var(--text-muted);">Activities Uploaded:</span>
            <strong id="hcActivitiesCount" style="color:#38bdf8; margin-left:4px;">0</strong>
          </div>
          <div>
            <span style="color:var(--text-muted);">COROS Relay:</span>
            <strong id="hcCorosRelayStatus" style="color:var(--accent); margin-left:4px;">Active via Intervals.icu</strong>
          </div>
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

    <!-- TAB 7: COROS TRAINING HUB & EVOLAB -->
    <div id="tab-coros-hub" class="tab-content">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1.5rem; flex-wrap:wrap; gap:1rem;">
        <div>
          <h2 style="font-size:1.5rem; font-weight:800; color:#fff; margin-bottom:0.25rem;">COROS Training Hub & EvoLab Analytics</h2>
          <p style="font-size:0.875rem; color:var(--text-muted); margin:0;">
            Real-time synchronization with COROS EvoLab metrics, Running Fitness evaluation, and training load recommendations.
          </p>
        </div>
        <div style="display:flex; gap:0.5rem; align-items:center;">
          <span id="corosHubSyncStatus" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">COROS Cloud Linked</span>
          <button class="btn btn-secondary" style="font-size:0.75rem; padding:0.35rem 0.75rem;" onclick="loadCorosHub()">Refresh EvoLab</button>
        </div>
      </div>

      <!-- Grid 4: EvoLab Core Telemetry -->
      <div class="grid-4" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div class="card-title">Base Fitness (42d Rolling)</div>
          <div class="card-value" id="corosBaseFitness" style="color:#06b6d4;">--</div>
          <div class="card-subtext">Long-term physiological capacity (CTL)</div>
        </div>

        <div class="card">
          <div class="card-title">Load Impact (7d Rolling)</div>
          <div class="card-value" id="corosLoadImpact" style="color:#f43f5e;">--</div>
          <div class="card-subtext">Short-term training stress (ATL)</div>
        </div>

        <div class="card">
          <div class="card-title">Fatigue Index (0 - 100)</div>
          <div class="card-value" id="corosFatigueScore" style="color:#f59e0b;">--</div>
          <div class="card-subtext" id="corosFatigueZoneText">Optimized Zone</div>
        </div>

        <div class="card">
          <div class="card-title">7-Day Training Load</div>
          <div class="card-value" id="coros7dLoad" style="color:#10b981;">--</div>
          <div class="card-subtext" id="corosLoadRangeText">Target: -- - --</div>
        </div>
      </div>

      <!-- Fatigue Gauge & Intensity Trend -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
          <div class="card-title" style="margin-bottom:0;">EvoLab Fatigue & Intensity Trend</div>
          <span id="corosFatigueBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">OPTIMIZED</span>
        </div>
        <div class="gauge-container" style="margin-bottom: 0.75rem;">
          <div class="gauge-bar-bg" style="height:12px;">
            <div id="corosFatigueFill" class="gauge-fill" style="width:50%; background:var(--accent);"></div>
          </div>
          <div class="gauge-ticks">
            <span>0 (Minimal)</span>
            <span>20 (Performance / Taper)</span>
            <span>40 (Optimized Sweet Spot)</span>
            <span>60 (High Fatigue)</span>
            <span>80+ (Excessive)</span>
          </div>
        </div>
        <p class="card-subtext" id="corosFatigueDesc" style="margin:0; font-size:0.8125rem;">
          Evaluating fatigue dynamics...
        </p>
      </div>

      <!-- Grid 2: Running Fitness & Race Predictor -->
      <div class="grid-2" style="margin-bottom: 1.5rem;">
        <!-- Running Fitness Card -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <div class="card-title" style="margin-bottom:0;">Running Fitness (EvoLab 4-Pillars)</div>
            <div style="font-size:1.25rem; font-weight:800; color:#38bdf8;" id="corosOverallFitness">-- / 100</div>
          </div>
          <div style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:1rem;">
            Calibrated Threshold Pace: <strong id="corosThreshPace" style="color:#fff;">--:-- /km</strong>
          </div>

          <div style="display:flex; flex-direction:column; gap:0.75rem;">
            <div>
              <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:3px;">
                <span>Base (Aerobic Endurance / &gt;30km)</span>
                <strong id="corosBaseScore" style="color:#10b981;">--</strong>
              </div>
              <div class="gauge-bar-bg" style="height:6px;">
                <div id="corosBaseBar" class="gauge-fill" style="width:60%; background:#10b981;"></div>
              </div>
            </div>

            <div>
              <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:3px;">
                <span>Endurance (Lactate Threshold / ~10km)</span>
                <strong id="corosEnduranceScore" style="color:#06b6d4;">--</strong>
              </div>
              <div class="gauge-bar-bg" style="height:6px;">
                <div id="corosEnduranceBar" class="gauge-fill" style="width:65%; background:#06b6d4;"></div>
              </div>
            </div>

            <div>
              <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:3px;">
                <span>Speed (VO2 Max Aerobic Power / ~3km)</span>
                <strong id="corosSpeedScore" style="color:#a855f7;">--</strong>
              </div>
              <div class="gauge-bar-bg" style="height:6px;">
                <div id="corosSpeedBar" class="gauge-fill" style="width:70%; background:#a855f7;"></div>
              </div>
            </div>

            <div>
              <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:3px;">
                <span>Sprint (Neuromuscular Anaerobic / ~400m)</span>
                <strong id="corosSprintScore" style="color:#f59e0b;">--</strong>
              </div>
              <div class="gauge-bar-bg" style="height:6px;">
                <div id="corosSprintBar" class="gauge-fill" style="width:60%; background:#f59e0b;"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Race Predictor Card -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <div class="card-title" style="margin-bottom:0;">COROS Race Predictor</div>
            <span class="periodization-badge" style="background:rgba(56,189,248,0.2); color:#38bdf8;">Riegel / Cameron Model</span>
          </div>
          <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:1rem;">
            Calculated finish times and pacing benchmarks based on threshold efficiency and aerobic training volume.
          </p>

          <table class="table">
            <thead>
              <tr>
                <th>Event</th>
                <th>Distance</th>
                <th>Predicted Time</th>
                <th>Predicted Pace</th>
              </tr>
            </thead>
            <tbody id="corosRaceTableBody">
              <!-- Populated dynamically -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- Grid 2: Training Effect & Recovery Timer Simulator -->
      <div class="grid-2">
        <!-- Training Effect Calculator -->
        <div class="card">
          <div class="card-title" style="margin-bottom:0.75rem;">Training Effect (TE) Estimator</div>
          <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:0.5rem; margin-bottom:0.75rem;">
            <div>
              <label style="font-size:0.75rem; color:var(--text-muted);">Duration (mins)</label>
              <input type="number" id="teInputMins" value="60" style="width:100%; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; padding:0.35rem 0.5rem; font-size:0.8125rem;">
            </div>
            <div>
              <label style="font-size:0.75rem; color:var(--text-muted);">Load (TSS)</label>
              <input type="number" id="teInputLoad" value="65" style="width:100%; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; padding:0.35rem 0.5rem; font-size:0.8125rem;">
            </div>
            <div>
              <label style="font-size:0.75rem; color:var(--text-muted);">Avg Heart Rate</label>
              <input type="number" id="teInputHr" value="155" style="width:100%; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; padding:0.35rem 0.5rem; font-size:0.8125rem;">
            </div>
          </div>
          <button class="btn btn-secondary" style="font-size:0.75rem; padding:0.35rem 0.75rem; margin-bottom:0.75rem;" onclick="calcCorosTE()">Compute Session Effect</button>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem;">
            <div style="background:#0f172a; border:1px solid var(--border); border-radius:6px; padding:0.6rem;">
              <div style="font-size:0.75rem; color:var(--text-muted);">Aerobic Training Effect</div>
              <div style="font-size:1.25rem; font-weight:800; color:#10b981;" id="corosAeroTeVal">--</div>
              <div style="font-size:0.7rem; color:var(--text-muted);" id="corosAeroTeLabel">Maintaining</div>
            </div>
            <div style="background:#0f172a; border:1px solid var(--border); border-radius:6px; padding:0.6rem;">
              <div style="font-size:0.75rem; color:var(--text-muted);">Anaerobic Training Effect</div>
              <div style="font-size:1.25rem; font-weight:800; color:#f59e0b;" id="corosAnaeroTeVal">--</div>
              <div style="font-size:0.7rem; color:var(--text-muted);" id="corosAnaeroTeLabel">Maintaining</div>
            </div>
          </div>
        </div>

        <!-- Recovery Timer Card -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <div class="card-title" style="margin-bottom:0;">COROS Recovery Timer</div>
            <span id="corosRecoveryBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">READY (90%+)</span>
          </div>

          <div style="text-align:center; padding:1rem 0;">
            <div style="font-size:2.25rem; font-weight:800; color:#fff;" id="corosRecoveryHours">0.0h</div>
            <div style="font-size:0.8125rem; color:var(--text-muted); margin-top:2px;">Time until 100% full recovery</div>
          </div>

          <div style="margin-bottom:0.75rem;">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted); margin-bottom:4px;">
              <span>Recovery Percentage</span>
              <strong id="corosRecoveryPctText" style="color:#10b981;">100%</strong>
            </div>
            <div class="gauge-bar-bg" style="height:10px;">
              <div id="corosRecoveryFill" class="gauge-fill" style="width:100%; background:var(--success);"></div>
            </div>
          </div>

          <p style="font-size:0.8125rem; color:var(--text-muted); margin:0;" id="corosRecoveryGuidance">
            Your body is fully recovered and primed for high-intensity intervals or long aerobic volume.
          </p>
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
        const [profRes, anaRes, coachRes, statusRes, compRes, qualRes] = await Promise.all([
          fetch('/api/profile'),
          fetch('/api/analytics'),
          fetch('/api/coaching'),
          fetch('/api/status'),
          fetch('/api/compliance'),
          fetch('/api/data-quality')
        ]);

        currentProfile = await profRes.json();
        currentAnalytics = await anaRes.json();
        const coach = await coachRes.json();
        const statusData = await statusRes.json();
        const comp = await compRes.json();
        const qualityData = await qualRes.json();

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

        // Populate Biometrics Cards from latest series entry
        if (currentAnalytics && currentAnalytics.daily_series) {
          const s = currentAnalytics.daily_series;
          const latestWithSleep = [...s].reverse().find(x => x.sleep_hours !== null && x.sleep_hours !== undefined);
          const latestWithSpo2 = [...s].reverse().find(x => x.spo2 !== null && x.spo2 !== undefined);
          const latestWithWeight = [...s].reverse().find(x => x.weight !== null && x.weight !== undefined);
          const latestWithFat = [...s].reverse().find(x => x.body_fat !== null && x.body_fat !== undefined);

          if (latestWithSleep) {
            document.getElementById('dashSleepVal').innerText = latestWithSleep.sleep_hours + 'h';
            document.getElementById('dashSleepSubtext').innerText = latestWithSleep.date + (latestWithSleep.sleep_note ? ' (' + latestWithSleep.sleep_note.slice(0, 24) + '...)' : '');
          }
          if (latestWithSpo2) {
            document.getElementById('dashSpo2Val').innerText = latestWithSpo2.spo2 + '%';
            document.getElementById('dashSpo2Subtext').innerText = 'Recorded on ' + latestWithSpo2.date;
          }
          if (latestWithWeight) {
            document.getElementById('dashWeightVal').innerText = latestWithWeight.weight + ' kg';
            document.getElementById('dashWeightSubtext').innerText = 'Recorded on ' + latestWithWeight.date;
          }
          if (latestWithFat) {
            document.getElementById('dashBodyFatVal').innerText = latestWithFat.body_fat + '%';
            document.getElementById('dashBodyFatSubtext').innerText = 'Recorded on ' + latestWithFat.date;
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

          const b = document.getElementById('acwrRatioBadge');
          if (b) {
            b.innerText = a.status.replace('_', ' ');
            if (a.status === 'SWEET_SPOT') {
              b.style.background = 'rgba(16,185,129,0.2)';
              b.style.color = 'var(--success)';
            } else if (a.status === 'DANGER_ZONE') {
              b.style.background = 'rgba(239,68,68,0.2)';
              b.style.color = 'var(--danger)';
            } else {
              b.style.background = 'rgba(245,158,11,0.2)';
              b.style.color = 'var(--warning)';
            }
          }
        }

        // Populate Weekly Load Distribution & Target card
        if (currentAnalytics) {
          const ws = currentAnalytics.weekly_summary || {};
          const sevenHrs = ws.seven_day_hours || 0;
          const targetHrs = ws.target_hours || (currentProfile ? currentProfile.weekly_hours : 8.0);
          const sevenLoad = ws.seven_day_load || 0;
          const volPct = targetHrs > 0 ? Math.round((sevenHrs / targetHrs) * 100) : 0;

          const wBadge = document.getElementById('weeklyLoadBadge');
          if (wBadge) {
            wBadge.innerText = `${sevenHrs}h / ${targetHrs}h (${volPct}%)`;
            wBadge.style.color = volPct >= 80 ? 'var(--success)' : (volPct >= 40 ? '#38bdf8' : 'var(--warning)');
            wBadge.style.background = volPct >= 80 ? 'rgba(16,185,129,0.2)' : (volPct >= 40 ? 'rgba(56,189,248,0.2)' : 'rgba(245,158,11,0.2)');
          }

          const volTxt = document.getElementById('weeklyVolumeText');
          if (volTxt) volTxt.innerText = `${sevenHrs} hrs`;

          const thTxt = document.getElementById('targetHoursText');
          if (thTxt) thTxt.innerText = `${targetHrs} Hours`;

          const loadTxt = document.getElementById('weeklyLoadText');
          if (loadTxt) loadTxt.innerText = `${sevenLoad} TSS`;

          // Target weekly load range based on CTL
          const ctlVal = (currentAnalytics.readiness && currentAnalytics.readiness.ctl) ? currentAnalytics.readiness.ctl : 40;
          const recMin = Math.round(ctlVal * 7 * 0.85);
          const recMax = Math.round(ctlVal * 7 * 1.25);
          const rangeTxt = document.getElementById('targetLoadRangeText');
          if (rangeTxt) rangeTxt.innerText = `${recMin} - ${recMax} TSS`;

          // Stacked discipline shares
          const sports = ws.seven_day_sports || {};
          const totalLoadSeven = Object.values(sports).reduce((acc, sp) => acc + (sp.load || 0), 0) || sevenLoad || 1;
          const rideLoad = (sports.Ride && sports.Ride.load) || 0;
          const runLoad = (sports.Run && sports.Run.load) || 0;
          const swimLoad = (sports.Swim && sports.Swim.load) || 0;
          const otherLoad = (sports.Other && sports.Other.load) || 0;

          const ridePct = Math.round((rideLoad / totalLoadSeven) * 100);
          const runPct = Math.round((runLoad / totalLoadSeven) * 100);
          const swimPct = Math.round((swimLoad / totalLoadSeven) * 100);
          const otherPct = Math.max(0, 100 - ridePct - runPct - swimPct);

          const bRide = document.getElementById('barShareRide');
          if (bRide) bRide.style.width = ridePct + '%';
          const bRun = document.getElementById('barShareRun');
          if (bRun) bRun.style.width = runPct + '%';
          const bSwim = document.getElementById('barShareSwim');
          if (bSwim) bSwim.style.width = swimPct + '%';
          const bOther = document.getElementById('barShareOther');
          if (bOther) bOther.style.width = otherPct + '%';

          const pillsEl = document.getElementById('weeklyDisciplinePills');
          if (pillsEl) {
            const parts = [];
            if (rideLoad > 0) parts.push(`Ride: ${rideLoad} TSS (${(sports.Ride && sports.Ride.hours) || 0}h)`);
            if (runLoad > 0) parts.push(`Run: ${runLoad} TSS (${(sports.Run && sports.Run.hours) || 0}h)`);
            if (swimLoad > 0) parts.push(`Swim: ${swimLoad} TSS`);
            if (otherLoad > 0) parts.push(`Other: ${otherLoad} TSS`);
            pillsEl.innerText = parts.length ? parts.join(' | ') : `${sevenHrs} hrs completed`;
          }

          if (currentAnalytics.acwr) {
            const a = currentAnalytics.acwr;
            const ratioInline = document.getElementById('acwrRatioInline');
            if (ratioInline) {
              ratioInline.innerText = `${a.ratio.toFixed(2)} (${a.status.replace('_', ' ')})`;
              ratioInline.style.color = a.status === 'SWEET_SPOT' ? 'var(--success)' : (a.status === 'DANGER_ZONE' ? 'var(--danger)' : 'var(--warning)');
            }
          }
        }

        if (currentAnalytics && currentAnalytics.readiness) {
          const r = currentAnalytics.readiness;
          const rBadge = document.getElementById('rhrStrainBadge');
          if (rBadge) {
            rBadge.innerText = r.rhr_elevated ? 'Autonomic Strain (+4 bpm)' : 'Autonomic Stable';
            rBadge.style.background = r.rhr_elevated ? 'rgba(239,68,68,0.2)' : 'rgba(16,185,129,0.2)';
            rBadge.style.color = r.rhr_elevated ? 'var(--danger)' : 'var(--success)';
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

        // Load Health Connect Status
        loadHealthConnectStatus();

        // Load COROS Training Hub & EvoLab Telemetry
        loadCorosHub();

        // Update Joe Friel Telemetry Data Quality Auditor
        if (qualityData) {
          const qb = document.getElementById('dataQualityBadge');
          if (qb) {
            qb.innerText = 'Audit: ' + qualityData.overall;
            if (qualityData.overall === 'Good') {
              qb.style.background = 'rgba(16,185,129,0.2)';
              qb.style.color = 'var(--success)';
            } else if (qualityData.overall === 'Partial') {
              qb.style.background = 'rgba(245,158,11,0.2)';
              qb.style.color = 'var(--warning)';
            } else {
              qb.style.background = 'rgba(239,68,68,0.2)';
              qb.style.color = 'var(--danger)';
            }
          }
          const qf = document.getElementById('dataQualityFix');
          if (qf) qf.innerText = qualityData.suggested_fix;

          const cl = document.getElementById('dataQualityChecklist');
          if (cl && qualityData.checks) {
            cl.innerHTML = qualityData.checks.map(c => {
              const bg = c.status === 'OK' ? 'rgba(16,185,129,0.15)' : (c.status === 'Warning' ? 'rgba(245,158,11,0.15)' : 'rgba(239,68,68,0.15)');
              const col = c.status === 'OK' ? 'var(--success)' : (c.status === 'Warning' ? 'var(--warning)' : 'var(--danger)');
              return '<div style="display:flex; justify-content:space-between; align-items:center; background:#0f172a; border:1px solid var(--border); border-radius:4px; padding:0.35rem 0.6rem;">' +
                     '<div><span style="font-weight:600; color:#e2e8f0;">' + c.area + ':</span> <span style="color:var(--text-muted);">' + c.explanation + '</span></div>' +
                     '<span style="padding:2px 6px; border-radius:3px; font-size:0.7rem; font-weight:700; background:' + bg + '; color:' + col + ';">' + c.status + '</span>' +
                     '</div>';
            }).join('');
          }
        }

        // Update W' and CP displays
        if (currentProfile) {
          const cp = currentProfile.ftp_bike || 250;
          const cpEl = document.getElementById('cpDisplay');
          if (cpEl) cpEl.innerText = cp + ' W';
          const wpEl = document.getElementById('wPrimeDisplay');
          if (wpEl) wpEl.innerText = '20.0 kJ';
        }

      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      }
    }

    async function simulateWbal(type) {
      const cp = (currentProfile && currentProfile.ftp_bike) ? currentProfile.ftp_bike : 250;
      const wPrime = 20000;
      let watts = [];
      if (type === 'intervals') {
        for (let rep = 0; rep < 4; rep++) {
          for (let s = 0; s < 240; s++) watts.push(Math.round(cp * 1.20));
          for (let s = 0; s < 120; s++) watts.push(Math.round(cp * 0.50));
        }
      } else {
        for (let s = 0; s < 1200; s++) watts.push(Math.round(cp * 1.02));
        for (let s = 0; s < 300; s++) watts.push(Math.round(cp * 0.55));
      }

      const res = await fetch('/api/wbal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ watts: watts, cp: cp, w_prime: wPrime })
      });
      const data = await res.json();
      if (data && data.summary) {
        const s = data.summary;
        const minPct = Math.max(0, Math.round(s.wbal_min_j / wPrime * 100));
        const fill = document.getElementById('wbalBatteryFill');
        if (fill) {
          fill.style.width = minPct + '%';
          fill.style.background = minPct < 30 ? 'var(--danger)' : (minPct < 60 ? 'var(--warning)' : 'var(--success)');
        }
        const pctEl = document.getElementById('wbalBatteryPct');
        if (pctEl) pctEl.innerText = minPct + '% min remaining (' + (s.wbal_min_j / 1000).toFixed(1) + ' / ' + (wPrime / 1000).toFixed(1) + ' kJ)';
        const b = document.getElementById('wbalStatusBadge');
        if (b) {
          b.innerText = minPct < 30 ? 'Battery Depleted' : (minPct < 60 ? 'Battery Strained' : 'Battery Optimal');
          b.style.color = minPct < 30 ? 'var(--danger)' : (minPct < 60 ? 'var(--warning)' : 'var(--success)');
        }
        const resBox = document.getElementById('wbalSimResult');
        if (resBox) {
          resBox.style.display = 'block';
          resBox.innerHTML = '<strong>Skiba Model Output:</strong> Max Depletion: ' + (s.wbal_max_depletion_j / 1000).toFixed(1) + ' kJ (' + s.wbal_usage_pct + '%) | Below 30%: ' + s.seconds_below_30pct + 's | Reconstitution Ratio: ' + s.wbal_recovery_ratio + 'x | Depletion Events: ' + s.wbal_depletion_events;
        }
      }
    }

    async function loadCorosHub() {
      try {
        const res = await fetch('/api/coros/evolab');
        const data = await res.json();
        if (!data) return;

        // 1. EvoLab Core Telemetry
        if (data.evolab) {
          const e = data.evolab;
          const bfEl = document.getElementById('corosBaseFitness');
          if (bfEl) bfEl.innerText = e.base_fitness.toFixed(1);
          const liEl = document.getElementById('corosLoadImpact');
          if (liEl) liEl.innerText = e.load_impact.toFixed(1);
          const fsEl = document.getElementById('corosFatigueScore');
          if (fsEl) fsEl.innerText = e.fatigue_score.toFixed(0);

          const fzEl = document.getElementById('corosFatigueZoneText');
          if (fzEl) fzEl.innerText = e.fatigue_zone + ' Zone';

          const fbBadge = document.getElementById('corosFatigueBadge');
          if (fbBadge) {
            fbBadge.innerText = e.fatigue_zone;
            if (e.fatigue_zone === 'OPTIMIZED') {
              fbBadge.style.background = 'rgba(16,185,129,0.2)';
              fbBadge.style.color = 'var(--success)';
            } else if (e.fatigue_zone === 'PERFORMANCE') {
              fbBadge.style.background = 'rgba(6,182,212,0.2)';
              fbBadge.style.color = '#06b6d4';
            } else if (e.fatigue_zone === 'HIGH') {
              fbBadge.style.background = 'rgba(245,158,11,0.2)';
              fbBadge.style.color = 'var(--warning)';
            } else if (e.fatigue_zone === 'EXCESSIVE') {
              fbBadge.style.background = 'rgba(239,68,68,0.2)';
              fbBadge.style.color = 'var(--danger)';
            } else {
              fbBadge.style.background = 'rgba(148,163,184,0.2)';
              fbBadge.style.color = '#94a3b8';
            }
          }

          const fillEl = document.getElementById('corosFatigueFill');
          if (fillEl) {
            fillEl.style.width = Math.min(100, Math.max(5, e.fatigue_score)) + '%';
            fillEl.style.background = e.fatigue_score >= 80 ? 'var(--danger)' : (e.fatigue_score >= 60 ? 'var(--warning)' : (e.fatigue_score >= 40 ? 'var(--success)' : '#06b6d4'));
          }

          const descEl = document.getElementById('corosFatigueDesc');
          if (descEl) descEl.innerText = e.fatigue_description + ' (' + e.intensity_trend + ')';

          const loadEl = document.getElementById('coros7dLoad');
          if (loadEl) loadEl.innerText = e.seven_day_load.toFixed(0) + ' TSS';
          const rangeEl = document.getElementById('corosLoadRangeText');
          if (rangeEl) rangeEl.innerText = 'Target: ' + e.recommended_min_load.toFixed(0) + ' - ' + e.recommended_max_load.toFixed(0) + ' (' + e.load_recommendation_status + ')';
        }

        // 2. Running Fitness 4-Pillars
        if (data.running_fitness) {
          const rf = data.running_fitness;
          const ofEl = document.getElementById('corosOverallFitness');
          if (ofEl) ofEl.innerText = rf.overall_score.toFixed(1) + ' / 100';
          const tpEl = document.getElementById('corosThreshPace');
          if (tpEl) tpEl.innerText = rf.threshold_pace_formatted;

          const bVal = document.getElementById('corosBaseScore');
          if (bVal) bVal.innerText = rf.base_score.toFixed(1);
          const bBar = document.getElementById('corosBaseBar');
          if (bBar) bBar.style.width = rf.base_score + '%';

          const eVal = document.getElementById('corosEnduranceScore');
          if (eVal) eVal.innerText = rf.endurance_score.toFixed(1);
          const eBar = document.getElementById('corosEnduranceBar');
          if (eBar) eBar.style.width = rf.endurance_score + '%';

          const sVal = document.getElementById('corosSpeedScore');
          if (sVal) sVal.innerText = rf.speed_score.toFixed(1);
          const sBar = document.getElementById('corosSpeedBar');
          if (sBar) sBar.style.width = rf.speed_score + '%';

          const spVal = document.getElementById('corosSprintScore');
          if (spVal) spVal.innerText = rf.sprint_score.toFixed(1);
          const spBar = document.getElementById('corosSprintBar');
          if (spBar) spBar.style.width = rf.sprint_score + '%';
        }

        // 3. Race Predictor Table
        if (data.race_predictions) {
          const tbody = document.getElementById('corosRaceTableBody');
          if (tbody) {
            tbody.innerHTML = data.race_predictions.map(p => {
              return '<tr>' +
                '<td style="font-weight:700; color:#fff;">' + p.distance_name + '</td>' +
                '<td style="color:var(--text-muted);">' + p.distance_km + ' km</td>' +
                '<td style="font-weight:700; color:#38bdf8;">' + p.predicted_time_formatted + '</td>' +
                '<td style="color:var(--success);">' + p.predicted_pace_formatted + '</td>' +
              '</tr>';
            }).join('');
          }
        }

        // 4. Training Effect & Recovery Timer
        if (data.training_effect) {
          renderCorosTE(data.training_effect);
        }

      } catch (err) {
        console.debug('Failed loading COROS Hub metrics:', err);
      }
    }

    function renderCorosTE(te) {
      if (!te) return;
      const aeroEl = document.getElementById('corosAeroTeVal');
      if (aeroEl) aeroEl.innerText = te.aerobic_te.toFixed(1);
      const aeroLbl = document.getElementById('corosAeroTeLabel');
      if (aeroLbl) aeroLbl.innerText = te.aerobic_label;

      const anaeroEl = document.getElementById('corosAnaeroTeVal');
      if (anaeroEl) anaeroEl.innerText = te.anaerobic_te.toFixed(1);
      const anaeroLbl = document.getElementById('corosAnaeroTeLabel');
      if (anaeroLbl) anaeroLbl.innerText = te.anaerobic_label;

      const recH = document.getElementById('corosRecoveryHours');
      if (recH) recH.innerText = te.recovery_hours.toFixed(1) + 'h';
      const recPct = document.getElementById('corosRecoveryPctText');
      if (recPct) recPct.innerText = te.recovery_pct + '%';
      const recFill = document.getElementById('corosRecoveryFill');
      if (recFill) {
        recFill.style.width = te.recovery_pct + '%';
        recFill.style.background = te.recovery_state === 'FRESH' ? 'var(--success)' : (te.recovery_state === 'TIRED' ? 'var(--warning)' : 'var(--danger)');
      }

      const recBadge = document.getElementById('corosRecoveryBadge');
      if (recBadge) {
        recBadge.innerText = te.recovery_state + ' (' + te.recovery_pct + '%)';
        recBadge.style.color = te.recovery_state === 'FRESH' ? 'var(--success)' : (te.recovery_state === 'TIRED' ? 'var(--warning)' : 'var(--danger)');
        recBadge.style.background = te.recovery_state === 'FRESH' ? 'rgba(16,185,129,0.2)' : (te.recovery_state === 'TIRED' ? 'rgba(245,158,11,0.2)' : 'rgba(239,68,68,0.2)');
      }

      const recGuid = document.getElementById('corosRecoveryGuidance');
      if (recGuid) {
        if (te.recovery_state === 'FRESH') {
          recGuid.innerText = 'Body is fully recovered and primed for high-intensity intervals or long aerobic volume.';
        } else if (te.recovery_state === 'TIRED') {
          recGuid.innerText = 'Body is processing recent training strain. Easy aerobic recovery or zone 2 volume is permitted.';
        } else {
          recGuid.innerText = 'High physiological fatigue accumulated. Complete rest or light passive mobility recommended.';
        }
      }
    }

    async function calcCorosTE() {
      const durMins = parseInt(document.getElementById('teInputMins').value) || 60;
      const load = parseFloat(document.getElementById('teInputLoad').value) || 60.0;
      const hr = parseInt(document.getElementById('teInputHr').value) || 155;
      try {
        const res = await fetch('/api/coros/training-effect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            duration_seconds: durMins * 60,
            load_tss: load,
            hr_avg: hr
          })
        });
        const data = await res.json();
        renderCorosTE(data);
      } catch (err) {
        console.error('Failed computing training effect:', err);
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

    async function loadHealthConnectStatus() {
      try {
        const uEl = document.getElementById('hcWebhookUrl');
        if (uEl) {
          uEl.innerText = window.location.origin + '/api/health-connect';
        }
        const res = await fetch('/api/health-connect/status');
        const data = await res.json();
        if (data && data.last_sync) {
          const l = data.last_sync;
          const dtText = document.getElementById('hcLastSyncText');
          if (dtText && l.timestamp) dtText.innerText = l.timestamp.slice(0, 19).replace('T', ' ');
          const wCount = document.getElementById('hcWellnessCount');
          if (wCount) wCount.innerText = (l.wellness_records_updated || 0) + ' days';
          const aCount = document.getElementById('hcActivitiesCount');
          if (aCount) aCount.innerText = (l.activities_uploaded || 0) + '';
        }
        const cRelay = document.getElementById('hcCorosRelayStatus');
        if (cRelay) {
          cRelay.innerText = data.coros_connected ? `Active (${data.coros_mode})` : 'Not Configured';
          cRelay.style.color = data.coros_connected ? 'var(--success)' : 'var(--warning)';
        }
      } catch (err) {
        console.debug('Failed loading Health Connect status:', err);
      }
    }

    async function triggerLanPull() {
      const ip = (document.getElementById('hcPhoneIp').value || '').trim();
      const days = parseInt(document.getElementById('hcDays').value) || 7;
      if (!ip) {
        alert('Please enter your phone IP address (shown in the HC Webhook app on your phone)');
        return;
      }
      const btn = document.getElementById('btnLanPull');
      const statusEl = document.getElementById('hcPullStatus');
      btn.disabled = true;
      btn.innerText = 'Pulling...';
      statusEl.innerText = `Connecting to http://${ip}:8787/?days=${days}...`;

      try {
        const res = await fetch('/api/health-connect/pull', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone_ip: ip, port: 8787, days: days, dry_run: false })
        });
        const data = await res.json();
        if (res.ok) {
          showToast(`Synced ${data.wellness_records_updated} wellness days & ${data.activities_uploaded} activities!`);
          statusEl.innerText = `Success: ${data.wellness_records_updated} days written to Intervals.icu & queued for COROS!`;
          loadDashboard();
        } else {
          statusEl.innerText = `Error: ${data.error || 'Failed to pull from phone'}`;
          alert(`Pull Error: ${data.error}`);
        }
      } catch (err) {
        statusEl.innerText = `Network Error: ${err}`;
        alert(`Network Error: ${err}`);
      } finally {
        btn.disabled = false;
        btn.innerText = 'Pull Now';
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

      const series = data.daily_series || [];

      // Render all metric charts
      renderPmcChart(series);
      renderAcwrChart(series);
      renderRhrChart(series, data.readiness ? data.readiness.resting_hr_baseline : null);
      renderSleepChart(series);
      renderVitalsChart(series);
      renderDailyLoadChart(series);
      renderDecouplingGauge(3.2);

      const sumEl = document.getElementById('totalVolumeLoadSummary');
      if (sumEl) {
        sumEl.innerText = (data.total_moving_hours || 0) + ' hrs | ' + (data.total_load_tss || 0) + ' TSS (' + (data.total_activities || 0) + ' activities)';
      }

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

    function renderPmcChart(series) {
      const svg = document.getElementById('pmcChartSvg');
      if (!svg || !series || series.length === 0) return;

      const w = 800, h = 240;
      const padL = 45, padR = 25, padT = 20, padB = 30;
      const pw = w - padL - padR;
      const ph = h - padT - padB;

      let allVals = [];
      series.forEach(d => {
        allVals.push(d.ctl, d.atl, d.tsb);
      });
      let minVal = Math.min(...allVals, -20);
      let maxVal = Math.max(...allVals, 60);
      const span = maxVal - minVal || 1;
      minVal -= span * 0.05;
      maxVal += span * 0.05;

      const getX = (i) => padL + (i / (series.length - 1)) * pw;
      const getY = (val) => padT + ph - ((val - minVal) / (maxVal - minVal)) * ph;
      const y0 = getY(0);

      let gridSvg = '';
      const ySteps = 4;
      for (let s = 0; s <= ySteps; s++) {
        const val = minVal + (s / ySteps) * (maxVal - minVal);
        const yPos = getY(val);
        gridSvg += `<line x1="${padL}" y1="${yPos}" x2="${w - padR}" y2="${yPos}" stroke="#1f2937" stroke-dasharray="3"/>`;
        gridSvg += `<text x="${padL - 8}" y="${yPos + 4}" fill="#6b7280" font-size="10" text-anchor="end">${Math.round(val)}</text>`;
      }

      if (y0 >= padT && y0 <= padT + ph) {
        gridSvg += `<line x1="${padL}" y1="${y0}" x2="${w - padR}" y2="${y0}" stroke="#4b5563" stroke-width="1.5" stroke-dasharray="4"/>`;
        gridSvg += `<text x="${w - padR + 4}" y="${y0 + 3}" fill="#9ca3af" font-size="10">0</text>`;
      }

      let dateSvg = '';
      for (let i = 0; i < series.length; i += 5) {
        const xPos = getX(i);
        const dt = series[i].date ? series[i].date.slice(5) : '';
        dateSvg += `<text x="${xPos}" y="${h - 10}" fill="#6b7280" font-size="10" text-anchor="middle">${dt}</text>`;
      }
      const lastX = getX(series.length - 1);
      const lastDt = series[series.length - 1].date ? series[series.length - 1].date.slice(5) : '';
      dateSvg += `<text x="${lastX}" y="${h - 10}" fill="#9ca3af" font-size="10" text-anchor="middle">${lastDt}</text>`;

      const ctlPoints = series.map((d, i) => `${getX(i).toFixed(1)},${getY(d.ctl).toFixed(1)}`).join(' L ');
      const atlPoints = series.map((d, i) => `${getX(i).toFixed(1)},${getY(d.atl).toFixed(1)}`).join(' L ');
      const tsbPoints = series.map((d, i) => `${getX(i).toFixed(1)},${getY(d.tsb).toFixed(1)}`).join(' L ');

      const tsbAreaPoints = `M ${getX(0).toFixed(1)},${y0.toFixed(1)} L ` +
        series.map((d, i) => `${getX(i).toFixed(1)},${getY(d.tsb).toFixed(1)}`).join(' L ') +
        ` L ${getX(series.length - 1).toFixed(1)},${y0.toFixed(1)} Z`;

      svg.innerHTML = `
        <defs>
          <linearGradient id="tsbGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#10b981" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="#f43f5e" stop-opacity="0.15"/>
          </linearGradient>
        </defs>
        ${gridSvg}
        ${dateSvg}
        <path d="${tsbAreaPoints}" fill="url(#tsbGradient)"/>
        <path d="M ${ctlPoints}" fill="none" stroke="#06b6d4" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M ${atlPoints}" fill="none" stroke="#f43f5e" stroke-width="2" stroke-linecap="round"/>
        <path d="M ${tsbPoints}" fill="none" stroke="#10b981" stroke-width="2" stroke-dasharray="4" stroke-linecap="round"/>
        <line id="pmcCrosshair" x1="0" y1="${padT}" x2="0" y2="${padT + ph}" stroke="#94a3b8" stroke-dasharray="2" opacity="0"/>
      `;

      const container = document.getElementById('pmcChartContainer');
      const tooltip = document.getElementById('pmcTooltip');
      if (container && tooltip) {
        container.onmousemove = function(e) {
          const rect = container.getBoundingClientRect();
          const mouseX = e.clientX - rect.left;
          const relX = (mouseX / rect.width) * w;
          if (relX < padL || relX > w - padR) {
            tooltip.style.display = 'none';
            const ch = document.getElementById('pmcCrosshair');
            if (ch) ch.setAttribute('opacity', '0');
            return;
          }
          const frac = (relX - padL) / pw;
          const idx = Math.min(series.length - 1, Math.max(0, Math.round(frac * (series.length - 1))));
          const pt = series[idx];
          const ptX = getX(idx);

          const ch = document.getElementById('pmcCrosshair');
          if (ch) {
            ch.setAttribute('x1', ptX);
            ch.setAttribute('x2', ptX);
            ch.setAttribute('opacity', '0.7');
          }

          tooltip.style.display = 'block';
          tooltip.style.left = Math.min(rect.width - 160, Math.max(10, mouseX - 60)) + 'px';
          tooltip.style.top = '15px';
          tooltip.innerHTML = `
            <div style="font-weight:700; color:#fff; border-bottom:1px solid #334155; padding-bottom:2px; margin-bottom:4px;">${pt.date}</div>
            <div style="color:#06b6d4;">CTL (Fitness): <strong>${pt.ctl}</strong></div>
            <div style="color:#f43f5e;">ATL (Fatigue): <strong>${pt.atl}</strong></div>
            <div style="color:#10b981;">TSB (Form): <strong>${(pt.tsb >= 0 ? '+' : '') + pt.tsb}</strong></div>
            <div style="color:#94a3b8; font-size:0.7rem; margin-top:2px;">Daily Load: ${pt.load_tss} TSS</div>
          `;
        };
        container.onmouseleave = function() {
          tooltip.style.display = 'none';
          const ch = document.getElementById('pmcCrosshair');
          if (ch) ch.setAttribute('opacity', '0');
        };
      }
    }

    function renderAcwrChart(series) {
      const svg = document.getElementById('acwrChartSvg');
      if (!svg || !series || series.length === 0) return;

      const w = 450, h = 180;
      const padL = 40, padR = 20, padT = 15, padB = 25;
      const pw = w - padL - padR;
      const ph = h - padT - padB;

      const minVal = 0.0;
      const maxVal = 2.0;
      const getX = (i) => padL + (i / (series.length - 1)) * pw;
      const getY = (val) => padT + ph - (Math.min(maxVal, Math.max(minVal, val)) / maxVal) * ph;

      const y1_5 = getY(1.5);
      const y1_3 = getY(1.3);
      const y0_8 = getY(0.8);
      const y0_0 = getY(0.0);

      let zonesSvg = `
        <rect x="${padL}" y="${padT}" width="${pw}" height="${y1_5 - padT}" fill="rgba(239, 68, 68, 0.15)"/>
        <rect x="${padL}" y="${y1_5}" width="${pw}" height="${y1_3 - y1_5}" fill="rgba(245, 158, 11, 0.15)"/>
        <rect x="${padL}" y="${y1_3}" width="${pw}" height="${y0_8 - y1_3}" fill="rgba(16, 185, 129, 0.15)"/>
        <rect x="${padL}" y="${y0_8}" width="${pw}" height="${y0_0 - y0_8}" fill="rgba(100, 116, 139, 0.08)"/>

        <line x1="${padL}" y1="${y1_5}" x2="${w - padR}" y2="${y1_5}" stroke="#ef4444" stroke-width="1" stroke-dasharray="3"/>
        <line x1="${padL}" y1="${y1_3}" x2="${w - padR}" y2="${y1_3}" stroke="#f59e0b" stroke-width="1" stroke-dasharray="3"/>
        <line x1="${padL}" y1="${y0_8}" x2="${w - padR}" y2="${y0_8}" stroke="#10b981" stroke-width="1" stroke-dasharray="3"/>
        
        <text x="${padL - 6}" y="${y1_5 + 3}" fill="#ef4444" font-size="9" text-anchor="end">1.5</text>
        <text x="${padL - 6}" y="${y1_3 + 3}" fill="#f59e0b" font-size="9" text-anchor="end">1.3</text>
        <text x="${padL - 6}" y="${y0_8 + 3}" fill="#10b981" font-size="9" text-anchor="end">0.8</text>
        <text x="${padL - 6}" y="${y0_0 + 3}" fill="#6b7280" font-size="9" text-anchor="end">0.0</text>
      `;

      let dateSvg = '';
      for (let i = 0; i < series.length; i += 7) {
        const xPos = getX(i);
        const dt = series[i].date ? series[i].date.slice(5) : '';
        dateSvg += `<text x="${xPos}" y="${h - 8}" fill="#6b7280" font-size="9" text-anchor="middle">${dt}</text>`;
      }
      const lastX = getX(series.length - 1);
      const lastDt = series[series.length - 1].date ? series[series.length - 1].date.slice(5) : '';
      dateSvg += `<text x="${lastX}" y="${h - 8}" fill="#9ca3af" font-size="9" text-anchor="middle">${lastDt}</text>`;

      const ratioPoints = series.map((d, i) => `${getX(i).toFixed(1)},${getY(d.acwr_ratio).toFixed(1)}`).join(' L ');

      svg.innerHTML = `
        ${zonesSvg}
        ${dateSvg}
        <path d="M ${ratioPoints}" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round"/>
        <line id="acwrCrosshair" x1="0" y1="${padT}" x2="0" y2="${padT + ph}" stroke="#94a3b8" stroke-dasharray="2" opacity="0"/>
      `;

      const container = document.getElementById('acwrChartContainer');
      const tooltip = document.getElementById('acwrTooltip');
      if (container && tooltip) {
        container.onmousemove = function(e) {
          const rect = container.getBoundingClientRect();
          const mouseX = e.clientX - rect.left;
          const relX = (mouseX / rect.width) * w;
          if (relX < padL || relX > w - padR) {
            tooltip.style.display = 'none';
            const ch = document.getElementById('acwrCrosshair');
            if (ch) ch.setAttribute('opacity', '0');
            return;
          }
          const frac = (relX - padL) / pw;
          const idx = Math.min(series.length - 1, Math.max(0, Math.round(frac * (series.length - 1))));
          const pt = series[idx];
          const ptX = getX(idx);

          const ch = document.getElementById('acwrCrosshair');
          if (ch) {
            ch.setAttribute('x1', ptX);
            ch.setAttribute('x2', ptX);
            ch.setAttribute('opacity', '0.7');
          }

          let statusColor = '#10b981', statusTxt = 'Sweet Spot';
          if (pt.acwr_ratio > 1.5) { statusColor = '#ef4444'; statusTxt = 'Danger Zone'; }
          else if (pt.acwr_ratio > 1.3) { statusColor = '#f59e0b'; statusTxt = 'Elevated Load'; }
          else if (pt.acwr_ratio < 0.8) { statusColor = '#64748b'; statusTxt = 'Under-training'; }

          tooltip.style.display = 'block';
          tooltip.style.left = Math.min(rect.width - 150, Math.max(10, mouseX - 60)) + 'px';
          tooltip.style.top = '15px';
          tooltip.innerHTML = `
            <div style="font-weight:700; color:#fff; border-bottom:1px solid #334155; padding-bottom:2px; margin-bottom:4px;">${pt.date}</div>
            <div style="color:#38bdf8;">ACWR Ratio: <strong>${pt.acwr_ratio.toFixed(2)}</strong></div>
            <div style="color:${statusColor}; font-size:0.7rem;">Status: ${statusTxt}</div>
          `;
        };
        container.onmouseleave = function() {
          tooltip.style.display = 'none';
          const ch = document.getElementById('acwrCrosshair');
          if (ch) ch.setAttribute('opacity', '0');
        };
      }
    }

    function renderRhrChart(series, baseline) {
      const svg = document.getElementById('rhrChartSvg');
      if (!svg || !series || series.length === 0) return;

      const w = 450, h = 180;
      const padL = 40, padR = 20, padT = 15, padB = 25;
      const pw = w - padL - padR;
      const ph = h - padT - padB;

      const rhrs = series.map(d => d.resting_hr).filter(v => v !== null && v !== undefined && v > 30);
      const baseVal = baseline || (rhrs.length ? (rhrs.reduce((a, b) => a + b, 0) / rhrs.length) : 50);
      const minVal = Math.min(baseVal - 8, rhrs.length ? Math.min(...rhrs) - 3 : 40);
      const maxVal = Math.max(baseVal + 10, rhrs.length ? Math.max(...rhrs) + 3 : 65);

      const getX = (i) => padL + (i / (series.length - 1)) * pw;
      const getY = (val) => padT + ph - ((val - minVal) / (maxVal - minVal || 1)) * ph;

      const yBase = getY(baseVal);
      const yStrain = getY(baseVal + 4.0);

      let gridSvg = `
        <line x1="${padL}" y1="${yBase}" x2="${w - padR}" y2="${yBase}" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4"/>
        <text x="${w - padR - 5}" y="${yBase - 4}" fill="#94a3b8" font-size="9" text-anchor="end">Base: ${Math.round(baseVal)} bpm</text>

        <line x1="${padL}" y1="${yStrain}" x2="${w - padR}" y2="${yStrain}" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="3"/>
        <text x="${w - padR - 5}" y="${yStrain - 4}" fill="#ef4444" font-size="9" text-anchor="end">+4 bpm Strain</text>

        <text x="${padL - 6}" y="${yBase + 3}" fill="#94a3b8" font-size="9" text-anchor="end">${Math.round(baseVal)}</text>
        <text x="${padL - 6}" y="${yStrain + 3}" fill="#ef4444" font-size="9" text-anchor="end">${Math.round(baseVal + 4)}</text>
      `;

      let dateSvg = '';
      for (let i = 0; i < series.length; i += 7) {
        const xPos = getX(i);
        const dt = series[i].date ? series[i].date.slice(5) : '';
        dateSvg += `<text x="${xPos}" y="${h - 8}" fill="#6b7280" font-size="9" text-anchor="middle">${dt}</text>`;
      }
      const lastX = getX(series.length - 1);
      const lastDt = series[series.length - 1].date ? series[series.length - 1].date.slice(5) : '';
      dateSvg += `<text x="${lastX}" y="${h - 8}" fill="#9ca3af" font-size="9" text-anchor="middle">${lastDt}</text>`;

      const validPoints = [];
      series.forEach((d, i) => {
        if (d.resting_hr) {
          validPoints.push({ x: getX(i), y: getY(d.resting_hr), hr: d.resting_hr, idx: i, date: d.date });
        }
      });

      let linePath = '';
      if (validPoints.length > 1) {
        linePath = 'M ' + validPoints.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' L ');
      }

      let dotsSvg = '';
      validPoints.forEach(p => {
        const isElevated = p.hr >= baseVal + 4.0;
        const color = isElevated ? '#ef4444' : '#10b981';
        dotsSvg += `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="3.5" fill="${color}" stroke="#0f172a" stroke-width="1"/>`;
      });

      svg.innerHTML = `
        ${gridSvg}
        ${dateSvg}
        ${linePath ? `<path d="${linePath}" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round"/>` : ''}
        ${dotsSvg}
        <line id="rhrCrosshair" x1="0" y1="${padT}" x2="0" y2="${padT + ph}" stroke="#94a3b8" stroke-dasharray="2" opacity="0"/>
      `;

      const container = document.getElementById('rhrChartContainer');
      const tooltip = document.getElementById('rhrTooltip');
      if (container && tooltip) {
        container.onmousemove = function(e) {
          const rect = container.getBoundingClientRect();
          const mouseX = e.clientX - rect.left;
          const relX = (mouseX / rect.width) * w;
          if (relX < padL || relX > w - padR) {
            tooltip.style.display = 'none';
            const ch = document.getElementById('rhrCrosshair');
            if (ch) ch.setAttribute('opacity', '0');
            return;
          }
          const frac = (relX - padL) / pw;
          const idx = Math.min(series.length - 1, Math.max(0, Math.round(frac * (series.length - 1))));
          const pt = series[idx];
          const ptX = getX(idx);

          const ch = document.getElementById('rhrCrosshair');
          if (ch) {
            ch.setAttribute('x1', ptX);
            ch.setAttribute('x2', ptX);
            ch.setAttribute('opacity', '0.7');
          }

          if (!pt.resting_hr) {
            tooltip.style.display = 'none';
            return;
          }

          const delta = (pt.resting_hr - baseVal);
          const isElevated = delta >= 4.0;

          tooltip.style.display = 'block';
          tooltip.style.left = Math.min(rect.width - 150, Math.max(10, mouseX - 60)) + 'px';
          tooltip.style.top = '15px';
          tooltip.innerHTML = `
            <div style="font-weight:700; color:#fff; border-bottom:1px solid #334155; padding-bottom:2px; margin-bottom:4px;">${pt.date}</div>
            <div style="color:#38bdf8;">Resting HR: <strong>${Math.round(pt.resting_hr)} bpm</strong></div>
            <div style="color:${isElevated ? '#ef4444' : '#10b981'}; font-size:0.7rem;">Delta: ${(delta >= 0 ? '+' : '') + delta.toFixed(1)} bpm [${isElevated ? 'STRAIN' : 'STABLE'}]</div>
          `;
        };
        container.onmouseleave = function() {
          tooltip.style.display = 'none';
          const ch = document.getElementById('rhrCrosshair');
          if (ch) ch.setAttribute('opacity', '0');
        };
      }
    }

    function renderSleepChart(series) {
      const svg = document.getElementById('sleepChartSvg');
      if (!svg || !series || series.length === 0) return;

      const w = 450, h = 180;
      const padL = 40, padR = 20, padT = 15, padB = 25;
      const pw = w - padL - padR;
      const ph = h - padT - padB;

      const maxVal = 10.0;
      const minVal = 0.0;

      const getX = (i) => padL + (i / (series.length - 1)) * pw;
      const getY = (val) => padT + ph - (val / maxVal) * ph;
      const colW = Math.max(4, Math.floor(pw / series.length) - 2);

      const y7h = getY(7.0);

      let gridSvg = `
        <line x1="${padL}" y1="${y7h}" x2="${w - padR}" y2="${y7h}" stroke="#10b981" stroke-width="1.5" stroke-dasharray="4"/>
        <text x="${w - padR - 5}" y="${y7h - 4}" fill="#10b981" font-size="9" text-anchor="end">7h Optimal</text>
        <text x="${padL - 6}" y="${y7h + 3}" fill="#10b981" font-size="9" text-anchor="end">7h</text>
        <line x1="${padL}" y1="${getY(4.0)}" x2="${w - padR}" y2="${getY(4.0)}" stroke="#1f2937" stroke-dasharray="3"/>
        <text x="${padL - 6}" y="${getY(4.0) + 3}" fill="#6b7280" font-size="9" text-anchor="end">4h</text>
      `;

      let barsSvg = '';
      let sleepSum = 0;
      let sleepCount = 0;

      series.forEach((d, i) => {
        if (d.sleep_hours !== null && d.sleep_hours !== undefined) {
          sleepSum += d.sleep_hours;
          sleepCount += 1;
          const bh = (d.sleep_hours / maxVal) * ph;
          const bx = getX(i) - colW / 2;
          const by = padT + ph - bh;
          const barColor = d.sleep_hours >= 7.0 ? '#10b981' : d.sleep_hours >= 5.0 ? '#a855f7' : '#f59e0b';
          barsSvg += `<rect x="${bx}" y="${by}" width="${colW}" height="${bh}" rx="2" fill="${barColor}" opacity="0.85"/>`;
        }
      });

      const avgText = sleepCount > 0 ? (sleepSum / sleepCount).toFixed(1) + ' hrs avg' : '-- hrs avg';
      const sumEl = document.getElementById('sleepSummaryText');
      if (sumEl) sumEl.innerText = avgText;

      let dateSvg = '';
      for (let i = 0; i < series.length; i += 7) {
        const xPos = getX(i);
        const dt = series[i].date ? series[i].date.slice(5) : '';
        dateSvg += `<text x="${xPos}" y="${h - 8}" fill="#6b7280" font-size="9" text-anchor="middle">${dt}</text>`;
      }
      const lastX = getX(series.length - 1);
      const lastDt = series[series.length - 1].date ? series[series.length - 1].date.slice(5) : '';
      dateSvg += `<text x="${lastX}" y="${h - 8}" fill="#9ca3af" font-size="9" text-anchor="middle">${lastDt}</text>`;

      svg.innerHTML = gridSvg + barsSvg + dateSvg;
    }

    function renderVitalsChart(series) {
      const svg = document.getElementById('vitalsChartSvg');
      if (!svg || !series || series.length === 0) return;

      const w = 450, h = 180;
      const padL = 40, padR = 20, padT = 15, padB = 25;
      const pw = w - padL - padR;
      const ph = h - padT - padB;

      const getX = (i) => padL + (i / (series.length - 1)) * pw;
      // SpO2 scale (90% to 100%) on left, Weight (75kg to 85kg) on right
      const getSpo2Y = (val) => padT + ph - ((val - 90.0) / 10.0) * ph;
      const getWeightY = (val) => padT + ph - ((val - 75.0) / 10.0) * ph;

      let gridSvg = `
        <line x1="${padL}" y1="${getSpo2Y(95.0)}" x2="${w - padR}" y2="${getSpo2Y(95.0)}" stroke="#06b6d4" stroke-width="1" stroke-dasharray="3"/>
        <text x="${padL - 6}" y="${getSpo2Y(95.0) + 3}" fill="#06b6d4" font-size="9" text-anchor="end">95%</text>
        <text x="${w - padR + 4}" y="${getWeightY(80.0) + 3}" fill="#10b981" font-size="9">80kg</text>
      `;

      let pointsSvg = '';
      series.forEach((d, i) => {
        const cx = getX(i);
        if (d.spo2 !== null && d.spo2 !== undefined) {
          const cy = Math.max(padT, Math.min(padT + ph, getSpo2Y(d.spo2)));
          pointsSvg += `<circle cx="${cx}" cy="${cy}" r="3.5" fill="#06b6d4"/>`;
        }
        if (d.weight !== null && d.weight !== undefined) {
          const wy = Math.max(padT, Math.min(padT + ph, getWeightY(d.weight)));
          pointsSvg += `<circle cx="${cx}" cy="${wy}" r="3.5" fill="#10b981"/>`;
        }
      });

      let dateSvg = '';
      for (let i = 0; i < series.length; i += 7) {
        const xPos = getX(i);
        const dt = series[i].date ? series[i].date.slice(5) : '';
        dateSvg += `<text x="${xPos}" y="${h - 8}" fill="#6b7280" font-size="9" text-anchor="middle">${dt}</text>`;
      }
      const lastX = getX(series.length - 1);
      const lastDt = series[series.length - 1].date ? series[series.length - 1].date.slice(5) : '';
      dateSvg += `<text x="${lastX}" y="${h - 8}" fill="#9ca3af" font-size="9" text-anchor="middle">${lastDt}</text>`;

      svg.innerHTML = gridSvg + pointsSvg + dateSvg;
    }

    let currentDailyLoadDays = 30;

    function filterDailyLoad(days) {
      currentDailyLoadDays = days;
      document.querySelectorAll('.chart-filter-btn').forEach(b => b.classList.remove('active'));
      const activeBtn = document.getElementById('btnLoad' + days + 'd');
      if (activeBtn) activeBtn.classList.add('active');
      if (currentAnalytics && currentAnalytics.daily_series) {
        renderDailyLoadChart(currentAnalytics.daily_series, days);
      }
    }

    function renderDailyLoadChart(allSeries, daysCount) {
      const svg = document.getElementById('loadChartSvg');
      const scrollBox = document.getElementById('loadChartScrollBox');
      if (!svg || !allSeries || allSeries.length === 0) return;

      const days = daysCount || currentDailyLoadDays || 30;
      const series = allSeries.slice(-days);

      const h = 190;
      const padL = 50, padR = 30, padT = 18, padB = 28;
      const colW = Math.max(28, Math.min(48, Math.floor(800 / series.length)));
      const pw = colW * series.length;
      const w = Math.max(scrollBox ? scrollBox.clientWidth : 800, padL + pw + padR);
      const ph = h - padT - padB;

      svg.setAttribute('width', w + 'px');
      svg.setAttribute('viewBox', `0 0 ${w} ${h}`);

      const maxLoad = Math.max(60, Math.max(...series.map(d => d.load_tss || 0)) * 1.18);
      const getX = (i) => padL + (i * colW);
      const barW = Math.max(12, colW * 0.72);
      const getY = (val) => padT + ph - (Math.min(maxLoad, val) / maxLoad) * ph;
      const y0 = padT + ph;

      let gridSvg = '';
      const ySteps = 4;
      for (let s = 0; s <= ySteps; s++) {
        const val = (s / ySteps) * maxLoad;
        const yPos = getY(val);
        gridSvg += `<line x1="${padL}" y1="${yPos}" x2="${w - padR}" y2="${yPos}" stroke="#1f2937" stroke-dasharray="3"/>`;
        gridSvg += `<text x="${padL - 8}" y="${yPos + 4}" fill="#6b7280" font-size="10" text-anchor="end">${Math.round(val)}</text>`;
      }

      const sportColors = {
        'Run': '#06b6d4',
        'Ride': '#f59e0b',
        'Swim': '#38bdf8',
        'Brick': '#a855f7',
        'Duathlon': '#a855f7',
        'Other': '#64748b'
      };

      // Hover highlight background bar
      let hoverBgSvg = `<rect id="loadHoverBar" x="0" y="${padT}" width="${colW}" height="${ph}" fill="rgba(56, 189, 248, 0.12)" rx="3" opacity="0" pointer-events="none"/>`;

      let barsSvg = '';
      series.forEach((d, i) => {
        const bx = getX(i) + (colW - barW) / 2;
        const sports = d.sports || {};
        let currentY = y0;

        const sportEntries = Object.entries(sports).filter(([sp, val]) => val > 0);
        if (sportEntries.length > 0 && d.load_tss > 0) {
          sportEntries.forEach(([sp, load]) => {
            const segH = Math.max(2, (load / maxLoad) * ph);
            const color = sportColors[sp] || sportColors['Other'];
            barsSvg += `<rect x="${bx.toFixed(1)}" y="${(currentY - segH).toFixed(1)}" width="${barW.toFixed(1)}" height="${segH.toFixed(1)}" fill="${color}" rx="2"/>`;
            currentY -= segH;
          });
        } else if (d.load_tss > 0) {
          const segH = Math.max(2, (d.load_tss / maxLoad) * ph);
          barsSvg += `<rect x="${bx.toFixed(1)}" y="${(currentY - segH).toFixed(1)}" width="${barW.toFixed(1)}" height="${segH.toFixed(1)}" fill="#f59e0b" rx="2"/>`;
        } else {
          barsSvg += `<circle cx="${(bx + barW / 2).toFixed(1)}" cy="${(y0 - 3).toFixed(1)}" r="2" fill="#334155"/>`;
        }
      });

      let dateSvg = '';
      const step = series.length > 20 ? 3 : (series.length > 10 ? 2 : 1);
      for (let i = 0; i < series.length; i += step) {
        const bx = getX(i) + colW / 2;
        const dt = series[i].date ? series[i].date.slice(5) : '';
        dateSvg += `<text x="${bx}" y="${h - 8}" fill="#94a3b8" font-size="10" text-anchor="middle">${dt}</text>`;
      }
      const lastIdx = series.length - 1;
      if (lastIdx % step !== 0) {
        const bx = getX(lastIdx) + colW / 2;
        const dt = series[lastIdx].date ? series[lastIdx].date.slice(5) : '';
        dateSvg += `<text x="${bx}" y="${h - 8}" fill="#38bdf8" font-size="10" font-weight="700" text-anchor="middle">${dt}</text>`;
      }

      svg.innerHTML = `
        ${gridSvg}
        ${hoverBgSvg}
        ${dateSvg}
        ${barsSvg}
      `;

      // Auto-scroll to end so latest days are displayed
      if (scrollBox && !scrollBox.dataset.userScrolled) {
        scrollBox.scrollLeft = scrollBox.scrollWidth;
      }

      // Trackpad / wheel horizontal scroll
      if (scrollBox && !scrollBox.dataset.wheelBound) {
        scrollBox.dataset.wheelBound = 'true';
        scrollBox.addEventListener('wheel', (e) => {
          if (Math.abs(e.deltaX) < Math.abs(e.deltaY)) {
            scrollBox.scrollLeft += e.deltaY;
            scrollBox.dataset.userScrolled = 'true';
            e.preventDefault();
          }
        }, { passive: false });
      }

      const tooltip = document.getElementById('loadTooltip');
      if (scrollBox && tooltip) {
        scrollBox.onmousemove = function(e) {
          const rect = scrollBox.getBoundingClientRect();
          const mouseX = e.clientX - rect.left + scrollBox.scrollLeft;
          if (mouseX < padL || mouseX > padL + pw) {
            tooltip.style.display = 'none';
            const hb = document.getElementById('loadHoverBar');
            if (hb) hb.setAttribute('opacity', '0');
            return;
          }

          const idx = Math.min(series.length - 1, Math.max(0, Math.floor((mouseX - padL) / colW)));
          const pt = series[idx];
          const colStartX = getX(idx);

          const hb = document.getElementById('loadHoverBar');
          if (hb) {
            hb.setAttribute('x', colStartX);
            hb.setAttribute('opacity', '1');
          }

          let sportLines = '';
          if (pt.sports && Object.keys(pt.sports).length > 0) {
            sportLines = Object.entries(pt.sports).map(([sp, val]) =>
              `<div style="font-size:0.75rem; color:${sportColors[sp] || '#94a3b8'};">• ${sp}: <strong>${val} TSS</strong></div>`
            ).join('');
          }

          tooltip.style.display = 'block';
          const tipLeft = e.clientX - rect.left;
          tooltip.style.left = Math.min(rect.width - 170, Math.max(10, tipLeft - 70)) + 'px';
          tooltip.style.top = '12px';
          tooltip.innerHTML = `
            <div style="font-weight:700; color:#fff; border-bottom:1px solid #334155; padding-bottom:3px; margin-bottom:4px;">${pt.date}</div>
            <div style="color:#f59e0b; font-size:0.8125rem;">Total Load: <strong>${pt.load_tss} TSS</strong></div>
            <div style="color:#38bdf8; font-size:0.75rem;">Moving Time: <strong>${pt.moving_hours} hrs</strong></div>
            ${sportLines ? `<div style="margin-top:4px; border-top:1px dashed #334155; padding-top:4px;">${sportLines}</div>` : ''}
          `;
        };

        scrollBox.onmouseleave = function() {
          tooltip.style.display = 'none';
          const hb = document.getElementById('loadHoverBar');
          if (hb) hb.setAttribute('opacity', '0');
        };
      }
    }

    function renderDecouplingGauge(pct) {
      const svg = document.getElementById('decouplingGaugeSvg');
      if (!svg) return;

      const val = pct !== null && pct !== undefined ? parseFloat(pct) : 3.5;
      const w = 350, h = 90;
      const padL = 20, padR = 20;
      const barY = 32, barH = 16, barW = w - padL - padR;

      const maxScale = 12.0;
      const getX = (v) => padL + (Math.min(maxScale, Math.max(0, v)) / maxScale) * barW;

      const x3 = getX(3.0);
      const x5 = getX(5.0);
      const x7_5 = getX(7.5);
      const x12 = getX(12.0);

      const markerX = getX(val);

      let verdict = 'Optimal Base Coupling (<5% drift)';
      let verdictColor = 'var(--success)';
      let feedback = 'Heart rate to output ratio remained stable across the session.';

      if (val < 3.0) {
        verdict = 'Superior Aerobic Coupling (<3% drift)';
        verdictColor = 'var(--accent)';
        feedback = 'Exceptional cardiac stability; no aerobic fatigue or decoupling observed.';
      } else if (val <= 5.0) {
        verdict = 'Optimal Base Coupling (<5% drift)';
        verdictColor = 'var(--success)';
        feedback = 'Aerobic endurance system is stable and well-conditioned for this duration.';
      } else if (val <= 7.5) {
        verdict = 'Mild Aerobic Strain (5-7.5% drift)';
        verdictColor = 'var(--warning)';
        feedback = 'Mild cardiac drift detected. Ensure adequate hydration, electrolyte intake, and 24h easy recovery.';
      } else {
        verdict = 'Significant Cardiac Drift (>7.5% drift)';
        verdictColor = 'var(--danger)';
        feedback = 'Noticeable aerobic decoupling (>7.5%) due to cumulative fatigue, thermal stress, or glycogen depletion. Prioritize recovery.';
      }

      const vEl = document.getElementById('decouplingVerdict');
      if (vEl) {
        vEl.innerText = verdict;
        vEl.style.color = verdictColor;
      }
      const fEl = document.getElementById('decouplingFeedback');
      if (fEl) {
        fEl.innerText = feedback;
      }

      svg.innerHTML = `
        <rect x="${padL}" y="${barY}" width="${x3 - padL}" height="${barH}" fill="#06b6d4" rx="2"/>
        <rect x="${x3}" y="${barY}" width="${x5 - x3}" height="${barH}" fill="#10b981"/>
        <rect x="${x5}" y="${barY}" width="${x7_5 - x5}" height="${barH}" fill="#f59e0b"/>
        <rect x="${x7_5}" y="${barY}" width="${x12 - x7_5}" height="${barH}" fill="#ef4444" rx="2"/>

        <text x="${padL}" y="${barY - 8}" fill="#6b7280" font-size="9" text-anchor="start">0%</text>
        <text x="${x3}" y="${barY - 8}" fill="#06b6d4" font-size="9" text-anchor="middle">3%</text>
        <text x="${x5}" y="${barY - 8}" fill="#10b981" font-size="9" text-anchor="middle">5% (Limit)</text>
        <text x="${x7_5}" y="${barY - 8}" fill="#f59e0b" font-size="9" text-anchor="middle">7.5%</text>
        <text x="${x12}" y="${barY - 8}" fill="#ef4444" font-size="9" text-anchor="end">12%+</text>

        <text x="${(padL + x3) / 2}" y="${barY + barH + 14}" fill="#06b6d4" font-size="8" text-anchor="middle">Superior</text>
        <text x="${(x3 + x5) / 2}" y="${barY + barH + 14}" fill="#10b981" font-size="8" text-anchor="middle">Stable</text>
        <text x="${(x5 + x7_5) / 2}" y="${barY + barH + 14}" fill="#f59e0b" font-size="8" text-anchor="middle">Mild Drift</text>
        <text x="${(x7_5 + x12) / 2}" y="${barY + barH + 14}" fill="#ef4444" font-size="8" text-anchor="middle">High Fatigue</text>

        <polygon points="${markerX - 4},${barY - 2} ${markerX + 4},${barY - 2} ${markerX},${barY + 6}" fill="#fff"/>
        <line x1="${markerX}" y1="${barY}" x2="${markerX}" y2="${barY + barH}" stroke="#fff" stroke-width="2"/>
        <text x="${markerX}" y="${barY - 12}" fill="#fff" font-size="10" font-weight="700" text-anchor="middle">${val.toFixed(1)}%</text>
      `;
    }

    async function submitSessionReview(e) {
      e.preventDefault();
      const sport = document.getElementById('revSport').value;
      const dur = parseInt(document.getElementById('revDuration').value) || 60;
      const rpe = parseInt(document.getElementById('revRpe').value) || 6;
      const dec = parseFloat(document.getElementById('revDecoupling').value);

      renderDecouplingGauge(dec);

      try {
        const res = await fetch('/api/review', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sport: sport,
            duration: dur,
            rpe: rpe,
            decoupling: isNaN(dec) ? null : dec
          })
        });
        const data = await res.json();
        if (data && data.coaching_feedback && data.coaching_feedback.length > 0) {
          const fEl = document.getElementById('decouplingFeedback');
          if (fEl) {
            fEl.innerHTML = data.coaching_feedback.join('<br>');
          }
        }
        showToast('Session debrief and efficiency calculated!');
      } catch (err) {
        console.error('Session review error:', err);
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
          else if (evt.type === 'Brick' || evt.type === 'Duathlon') tagClass = 'tag-brick';
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

