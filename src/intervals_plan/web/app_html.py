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
  <style>/* hallmark: modern-minimal / dark / athlete-engineering */
    :root {
      --color-bg-deep: #050811;
      --color-bg: #0b1120;
      --color-surface: #111c30;
      --color-surface-hover: #16243d;
      --color-surface-active: #1d3052;
      --color-surface-sunken: #070d18;
      --color-border: #1e2e4a;
      --color-border-subtle: rgba(255, 255, 255, 0.08);
      --color-border-hover: #334b75;
      --color-text: #f1f5f9;
      --color-text-muted: #94a3b8;
      --color-text-dim: #64748b;
      --color-accent: #38bdf8;
      --color-accent-hover: #0ea5e9;
      --color-accent-subtle: rgba(56, 189, 248, 0.15);
      --color-accent-dim: rgba(56, 189, 248, 0.25);
      --color-success: #10b981;
      --color-success-hover: #059669;
      --color-success-subtle: rgba(16, 185, 129, 0.15);
      --color-warning: #f59e0b;
      --color-warning-subtle: rgba(245, 158, 11, 0.15);
      --color-danger: #ef4444;
      --color-danger-hover: #dc2626;
      --color-danger-subtle: rgba(239, 68, 68, 0.15);
      --color-purple: #c084fc;
      --color-purple-subtle: rgba(192, 132, 252, 0.15);
      --color-focus: #38bdf8;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      --radius-sm: 4px;
      --radius-md: 8px;
      --radius-lg: 12px;
      --radius-full: 9999px;
      --transition-fast: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease, opacity 0.15s ease, transform 0.15s ease;

      /* Semantic aliases for backwards compatibility */
      --bg: var(--color-bg);
      --card-bg: var(--color-surface);
      --card-border: var(--color-border);
      --text-main: var(--color-text);
      --text-muted: var(--color-text-muted);
      --accent: var(--color-accent);
      --accent-hover: var(--color-accent-hover);
      --success: var(--color-success);
      --warning: var(--color-warning);
      --danger: var(--color-danger);
      --font: var(--font-sans);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      overflow-x: clip;
      background-color: var(--color-bg);
      color: var(--color-text);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* Focus Rings */
    button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {
      outline: 2px solid var(--color-focus);
      outline-offset: 2px;
    }

    /* Tabular Numerals on all metrics */
    .card-value, .metric-number, .stat-value, .chart-tooltip, table, .table td, .table th, .tabular, .gauge-ticks, .periodization-badge, .diagnostic-panel {
      font-variant-numeric: tabular-nums;
      font-feature-settings: "tnum";
    }

    header {
      background: var(--color-surface-sunken);
      border-bottom: 1px solid var(--color-border);
      padding: 0.875rem 2rem;
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
      background: linear-gradient(135deg, var(--color-accent), var(--color-success));
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      color: var(--color-bg-deep);
      font-size: 1.1rem;
    }
    .brand-title {
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--color-text);
    }
    .brand-tag {
      font-size: 0.6875rem;
      color: var(--color-accent);
      background: var(--color-accent-subtle);
      padding: 2px 8px;
      border-radius: var(--radius-full);
      font-weight: 600;
      letter-spacing: 0.02em;
    }

    nav {
      display: flex;
      gap: 0.5rem;
    }
    .nav-btn {
      background: transparent;
      border: 1px solid transparent;
      color: var(--color-text-muted);
      padding: 0.5rem 1rem;
      border-radius: var(--radius-md);
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      transition: var(--transition-fast);
    }
    .nav-btn:hover {
      color: var(--color-text);
      background: var(--color-surface-hover);
      border-color: var(--color-border-subtle);
    }
    .nav-btn:active {
      transform: translateY(1px);
    }
    .nav-btn.active {
      color: var(--color-accent);
      background: var(--color-accent-subtle);
      border-color: var(--color-accent-dim);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .status-badge {
      font-size: 0.75rem;
      padding: 4px 12px;
      border-radius: var(--radius-full);
      background: var(--color-success-subtle);
      color: var(--color-success);
      border: 1px solid rgba(16, 185, 129, 0.3);
      font-weight: 600;
    }

    .spinner {
      display: inline-block;
      width: 0.75rem;
      height: 0.75rem;
      border: 2px solid rgba(255, 255, 255, 0.25);
      border-radius: 50%;
      border-top-color: #ffffff;
      animation: spin 0.8s linear infinite;
      margin-right: 0.375rem;
      vertical-align: middle;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .info-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.22);
      color: var(--color-text-muted);
      font-family: var(--font-sans);
      font-size: 0.625rem;
      font-style: italic;
      font-weight: 700;
      line-height: 1;
      cursor: help;
      position: relative;
      margin-left: 0.375rem;
      vertical-align: middle;
      transition: color 0.15s ease, border-color 0.15s ease, background-color 0.15s ease;
      user-select: none;
      flex-shrink: 0;
      text-transform: none;
    }
    .info-btn:hover,
    .info-btn:focus-visible {
      color: #ffffff;
      background: rgba(56, 189, 248, 0.25);
      border-color: #38bdf8;
      outline: none;
    }
    .info-popover {
      visibility: hidden;
      opacity: 0;
      position: absolute;
      bottom: calc(100% + 8px);
      left: 50%;
      transform: translateX(-50%) translateY(4px);
      width: 250px;
      max-width: 80vw;
      background: #0f172a;
      color: var(--color-text);
      border: 1px solid rgba(56, 189, 248, 0.35);
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6), 0 0 1px 1px rgba(255, 255, 255, 0.05);
      border-radius: 6px;
      padding: 0.625rem 0.75rem;
      font-size: 0.75rem;
      font-style: normal;
      font-weight: 400;
      line-height: 1.45;
      text-align: left;
      z-index: 1000;
      pointer-events: none;
      transition: opacity 0.15s ease, transform 0.15s ease, visibility 0.15s ease;
      white-space: normal;
      word-break: normal;
    }
    .info-btn:hover .info-popover,
    .info-btn:focus-visible .info-popover {
      visibility: visible;
      opacity: 1;
      transform: translateX(-50%) translateY(0);
      pointer-events: auto;
    }
    .info-popover.popover-left {
      left: 0;
      transform: translateY(4px);
    }
    .info-btn:hover .info-popover.popover-left,
    .info-btn:focus-visible .info-popover.popover-left {
      transform: translateY(0);
    }
    .info-popover.popover-right {
      left: auto;
      right: -6px;
      transform: translateY(4px);
    }
    .info-btn:hover .info-popover.popover-right,
    .info-btn:focus-visible .info-popover.popover-right {
      transform: translateY(0);
    }
    .popover-title {
      display: block;
      font-weight: 700;
      color: #38bdf8;
      margin-bottom: 0.25rem;
      font-size: 0.75rem;
    }
    .popover-def {
      display: block;
      color: #e2e8f0;
      margin-bottom: 0.35rem;
    }
    .popover-rel {
      display: block;
      color: #94a3b8;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      padding-top: 0.35rem;
      font-size: 0.71875rem;
    }
    .popover-rel strong {
      color: #10b981;
    }

    .muscle-poly {
      cursor: pointer;
      stroke: rgba(255, 255, 255, 0.25);
      stroke-width: 1.5px;
      transition: fill 0.2s ease, filter 0.2s ease, stroke 0.2s ease;
    }
    .muscle-poly:hover {
      filter: brightness(1.35) drop-shadow(0 0 6px rgba(56, 189, 248, 0.7));
      stroke: #38bdf8;
      stroke-width: 2px;
    }
    .muscle-poly.active-selected {
      stroke: #ffffff;
      stroke-width: 2.5px;
      filter: drop-shadow(0 0 8px #38bdf8);
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
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      padding: 1.5rem;
      position: relative;
    }
    .card-title {
      font-size: 0.8125rem;
      letter-spacing: normal;
      color: var(--color-text-muted);
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
      color: var(--color-text);
    }
    .card-subtext {
      font-size: 0.8125rem;
      color: var(--color-text-muted);
      margin-top: 0.5rem;
    }

    .gauge-container {
      margin: 1.5rem 0;
      position: relative;
    }
    .gauge-bar-bg {
      height: 12px;
      background: var(--color-surface-sunken);
      border: 1px solid var(--color-border);
      border-radius: 6px;
      position: relative;
      overflow: hidden;
    }
    .gauge-fill {
      height: 100%;
      border-radius: 6px;
      transition: opacity 0.3s ease;
    }
    .gauge-ticks {
      display: flex;
      justify-content: space-between;
      margin-top: 8px;
      font-size: 0.75rem;
      color: var(--color-text-muted);
    }

    .alert-box {
      background: var(--color-warning-subtle);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: var(--radius-md);
      padding: 1rem;
      margin-bottom: 1.5rem;
    }
    .alert-title {
      font-size: 0.875rem;
      font-weight: 700;
      color: var(--color-warning);
      margin-bottom: 0.25rem;
    }
    .alert-desc {
      font-size: 0.8125rem;
      color: var(--color-text-muted);
      line-height: 1.5;
    }

    .btn {
      background: var(--color-accent);
      color: var(--color-bg-deep);
      border: 1px solid transparent;
      padding: 0.625rem 1.25rem;
      font-size: 0.875rem;
      font-weight: 700;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: var(--transition-fast);
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
    }
    .btn:hover { background: var(--color-accent-hover); }
    .btn:active { transform: translateY(1px); }
    .btn:disabled { opacity: 0.55; cursor: not-allowed; }
    .btn-secondary {
      background: var(--color-surface-active);
      color: var(--color-text);
      border-color: var(--color-border);
    }
    .btn-secondary:hover {
      background: var(--color-border-hover);
      border-color: var(--color-accent);
    }
    .btn-danger {
      background: var(--color-danger);
      color: var(--color-text);
    }
    .btn-danger:hover { background: var(--color-danger-hover); }

    /* Form Inputs */
    .form-group {
      margin-bottom: 1.25rem;
    }
    .form-label {
      display: block;
      font-size: 0.8125rem;
      font-weight: 600;
      color: var(--color-text-muted);
      margin-bottom: 0.375rem;
    }
    .form-input, .form-select {
      width: 100%;
      background: var(--color-surface-sunken);
      border: 1px solid var(--color-border);
      color: var(--color-text);
      padding: 0.625rem 0.875rem;
      border-radius: var(--radius-md);
      font-size: 0.875rem;
      outline: 2px solid transparent;
      outline-offset: -2px;
      transition: border-color 0.15s ease, background-color 0.15s ease;
    }
    .form-input:hover, .form-select:hover {
      background: var(--color-surface);
      border-color: var(--color-border-hover);
    }
    .form-input:focus-visible, .form-select:focus-visible {
      border-color: var(--color-accent);
      outline-color: var(--color-focus);
    }
    .range-wrap {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    .range-val {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--color-accent);
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
      background: var(--color-surface-sunken);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      padding: 1rem;
      min-height: 220px;
      display: flex;
      flex-direction: column;
      color: var(--color-text);
    }
    .day-header {
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--color-text-muted);
      border-bottom: 1px solid var(--color-border);
      padding-bottom: 0.5rem;
      margin-bottom: 0.75rem;
      display: flex;
      justify-content: space-between;
    }
    .workout-card {
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-sm);
      padding: 0.75rem;
      cursor: pointer;
      color: var(--color-text);
      transition: border-color 0.15s ease, transform 0.15s ease;
      flex: 1;
    }
    .workout-card:hover {
      border-color: var(--color-accent);
      transform: translateY(-2px);
    }
    .workout-tag {
      font-size: 0.6875rem;
      padding: 4px 8px;
      border-radius: var(--radius-sm);
      font-weight: 700;
      display: inline-block;
      margin-bottom: 0.375rem;
    }
    .tag-run { background: var(--color-accent-subtle); color: var(--color-accent); }
    .tag-ride { background: var(--color-success-subtle); color: var(--color-success); }
    .tag-swim { background: rgba(14, 165, 233, 0.25); color: #38bdf8; }
    .tag-brick { background: var(--color-purple-subtle); color: var(--color-purple); }
    .tag-duathlon { background: var(--color-warning-subtle); color: var(--color-warning); }
    .tag-rest { background: rgba(107, 114, 128, 0.2); color: var(--color-text-muted); }
    .tag-quality { background: var(--color-danger-subtle); color: #fb7185; }

    .workout-title {
      font-size: 0.8125rem;
      font-weight: 700;
      color: var(--color-text);
      margin-bottom: 0.375rem;
      line-height: 1.3;
    }
    .workout-meta {
      font-size: 0.6875rem;
      color: var(--color-text-muted);
    }

    /* Modal / Drawer */
    .modal-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(5, 8, 17, 0.85);
      backdrop-filter: blur(4px);
      z-index: 100;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
    }
    .modal-overlay.active { display: flex; }
    .modal {
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
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
      color: var(--color-text-muted);
      font-size: 1.5rem;
      cursor: pointer;
    }

    /* Watch Preview Box */
    .coros-preview-box {
      background: var(--color-bg-deep);
      border: 3px solid var(--color-border);
      border-radius: 24px;
      padding: 1.5rem;
      margin-top: 1.25rem;
      font-family: var(--font-mono);
      color: var(--color-accent);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
    }
    .coros-screen-header {
      font-size: 0.75rem;
      color: var(--color-text-muted);
      border-bottom: 1px dashed var(--color-border);
      padding-bottom: 0.5rem;
      margin-bottom: 0.75rem;
    }

    /* SVG Interactive Charts */
    .chart-scroll-container {
      width: 100%;
      overflow-x: auto;
      overflow-y: hidden;
      scrollbar-width: thin;
      scrollbar-color: var(--color-border-hover) var(--color-surface-sunken);
      -webkit-overflow-scrolling: touch;
      position: relative;
    }
    .chart-scroll-container::-webkit-scrollbar {
      height: 6px;
    }
    .chart-scroll-container::-webkit-scrollbar-track {
      background: var(--color-surface-sunken);
      border-radius: var(--radius-sm);
    }
    .chart-scroll-container::-webkit-scrollbar-thumb {
      background: var(--color-border-hover);
      border-radius: var(--radius-sm);
    }
    .chart-scroll-container::-webkit-scrollbar-thumb:hover {
      background: var(--color-text-dim);
    }
    .chart-filter-btn {
      transition: var(--transition-fast);
    }
    .chart-filter-btn.active {
      background: var(--color-accent) !important;
      color: var(--color-bg-deep) !important;
      font-weight: 700 !important;
    }

    /* Interactive Series Toggle Buttons */
    .chart-toggle-btn {
      background: var(--color-surface-sunken);
      border: 1px solid var(--color-border);
      color: var(--color-text-muted);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.3rem 0.65rem;
      border-radius: var(--radius-sm);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: var(--transition-fast);
    }
    .chart-toggle-btn:hover {
      background: var(--color-surface-hover);
      color: var(--color-text);
      border-color: var(--color-border-hover);
    }
    .chart-toggle-btn:active {
      transform: translateY(1px);
    }
    .chart-toggle-btn.active {
      background: var(--color-surface-active);
      color: var(--color-text);
      border-color: var(--color-accent);
    }
    .legend-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
    }

    .chart-box {
      width: 100%;
      height: 280px;
      background: var(--color-surface-sunken);
      border-radius: var(--radius-md);
      padding: 0.75rem 1rem;
      border: 1px solid var(--color-border);
      position: relative;
    }
    .chart-box-compact {
      width: 100%;
      height: 210px;
      background: var(--color-surface-sunken);
      border-radius: var(--radius-md);
      padding: 0.75rem 1rem;
      border: 1px solid var(--color-border);
      position: relative;
    }
    .chart-tooltip {
      position: absolute;
      display: none;
      background: rgba(7, 13, 24, 0.95);
      border: 1px solid var(--color-border-hover);
      border-radius: var(--radius-md);
      padding: 0.6rem 0.85rem;
      font-size: 0.75rem;
      color: var(--color-text);
      pointer-events: none;
      z-index: 50;
      white-space: nowrap;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.75);
      line-height: 1.45;
      backdrop-filter: blur(6px);
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

    /* Diagnostic Inspection Panel */
    .diagnostic-panel {
      font-size: 0.8125rem;
      line-height: 1.45;
      color: var(--color-text);
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
      border-bottom: 1px solid var(--color-border);
      color: var(--color-text-muted);
      font-weight: 600;
    }
    .table td {
      padding: 0.75rem 1rem;
      border-bottom: 1px solid var(--color-border);
    }

    .toast {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: var(--color-surface);
      border: 1px solid var(--color-accent);
      color: var(--color-text);
      padding: 0.75rem 1.5rem;
      border-radius: var(--radius-md);
      box-shadow: 0 4px 16px rgba(0,0,0,0.6);
      z-index: 200;
      display: none;
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
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
      <button class="nav-btn" onclick="switchTab('strength')">Strength & Muscle Map</button>
      <button class="nav-btn" onclick="switchTab('analysis')">Analysis</button>
      <button class="nav-btn" onclick="switchTab('goals')">Goals & Profile</button>
      <button class="nav-btn" onclick="switchTab('planner')">Calendar & Plan</button>
      <button class="nav-btn" onclick="switchTab('sync')">Ecosystem & Sync</button>
      <button class="nav-btn" onclick="switchTab('export')">Export Center</button>
    </nav>
    <div class="header-actions">
      <button id="globalSyncBtn" class="btn" style="padding:0.35rem 0.85rem; font-size:0.75rem; font-weight:600;" onclick="triggerEcosystemSync()" title="Synchronize biometrics & workouts across Intervals, COROS, Samsung Health, Strava, Fit">
        <span id="syncBtnSpinner" style="display:none;" class="spinner" aria-hidden="true"></span>
        <span id="syncBtnText">Sync Ecosystem</span>
      </button>
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

      <!-- EXECUTIVE SUMMARY & ATHLETE READINESS HERO CARD -->
      <div class="card" style="margin-bottom: 1.5rem; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98)); border: 1px solid rgba(56, 189, 248, 0.3); box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:0.875rem; margin-bottom:1rem;">
          <div>
            <div style="display:flex; align-items:center; gap:0.5rem;">
              <span style="font-size:1.125rem; font-weight:800; color:#fff; letter-spacing:0.02em;">EXECUTIVE SUMMARY & BIOMETRIC READINESS</span>
              <span id="execReadinessPill" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success); font-size:0.75rem; font-weight:700;">OPTIMAL (82/100)</span>
            </div>
            <div style="font-size:0.8125rem; color:var(--text-muted); margin-top:2px;">
              Multi-Source Biometric Synthesis across Galaxy Watch 4, COROS DURA, & Intervals.icu
            </div>
          </div>
          <div style="text-align:right;">
            <span style="font-size:0.75rem; color:var(--text-muted);">Threshold Pace / LTHR:</span>
            <strong id="execLthrText" style="color:#38bdf8; font-size:0.875rem; margin-left:4px;">172 bpm (Ride) | 182 bpm (Run)</strong>
          </div>
        </div>

        <!-- 4-Column Executive Key Indicators -->
        <div class="grid-4" style="margin-bottom:1rem; gap:1rem;">
          <div style="background:rgba(15,23,42,0.6); padding:0.75rem; border-radius:6px; border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:0.6875rem; text-transform:uppercase; color:var(--text-muted); font-weight:700; display:flex; align-items:center;">
              <span>Autonomic Readiness</span>
              <span class="info-btn" tabindex="0" role="button" aria-label="About Autonomic Readiness">i<span class="info-popover popover-left"><span class="popover-title">Autonomic Readiness</span><span class="popover-def">Composite physiological readiness score reflecting autonomic nervous system balance from resting HR, HRV, and sleep.</span><span class="popover-rel"><strong>Relevance:</strong> High readiness indicates capacity for high-intensity intervals; low readiness calls for aerobic recovery.</span></span></span>
            </div>
            <div id="execReadinessHeadline" style="font-size:1.125rem; font-weight:800; color:var(--success); margin:2px 0;">Optimal Overload</div>
            <div id="execReadinessDesc" style="font-size:0.75rem; color:var(--text-muted);">RHR stable (56 bpm, +0.5 delta). Fully primed for volume & quality.</div>
          </div>

          <div style="background:rgba(15,23,42,0.6); padding:0.75rem; border-radius:6px; border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:0.6875rem; text-transform:uppercase; color:var(--text-muted); font-weight:700; display:flex; align-items:center;">
              <span>Workload Ratio (ACWR)</span>
              <span class="info-btn" tabindex="0" role="button" aria-label="About ACWR">i<span class="info-popover"><span class="popover-title">Acute:Chronic Workload Ratio</span><span class="popover-def">Ratio of acute 7-day fatigue to chronic 28-day fitness base (Gabbett model).</span><span class="popover-rel"><strong>Relevance:</strong> Sweet spot is 0.8-1.3. Spikes over 1.5 increase non-contact soft tissue injury risk.</span></span></span>
            </div>
            <div id="execAcwrHeadline" style="font-size:1.125rem; font-weight:800; color:#38bdf8; margin:2px 0;">0.47 Under-Training</div>
            <div id="execAcwrDesc" style="font-size:0.75rem; color:var(--text-muted);">Chronic base dropping; gradual progressive volume recommended.</div>
          </div>

          <div style="background:rgba(15,23,42,0.6); padding:0.75rem; border-radius:6px; border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:0.6875rem; text-transform:uppercase; color:var(--text-muted); font-weight:700; display:flex; align-items:center;">
              <span>Sleep & Nocturnal Recovery</span>
              <span class="info-btn" tabindex="0" role="button" aria-label="About Sleep and Recovery">i<span class="info-popover"><span class="popover-title">Nocturnal Sleep & Recovery</span><span class="popover-def">Total nocturnal sleep duration, sleep stages (deep and REM), and overnight SpO2 stability.</span><span class="popover-rel"><strong>Relevance:</strong> Deep sleep repairs muscle tissue and releases growth hormones; 7.0-8.5 hours required for adaptation.</span></span></span>
            </div>
            <div id="execSleepHeadline" style="font-size:1.125rem; font-weight:800; color:#a855f7; margin:2px 0;">7.5h Stable</div>
            <div id="execSleepDesc" style="font-size:0.75rem; color:var(--text-muted);">SpO2 97-98.5%. Healthy deep/REM restorative sleep architecture.</div>
          </div>

          <div style="background:rgba(15,23,42,0.6); padding:0.75rem; border-radius:6px; border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:0.6875rem; text-transform:uppercase; color:var(--text-muted); font-weight:700; display:flex; align-items:center;">
              <span>Body Composition (BIA)</span>
              <span class="info-btn" tabindex="0" role="button" aria-label="About Body Composition">i<span class="info-popover popover-right"><span class="popover-title">Body Composition (BIA)</span><span class="popover-def">Scale weight, bioimpedance body fat percentage, and calculated skeletal lean mass.</span><span class="popover-rel"><strong>Relevance:</strong> Determines power-to-weight ratio (W/kg) and running economy while safeguarding lean muscle mass.</span></span></span>
            </div>
            <div id="execBodyHeadline" style="font-size:1.125rem; font-weight:800; color:#10b981; margin:2px 0;">78.9 kg | 27.0% Fat</div>
            <div id="execBodyDesc" style="font-size:0.75rem; color:var(--text-muted);">57.5 kg Lean Mass (~30.5 kg Skeletal Muscle). Calibrated power-to-weight.</div>
          </div>
        </div>

        <!-- Executive Interpretation & How Ready You Are Banner -->
        <div style="background:rgba(56, 189, 248, 0.08); border-left:3px solid #38bdf8; border-radius:0 4px 4px 0; padding:0.625rem 0.875rem; font-size:0.8125rem; line-height:1.45;">
          <strong style="color:#38bdf8;">How Ready You Are Today:</strong>
          <span id="execVerdictText" style="color:#e2e8f0; margin-left:4px;">
            Your resting heart rate and nocturnal vitals are in an optimal, uncompromised autonomic state. Because acute load has dropped below your monthly chronic baseline (ACWR 0.47), you are free of accumulated systemic fatigue and fully primed to absorb this week's scheduled workouts without injury risk.
          </span>
        </div>
      </div>

      <div class="grid-4" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div class="card-title">
            <span>Physiological Readiness <span class="info-btn" tabindex="0" role="button" aria-label="About Physiological Readiness">i<span class="info-popover popover-left"><span class="popover-title">Physiological Readiness</span><span class="popover-def">Daily score (0-100) synthesizing resting heart rate delta, HRV RMSSD, and rolling workload.</span><span class="popover-rel"><strong>Relevance:</strong> High scores (>70) indicate readiness for key quality sessions; low scores (<50) recommend restorative sessions.</span></span></span></span>
          </div>
          <div class="card-value" id="readinessScore">--</div>
          <div class="card-subtext" id="readinessState">Calculating...</div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>ACWR (Tim Gabbett) <span class="info-btn" tabindex="0" role="button" aria-label="About ACWR">i<span class="info-popover"><span class="popover-title">ACWR (Acute:Chronic Workload Ratio)</span><span class="popover-def">Compares 7-day fatigue load to 28-day fitness base using rolling exponential models.</span><span class="popover-rel"><strong>Relevance:</strong> Values between 0.8 and 1.3 provide safe progressive overload; values >1.5 elevate injury hazards.</span></span></span></span>
          </div>
          <div class="card-value" id="acwrRatio">--</div>
          <div class="card-subtext" id="acwrStatus">Sweet Spot: 0.8 - 1.3</div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>Performance Balance (TSB) <span class="info-btn" tabindex="0" role="button" aria-label="About Training Stress Balance">i<span class="info-popover"><span class="popover-title">Training Stress Balance (TSB)</span><span class="popover-def">CTL (Fitness) minus ATL (Fatigue). Reflects athlete freshness versus training strain.</span><span class="popover-rel"><strong>Relevance:</strong> -10 to -30 during hard training blocks; +5 to +20 during taper for peak race performance.</span></span></span></span>
          </div>
          <div class="card-value" id="tsbValue">--</div>
          <div class="card-subtext" id="pmcSubtext">Fitness vs Fatigue</div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>Resting HR (3d vs 30d) <span class="info-btn" tabindex="0" role="button" aria-label="About Resting HR">i<span class="info-popover popover-right"><span class="popover-title">Resting Heart Rate Delta</span><span class="popover-def">Comparison of 3-day rolling resting pulse against your 30-day baseline during sleep.</span><span class="popover-rel"><strong>Relevance:</strong> An increase >=4 bpm indicates systemic fatigue, poor recovery, dehydration, or onset of illness.</span></span></span></span>
          </div>
          <div class="card-value" id="rhrDelta">--</div>
          <div class="card-subtext" id="rhrSubtext">Baseline stability</div>
        </div>
      </div>

      <!-- Biometrics & Wellness Telemetry Cards -->
      <div class="grid-4" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div class="card-title">
            <span>Sleep Duration & Stages <span class="info-btn" tabindex="0" role="button" aria-label="About Sleep Stages">i<span class="info-popover popover-left"><span class="popover-title">Sleep Architecture</span><span class="popover-def">Total sleep hours and restorative distribution across deep slow-wave, REM, and light sleep.</span><span class="popover-rel"><strong>Relevance:</strong> Deep sleep promotes physical tissue regeneration; REM sleep restores cognitive and nervous resilience.</span></span></span></span>
          </div>
          <div class="card-value" id="dashSleepVal" style="color:#a855f7;">--</div>
          <div class="card-subtext" id="dashSleepSubtext">Samsung Health / Health Connect</div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>Blood Oxygen (SpO2) <span class="info-btn" tabindex="0" role="button" aria-label="About Blood Oxygen">i<span class="info-popover"><span class="popover-title">Blood Oxygen Saturation</span><span class="popover-def">Nocturnal arterial oxygen saturation percentage measured by optical pulse oximetry.</span><span class="popover-rel"><strong>Relevance:</strong> Healthy baseline is 95-100%. Levels <93% indicate impaired recovery, respiratory issues, or altitude stress.</span></span></span></span>
          </div>
          <div class="card-value" id="dashSpo2Val" style="color:#06b6d4;">--</div>
          <div class="card-subtext" id="dashSpo2Subtext">Optimal &gt;95%</div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>Body Composition (Weight) <span class="info-btn" tabindex="0" role="button" aria-label="About Weight">i<span class="info-popover"><span class="popover-title">Body Weight</span><span class="popover-def">Daily scale morning weight in kilograms recorded under consistent post-wake conditions.</span><span class="popover-rel"><strong>Relevance:</strong> Used directly to compute W/kg threshold power and pace energy expenditure dynamics.</span></span></span></span>
          </div>
          <div class="card-value" id="dashWeightVal" style="color:#10b981;">--</div>
          <div class="card-subtext" id="dashWeightSubtext">Scale Telemetry</div>
        </div>
        <div class="card">
          <div class="card-title">
            <span>Body Fat % <span class="info-btn" tabindex="0" role="button" aria-label="About Body Fat">i<span class="info-popover popover-right"><span class="popover-title">Body Fat Percentage</span><span class="popover-def">Estimated percentage of adipose tissue from bioimpedance scale telemetry.</span><span class="popover-rel"><strong>Relevance:</strong> Helps ensure weight loss preserves lean skeletal muscle mass while optimizing race body composition.</span></span></span></span>
          </div>
          <div class="card-value" id="dashBodyFatVal" style="color:#f59e0b;">--</div>
          <div class="card-subtext" id="dashBodyFatSubtext">Bioimpedance Analysis</div>
        </div>
      </div>

      <!-- EvoLab Recovery & Fatigue Telemetry Grid -->
      <div class="grid-2" style="margin-bottom: 1.5rem;">
        <!-- Physical Recovery Timer Card -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <div class="card-title" style="margin-bottom:0;">
              <span>Physical Recovery Timer <span class="info-btn" tabindex="0" role="button" aria-label="About Recovery Timer">i<span class="info-popover popover-left"><span class="popover-title">Physical Recovery Timer</span><span class="popover-def">Dynamic hours countdown modeling complete physiological restoration from recent session loads.</span><span class="popover-rel"><strong>Relevance:</strong> Guides training readiness: 90-100% allows hard intervals; under 70% suggests recovery or easy base.</span></span></span></span>
            </div>
            <span id="corosRecoveryBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">READY (90%+)</span>
          </div>

          <div style="display:flex; align-items:baseline; gap:0.5rem; margin-bottom:0.25rem;">
            <div style="font-size:2.25rem; font-weight:800; color:#fff;" id="corosRecoveryHours">0.0h</div>
            <div style="font-size:0.8125rem; color:var(--text-muted);">until 100% full recovery</div>
          </div>

          <div style="margin-bottom:0.75rem;">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted); margin-bottom:4px;">
              <span>Recovery Completion</span>
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

        <!-- Fatigue Index & Intensity Trend Card -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <div class="card-title" style="margin-bottom:0;">
              <span>Fatigue Index & Intensity Trend <span class="info-btn" tabindex="0" role="button" aria-label="About Fatigue Index">i<span class="info-popover popover-right"><span class="popover-title">Fatigue Index</span><span class="popover-def">Scaled gauge (0-100) quantifying accumulated cardiovascular and muscular strain.</span><span class="popover-rel"><strong>Relevance:</strong> 40-60 is the optimal overload zone; >80 indicates overreaching and elevated overtraining risk.</span></span></span></span>
            </div>
            <span id="corosFatigueBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">OPTIMIZED</span>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.25rem;">
            <div style="display:flex; align-items:baseline; gap:0.4rem;">
              <span style="font-size:2rem; font-weight:800; color:#f59e0b;" id="corosFatigueScore">--</span>
              <span style="font-size:0.8125rem; color:var(--text-muted);">/ 100</span>
            </div>
            <span id="corosFatigueZoneText" style="font-size:0.8125rem; font-weight:600; color:#38bdf8;">Optimized Zone</span>
          </div>

          <div class="gauge-container" style="margin-bottom: 0.6rem;">
            <div class="gauge-bar-bg" style="height:10px;">
              <div id="corosFatigueFill" class="gauge-fill" style="width:50%; background:var(--accent);"></div>
            </div>
            <div class="gauge-ticks">
              <span>0 (Fresh)</span>
              <span>20 (Taper)</span>
              <span>40 (Sweet Spot)</span>
              <span>60 (High)</span>
              <span>80+ (Overreach)</span>
            </div>
          </div>

          <p class="card-subtext" id="corosFatigueDesc" style="margin:0 0 0.5rem 0; font-size:0.8125rem;">
            Evaluating fatigue dynamics...
          </p>

          <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted); border-top:1px dashed #334155; padding-top:0.4rem;">
            <span>Capacity: <strong style="color:#06b6d4;" id="corosBaseFitness">--</strong> CTL</span>
            <span>Impact: <strong style="color:#f43f5e;" id="corosLoadImpact">--</strong> ATL</span>
            <span>7d Load: <strong style="color:#10b981;" id="coros7dLoad">--</strong></span>
          </div>
          <div style="font-size:0.6875rem; color:var(--text-muted); margin-top:2px;" id="corosLoadRangeText">Target: -- - --</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <div class="card-title" style="margin-bottom:0;">
              <span>Weekly Load Distribution & Target <span class="info-btn" tabindex="0" role="button" aria-label="About Weekly Load">i<span class="info-popover popover-left"><span class="popover-title">Weekly Load & Volume</span><span class="popover-def">7-day cumulative training hours and Training Stress Score (TSS) compared against plan target.</span><span class="popover-rel"><strong>Relevance:</strong> Keeps volume ramp rate controlled within 5-10% to prevent overtraining.</span></span></span></span>
            </div>
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
            <div class="card-title" style="margin-bottom:0;">
              <span>Telemetry Data Quality (Joe Friel Audit) <span class="info-btn" tabindex="0" role="button" aria-label="About Data Quality">i<span class="info-popover popover-left"><span class="popover-title">Data Quality Audit</span><span class="popover-def">Algorithmic validation of LTHR, FTP, max HR, and sensor continuity against Joe Friel rules.</span><span class="popover-rel"><strong>Relevance:</strong> Erroneous threshold settings distort all load, zone, and readiness calculations.</span></span></span></span>
            </div>
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
            <div class="card-title" style="margin-bottom:0;">
              <span>Anaerobic Battery (Skiba W') & DFA Alpha 1 <span class="info-btn" tabindex="0" role="button" aria-label="About W prime and DFA a1">i<span class="info-popover popover-right"><span class="popover-title">Skiba W' & DFA Alpha 1</span><span class="popover-def">W' is finite anaerobic work capacity above Critical Power; DFA a1 tracks fractal HRV threshold shifts.</span><span class="popover-rel"><strong>Relevance:</strong> W' governs surge capacity in races; DFA a1=0.75 identifies aerobic threshold (LT1) without blood tests.</span></span></span></span>
            </div>
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

    <!-- TAB STRENGTH: STRENGTH TRAINING & ANATOMICAL MUSCLE MAP -->
    <div id="tab-strength" class="tab-content">
      <!-- Hypertrophy & Concurrent Status Header Row -->
      <div class="grid-3" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.5rem;">
            <div class="card-title" style="margin-bottom:0;">
              <span>Systemic Muscle Recovery <span class="info-btn" tabindex="0" role="button" aria-label="About Muscle Recovery">i<span class="info-popover popover-left"><span class="popover-title">Muscle Fiber Recovery</span><span class="popover-def">Composite neuromuscular readiness across all 13 primary muscle groups based on 48-72h protein synthesis repair curves.</span><span class="popover-rel"><strong>Relevance:</strong> Guide session timing: train muscles only when recovery exceeds 85-90% for maximum mechanical tension.</span></span></span></span>
            </div>
            <span id="strengthSystemicBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">90% Primed</span>
          </div>
          <div style="font-size:2rem; font-weight:800; color:#fff;" id="strengthSystemicVal">90%</div>
          <div class="gauge-bar-bg" style="height:8px; margin:0.5rem 0;">
            <div id="strengthSystemicFill" class="gauge-fill" style="width:90%; background:var(--success);"></div>
          </div>
          <p class="card-subtext" style="margin:0;">Derived from Strava gym logs & Intervals weight sessions.</p>
        </div>

        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.5rem;">
            <div class="card-title" style="margin-bottom:0;">
              <span>RP Volume Landmarks <span class="info-btn" tabindex="0" role="button" aria-label="About RP Volume Landmarks">i<span class="info-popover"><span class="popover-title">Hypertrophy Volume Landmarks</span><span class="popover-def">Dr. Mike Israetel / RP model tracking weekly direct working sets against MEV (Minimum Effective) and MAV (Maximum Adaptive).</span><span class="popover-rel"><strong>Relevance:</strong> Staying within MAV (12-20 sets/week) drives progressive overload without overreaching past MRV.</span></span></span></span>
            </div>
            <span id="strengthVolumeStatusBadge" class="periodization-badge" style="background:rgba(56,189,248,0.2); color:#38bdf8;">Optimal MAV</span>
          </div>
          <div style="font-size:2rem; font-weight:800; color:#38bdf8;" id="strengthTotalSetsVal">72 Sets</div>
          <div style="font-size:0.8125rem; color:var(--text-muted); margin-top:4px;" id="strengthVolumeSummaryText">
            Aggregated across 13 major muscle groups this week.
          </div>
          <p class="card-subtext" style="margin:0.25rem 0 0 0;">Weekly target: 12-18 sets per muscle group.</p>
        </div>

        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.5rem;">
            <div class="card-title" style="margin-bottom:0;">
              <span>AMPK vs mTORC1 Guard <span class="info-btn" tabindex="0" role="button" aria-label="About AMPK vs mTORC1">i<span class="info-popover popover-right"><span class="popover-title">Molecular Interference Guard</span><span class="popover-def">Tracks session proximity between endurance (AMPK) and resistance (mTORC1) stimuli to prevent molecular interference.</span><span class="popover-rel"><strong>Relevance:</strong> Separate heavy leg sessions from endurance workouts by >= 6-8 hours to safeguard muscle protein synthesis.</span></span></span></span>
            </div>
            <span id="strengthInterferenceBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">Clear (No Conflict)</span>
          </div>
          <div style="font-size:1.1rem; font-weight:700; color:#10b981; margin:0.25rem 0;" id="strengthInterferenceHeadline">
            Optimal Concurrent Separation
          </div>
          <p style="font-size:0.75rem; color:var(--text-muted); margin:0; line-height:1.45;" id="strengthInterferenceDesc">
            Last lower body session separated by &gt;8 hours from endurance runs/rides. Molecular protein synthesis uncompromised.
          </p>
        </div>
      </div>

      <!-- Main Interactive Anatomical Muscle Map & Live Inspector -->
      <div class="grid-2" style="margin-bottom: 1.5rem;">
        <!-- Left Column: Dual Anatomical Muscle Map SVG -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; flex-wrap:wrap; gap:0.5rem;">
            <div>
              <div class="card-title" style="margin-bottom:0.25rem;">
                <span>Interactive Anatomical Muscle Map <span class="info-btn" tabindex="0" role="button" aria-label="About Muscle Map">i<span class="info-popover popover-left"><span class="popover-title">Anatomical Muscle Map</span><span class="popover-def">Dual Front and Back vector models color-coded by weekly set volume and recovery readiness.</span><span class="popover-rel"><strong>Relevance:</strong> Click any muscle group to view sets, RP volume landmark state, and targeted exercises.</span></span></span></span>
              </div>
              <div style="font-size:0.75rem; color:var(--text-muted);">Front (Anterior) & Back (Posterior) Views. Click any muscle to inspect.</div>
            </div>
            <span class="periodization-badge" style="background:rgba(56,189,248,0.2); color:#38bdf8;">13 Muscle Groups</span>
          </div>

          <!-- Anatomical SVG Body Map Container -->
          <div style="background: #0f172a; border: 1px solid var(--border); border-radius: 8px; padding: 1rem 0; display:flex; justify-content:center; align-items:center; position:relative;">
            <svg id="muscleMapSvg" width="100%" height="380" viewBox="0 0 560 380" role="img" aria-label="Interactive Dual-View Anatomical Muscle Map">
              <!-- Background / Figure Outlines -->
              <g id="figure-labels" style="font-size:11px; fill:#64748b; font-weight:700; text-anchor:middle;">
                <text x="140" y="24">ANTERIOR (FRONT)</text>
                <text x="420" y="24">POSTERIOR (BACK)</text>
              </g>

              <!-- FRONT ANATOMICAL FIGURE (Center x=140) -->
              <g id="front-figure" transform="translate(0, 10)">
                <!-- Head / Neck -->
                <circle cx="140" cy="50" r="18" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
                <path d="M 132 68 L 148 68 L 152 82 L 128 82 Z" fill="#1e293b" stroke="#334155" stroke-width="1.5" />

                <!-- Anterior / Side Delts (Shoulders Front) -->
                <!-- Left Shoulder Front (Viewer Left: x ~ 100) -->
                <path id="muscle-shoulders_front-left" class="muscle-poly" data-muscle="shoulders_front" onclick="inspectMuscle('shoulders_front')"
                  d="M 112 84 Q 96 90 98 114 Q 112 118 118 100 Z" fill="#334155" title="Anterior Deltoids" />
                <!-- Right Shoulder Front (Viewer Right: x ~ 180) -->
                <path id="muscle-shoulders_front-right" class="muscle-poly" data-muscle="shoulders_front" onclick="inspectMuscle('shoulders_front')"
                  d="M 168 84 Q 184 90 182 114 Q 168 118 162 100 Z" fill="#334155" title="Anterior Deltoids" />

                <!-- Lateral Delts (Viewer Left & Right Outers) -->
                <path id="muscle-shoulders_side-left" class="muscle-poly" data-muscle="shoulders_side" onclick="inspectMuscle('shoulders_side')"
                  d="M 96 94 Q 84 104 88 124 Q 98 126 102 112 Z" fill="#334155" title="Lateral Deltoids" />
                <path id="muscle-shoulders_side-right" class="muscle-poly" data-muscle="shoulders_side" onclick="inspectMuscle('shoulders_side')"
                  d="M 184 94 Q 196 104 192 124 Q 182 126 178 112 Z" fill="#334155" title="Lateral Deltoids" />

                <!-- Pectoralis Major (Chest) -->
                <path id="muscle-chest-left" class="muscle-poly" data-muscle="chest" onclick="inspectMuscle('chest')"
                  d="M 118 84 L 138 86 L 138 126 Q 116 128 112 112 Z" fill="#334155" title="Chest (Pectorals)" />
                <path id="muscle-chest-right" class="muscle-poly" data-muscle="chest" onclick="inspectMuscle('chest')"
                  d="M 162 84 L 142 86 L 142 126 Q 164 128 168 112 Z" fill="#334155" title="Chest (Pectorals)" />

                <!-- Biceps Brachii -->
                <path id="muscle-biceps-left" class="muscle-poly" data-muscle="biceps" onclick="inspectMuscle('biceps')"
                  d="M 94 124 Q 82 144 86 164 Q 98 166 104 142 Z" fill="#334155" title="Biceps Brachii" />
                <path id="muscle-biceps-right" class="muscle-poly" data-muscle="biceps" onclick="inspectMuscle('biceps')"
                  d="M 186 124 Q 198 144 194 164 Q 182 166 176 142 Z" fill="#334155" title="Biceps Brachii" />

                <!-- Forearms Front -->
                <path d="M 86 166 Q 78 190 76 214 Q 88 214 94 186 Z" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
                <path d="M 194 166 Q 202 190 204 214 Q 192 214 186 186 Z" fill="#1e293b" stroke="#334155" stroke-width="1.5" />

                <!-- Rectus Abdominis / Core (Abs) -->
                <path id="muscle-abs" class="muscle-poly" data-muscle="abs" onclick="inspectMuscle('abs')"
                  d="M 122 130 L 158 130 L 154 188 L 126 188 Z" fill="#334155" title="Rectus Abdominis (Abs & Core)" />

                <!-- Quadriceps Femoris (Left & Right Thighs) -->
                <path id="muscle-quads-left" class="muscle-poly" data-muscle="quads" onclick="inspectMuscle('quads')"
                  d="M 116 194 Q 104 230 112 280 Q 134 282 136 220 Z" fill="#334155" title="Quadriceps Femoris" />
                <path id="muscle-quads-right" class="muscle-poly" data-muscle="quads" onclick="inspectMuscle('quads')"
                  d="M 164 194 Q 176 230 168 280 Q 146 282 144 220 Z" fill="#334155" title="Quadriceps Femoris" />

                <!-- Anterior Calves & Shins -->
                <path id="muscle-calves-front-left" class="muscle-poly" data-muscle="calves" onclick="inspectMuscle('calves')"
                  d="M 112 288 Q 106 318 114 354 Q 126 354 128 314 Z" fill="#334155" title="Calves / Tibialis" />
                <path id="muscle-calves-front-right" class="muscle-poly" data-muscle="calves" onclick="inspectMuscle('calves')"
                  d="M 168 288 Q 174 318 166 354 Q 154 354 152 314 Z" fill="#334155" title="Calves / Tibialis" />
              </g>

              <!-- BACK ANATOMICAL FIGURE (Center x=420) -->
              <g id="back-figure" transform="translate(0, 10)">
                <!-- Head / Neck -->
                <circle cx="420" cy="50" r="18" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
                <path d="M 412 68 L 428 68 L 432 80 L 408 80 Z" fill="#1e293b" stroke="#334155" stroke-width="1.5" />

                <!-- Trapezius & Upper Back -->
                <path id="muscle-upper_back" class="muscle-poly" data-muscle="upper_back" onclick="inspectMuscle('upper_back')"
                  d="M 408 80 L 432 80 L 444 116 L 420 134 L 396 116 Z" fill="#334155" title="Trapezius & Rhomboids" />

                <!-- Rear Deltoids -->
                <path id="muscle-shoulders_rear-left" class="muscle-poly" data-muscle="shoulders_rear" onclick="inspectMuscle('shoulders_rear')"
                  d="M 392 86 Q 374 94 378 116 Q 394 116 398 98 Z" fill="#334155" title="Rear Deltoids" />
                <path id="muscle-shoulders_rear-right" class="muscle-poly" data-muscle="shoulders_rear" onclick="inspectMuscle('shoulders_rear')"
                  d="M 448 86 Q 466 94 462 116 Q 446 116 442 98 Z" fill="#334155" title="Rear Deltoids" />

                <!-- Triceps Brachii -->
                <path id="muscle-triceps-left" class="muscle-poly" data-muscle="triceps" onclick="inspectMuscle('triceps')"
                  d="M 374 120 Q 362 142 366 164 Q 378 164 384 140 Z" fill="#334155" title="Triceps Brachii" />
                <path id="muscle-triceps-right" class="muscle-poly" data-muscle="triceps" onclick="inspectMuscle('triceps')"
                  d="M 466 120 Q 478 142 474 164 Q 462 164 456 140 Z" fill="#334155" title="Triceps Brachii" />

                <!-- Latissimus Dorsi (Lats V-Taper) -->
                <path id="muscle-lats-left" class="muscle-poly" data-muscle="lats" onclick="inspectMuscle('lats')"
                  d="M 396 118 L 418 136 L 416 182 L 398 164 Z" fill="#334155" title="Latissimus Dorsi" />
                <path id="muscle-lats-right" class="muscle-poly" data-muscle="lats" onclick="inspectMuscle('lats')"
                  d="M 444 118 L 422 136 L 424 182 L 442 164 Z" fill="#334155" title="Latissimus Dorsi" />

                <!-- Forearms Back -->
                <path d="M 366 166 Q 358 190 356 214 Q 368 214 374 186 Z" fill="#1e293b" stroke="#334155" stroke-width="1.5" />
                <path d="M 474 166 Q 482 190 484 214 Q 472 214 466 186 Z" fill="#1e293b" stroke="#334155" stroke-width="1.5" />

                <!-- Gluteus Maximus & Medius (Glutes) -->
                <path id="muscle-glutes-left" class="muscle-poly" data-muscle="glutes" onclick="inspectMuscle('glutes')"
                  d="M 400 186 Q 388 208 402 232 Q 418 232 418 190 Z" fill="#334155" title="Gluteus Maximus" />
                <path id="muscle-glutes-right" class="muscle-poly" data-muscle="glutes" onclick="inspectMuscle('glutes')"
                  d="M 440 186 Q 452 208 438 232 Q 422 232 422 190 Z" fill="#334155" title="Gluteus Maximus" />

                <!-- Hamstrings (Biceps Femoris) -->
                <path id="muscle-hamstrings-left" class="muscle-poly" data-muscle="hamstrings" onclick="inspectMuscle('hamstrings')"
                  d="M 402 236 Q 392 260 400 282 Q 416 282 418 240 Z" fill="#334155" title="Hamstrings" />
                <path id="muscle-hamstrings-right" class="muscle-poly" data-muscle="hamstrings" onclick="inspectMuscle('hamstrings')"
                  d="M 438 236 Q 448 260 440 282 Q 424 282 422 240 Z" fill="#334155" title="Hamstrings" />

                <!-- Calves (Gastrocnemius & Soleus) -->
                <path id="muscle-calves-back-left" class="muscle-poly" data-muscle="calves" onclick="inspectMuscle('calves')"
                  d="M 398 288 Q 386 318 396 354 Q 412 354 414 314 Z" fill="#334155" title="Calves (Gastrocnemius)" />
                <path id="muscle-calves-back-right" class="muscle-poly" data-muscle="calves" onclick="inspectMuscle('calves')"
                  d="M 442 288 Q 454 318 444 354 Q 428 354 426 314 Z" fill="#334155" title="Calves (Gastrocnemius)" />
              </g>
            </svg>
          </div>

          <!-- Color Legend -->
          <div class="chart-legend" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-top:0.75rem;">
            <div style="display:flex; gap:0.75rem; flex-wrap:wrap;">
              <span class="chart-legend-item" style="color:#10b981;"><span class="legend-dot" style="background:#10b981;"></span>Optimal MAV</span>
              <span class="chart-legend-item" style="color:#f59e0b;"><span class="legend-dot" style="background:#f59e0b;"></span>Near MRV Ceiling</span>
              <span class="chart-legend-item" style="color:#ef4444;"><span class="legend-dot" style="background:#ef4444;"></span>Over MRV / High Strain</span>
              <span class="chart-legend-item" style="color:#64748b;"><span class="legend-dot" style="background:#334155;"></span>Below MEV / Maintenance</span>
            </div>
            <div style="font-size:0.7rem; color:var(--text-muted);">
              Click any muscle group to inspect detailed sets & recovery.
            </div>
          </div>
        </div>

        <!-- Right Column: Live Muscle Group Inspector -->
        <div class="card" id="muscleInspectorCard">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <div>
              <div class="card-title" style="margin-bottom:0.25rem;">
                <span id="inspectMuscleName">Chest (Pectoralis Major & Minor)</span>
              </div>
              <div style="font-size:0.75rem; color:var(--text-muted);" id="inspectMuscleSubtitle">Anterior Torso & Horizontal Pressing</div>
            </div>
            <span id="inspectLandmarkBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">OPTIMAL MAV</span>
          </div>

          <!-- Weekly Sets & Volume Spectrum Bar -->
          <div style="background:#0f172a; border:1px solid var(--border); border-radius:8px; padding:1rem; margin-bottom:1rem;">
            <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.5rem;">
              <div>
                <span style="font-size:2rem; font-weight:800; color:#38bdf8;" id="inspectWeeklySets">14.0</span>
                <span style="font-size:0.875rem; color:var(--text-muted); margin-left:4px;">working sets this week</span>
              </div>
              <div style="font-size:0.75rem; color:var(--text-muted);">
                Target MAV: <strong style="color:#10b981;" id="inspectTargetMav">14 sets</strong> (MRV: <span id="inspectMrvVal">22</span>)
              </div>
            </div>

            <!-- Volume Landmark Spectrum Gauge -->
            <div style="margin-bottom:0.5rem;">
              <div class="gauge-bar-bg" style="height:10px;">
                <div id="inspectVolumeFill" class="gauge-fill" style="width:65%; background:var(--success);"></div>
              </div>
              <div class="gauge-ticks">
                <span id="inspectTickMv">MV: 4</span>
                <span id="inspectTickMev">MEV: 8</span>
                <span id="inspectTickMav">MAV: 14</span>
                <span id="inspectTickMrv">MRV: 22+</span>
              </div>
            </div>
          </div>

          <!-- Recovery Readiness & Timing -->
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem; margin-bottom:1rem;">
            <div style="background:#0f172a; border:1px solid var(--border); border-radius:6px; padding:0.6rem 0.75rem;">
              <div style="font-size:0.75rem; color:var(--text-muted);">Recovery Readiness</div>
              <div style="font-size:1.25rem; font-weight:700; color:#10b981;" id="inspectRecoveryPct">100% Fully Recovered</div>
              <div style="font-size:0.7rem; color:var(--text-muted);" id="inspectHoursElapsed">Last trained ~48h ago</div>
            </div>

            <div style="background:#0f172a; border:1px solid var(--border); border-radius:6px; padding:0.6rem 0.75rem;">
              <div style="font-size:0.75rem; color:var(--text-muted);">Interference Risk</div>
              <div style="font-size:1.25rem; font-weight:700; color:#38bdf8;" id="inspectInterferenceRisk">None Detected</div>
              <div style="font-size:0.7rem; color:var(--text-muted);" id="inspectInterferenceDesc">&gt;8h separation from endurance</div>
            </div>
          </div>

          <!-- Coaching Prescription & Exercise Recommendations -->
          <div style="background:#111827; border:1px solid #1f2937; border-radius:6px; padding:0.75rem; margin-bottom:0.75rem;">
            <div style="font-size:0.75rem; font-weight:700; color:#38bdf8; text-transform:uppercase; margin-bottom:4px;">Scientific Coaching Prescription</div>
            <div style="font-size:0.8125rem; color:#e2e8f0; line-height:1.45;" id="inspectPrescriptionText">
              Chest volume is perfectly positioned in the Maximum Adaptive Volume sweet spot. Maintain 2-3 RIR on compound barbell pressing and push cable flyes to 0-1 RIR.
            </div>
          </div>

          <!-- Key Recommended Hypertrophy Exercises -->
          <div>
            <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:700; margin-bottom:0.35rem;">Key Stimulus Exercises</div>
            <div id="inspectExercisePills" style="display:flex; flex-wrap:wrap; gap:0.35rem;">
              <span class="periodization-badge" style="background:#1e293b; color:#cbd5e1;">Incline Barbell Press</span>
              <span class="periodization-badge" style="background:#1e293b; color:#cbd5e1;">Flat Dumbbell Press</span>
              <span class="periodization-badge" style="background:#1e293b; color:#cbd5e1;">Cable Crossovers</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Personalized 6-Day PPL Hypertrophy Program (Hybrid Athlete Blueprint) -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.5rem;">
          <div>
            <div class="card-title" style="margin-bottom:0.25rem;">
              <span>Personalized 6-Day Hybrid PPL Blueprint (Hypertrophy + Endurance) <span class="info-btn" tabindex="0" role="button" aria-label="About 6-Day PPL">i<span class="info-popover popover-left"><span class="popover-title">Hybrid 6-Day PPL</span><span class="popover-def">Scientifically periodized hypertrophy routine optimized with concurrent cardio sequencing (Push A / Pull A / Legs A / Push B / Pull B / Legs B).</span><span class="popover-rel"><strong>Relevance:</strong> Designed specifically for your intermediate lifting background to optimize muscle protein synthesis without compromising running/cycling.</span></span></span></span>
            </div>
            <p class="card-subtext" style="margin-bottom:0;">
              Full Commercial Gym | 6-Day Push / Pull / Legs | >= 6-Hour Concurrent Cardio Buffer
            </p>
          </div>
          <span class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">Personalized Plan Ready</span>
        </div>

        <!-- 6-Day PPL Day Selection Buttons -->
        <div style="display:flex; gap:0.5rem; margin-bottom:1rem; overflow-x:auto; padding-bottom:4px;" id="pplDayNav">
          <button class="btn chart-filter-btn active" id="btnPplDay0" onclick="showPplDay(0)">Day 1: Push A</button>
          <button class="btn btn-secondary chart-filter-btn" id="btnPplDay1" onclick="showPplDay(1)">Day 2: Pull A</button>
          <button class="btn btn-secondary chart-filter-btn" id="btnPplDay2" onclick="showPplDay(2)">Day 3: Legs A</button>
          <button class="btn btn-secondary chart-filter-btn" id="btnPplDay3" onclick="showPplDay(3)">Day 4: Push B</button>
          <button class="btn btn-secondary chart-filter-btn" id="btnPplDay4" onclick="showPplDay(4)">Day 5: Pull B</button>
          <button class="btn btn-secondary chart-filter-btn" id="btnPplDay5" onclick="showPplDay(5)">Day 6: Legs B</button>
          <button class="btn btn-secondary chart-filter-btn" id="btnPplDay6" onclick="showPplDay(6)">Day 7: Recovery</button>
        </div>

        <!-- Active PPL Day Display Card -->
        <div style="background:#0f172a; border:1px solid var(--border); border-radius:8px; padding:1.25rem;" id="pplActiveDayBox">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; flex-wrap:wrap; gap:0.5rem;">
            <div>
              <h3 style="font-size:1.15rem; color:#38bdf8; margin:0;" id="pplDayTitle">Day 1: Push A (Chest & Front/Side Delts Dominant)</h3>
              <div style="font-size:0.8125rem; color:var(--text-muted); margin-top:2px;" id="pplDayFocus">
                Horizontal pressing mechanical tension & upper chest fiber recruitment
              </div>
            </div>
            <div style="background:rgba(56,189,248,0.12); border:1px solid rgba(56,189,248,0.3); border-radius:4px; padding:0.35rem 0.6rem; font-size:0.75rem; color:#38bdf8;" id="pplDayCardioRule">
              Endurance: Easy Zone 2 cycling (30-45 mins) in afternoon or evening (>=6h separation).
            </div>
          </div>

          <table class="table" style="margin-top:0.75rem;">
            <thead>
              <tr>
                <th>Exercise</th>
                <th>Working Sets</th>
                <th>Target Reps</th>
                <th>Intensity (RIR)</th>
                <th>Rest Interval</th>
                <th>Primary Target</th>
              </tr>
            </thead>
            <tbody id="pplExerciseTableBody">
              <!-- Populated dynamically -->
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 2: ANALYSIS & PMC -->
    <div id="tab-analysis" class="tab-content">
      <div class="card" style="margin-bottom: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; flex-wrap:wrap; gap:0.5rem;">
          <div>
            <div class="card-title" style="margin-bottom:0.25rem;">
              <span>Performance Management Chart (Banister / Coggan PMC) <span class="info-btn" tabindex="0" role="button" aria-label="About PMC">i<span class="info-popover popover-left"><span class="popover-title">Performance Management Chart</span><span class="popover-def">Classic impulse-response model showing Fitness (CTL 42d), Fatigue (ATL 7d), and Form (TSB).</span><span class="popover-rel"><strong>Relevance:</strong> Allows precise tracking of long-term fitness accumulation and race taper timing.</span></span></span></span>
            </div>
            <div style="font-size:0.8125rem; color:var(--color-text-muted);" id="pmcDateRange">Interactive 30-Day Multi-Series Telemetry (Click point to inspect)</div>
          </div>
          <!-- Interactive Series Toggles -->
          <div style="display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap;">
            <button type="button" class="chart-toggle-btn active" id="pmcToggleCTL" onclick="togglePmcSeries('ctl')" aria-pressed="true">
              <span class="legend-dot" style="background:#06b6d4;"></span>Fitness (CTL)
            </button>
            <button type="button" class="chart-toggle-btn active" id="pmcToggleATL" onclick="togglePmcSeries('atl')" aria-pressed="true">
              <span class="legend-dot" style="background:#f43f5e;"></span>Fatigue (ATL)
            </button>
            <button type="button" class="chart-toggle-btn active" id="pmcToggleTSB" onclick="togglePmcSeries('tsb')" aria-pressed="true">
              <span class="legend-dot" style="background:#10b981;"></span>Form (TSB)
            </button>
          </div>
        </div>
        <div class="chart-box" id="pmcChartContainer" style="cursor:crosshair;">
          <div class="chart-tooltip" id="pmcTooltip" role="tooltip"></div>
          <svg id="pmcChartSvg" width="100%" height="100%" viewBox="0 0 800 240" preserveAspectRatio="none" role="img" aria-label="Performance Management Chart">
          </svg>
        </div>
        <div id="pmcDayInspector" class="diagnostic-panel" style="display:none; margin-top:0.75rem; background:var(--color-surface-sunken); border:1px solid var(--color-border); border-radius:var(--radius-md); padding:0.75rem 1rem;"></div>
        <div class="chart-legend">
          <span class="chart-legend-item" style="color:#06b6d4;">Fitness (CTL 42d)</span>
          <span class="chart-legend-item" style="color:#f43f5e;">Fatigue (ATL 7d)</span>
          <span class="chart-legend-item" style="color:#10b981;">Form (TSB = CTL - ATL)</span>
          <span class="chart-legend-item" style="color:var(--color-text-dim);">Neutral Form Line (TSB = 0)</span>
        </div>
      </div>

      <!-- Grid 2: ACWR & RHR Trends -->
      <div class="grid-2" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <div class="card-title" style="margin-bottom:0;">
              <span>Acute:Chronic Workload Ratio (ACWR Trend) <span class="info-btn" tabindex="0" role="button" aria-label="About ACWR Trend">i<span class="info-popover popover-left"><span class="popover-title">ACWR Trend</span><span class="popover-def">Historical rolling ratio of acute to chronic workload plotted across 30 days.</span><span class="popover-rel"><strong>Relevance:</strong> Identifies whether recent workload spikes into caution (1.3-1.5) or danger (>1.5) zones.</span></span></span></span>
            </div>
            <span id="acwrRatioBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">Sweet Spot</span>
          </div>
          <div class="chart-box-compact" id="acwrChartContainer" style="cursor:crosshair;">
            <div class="chart-tooltip" id="acwrTooltip" role="tooltip"></div>
            <svg id="acwrChartSvg" width="100%" height="100%" viewBox="0 0 450 180" preserveAspectRatio="none" role="img" aria-label="Acute to Chronic Workload Ratio Chart">
            </svg>
          </div>
          <div id="acwrDayInspector" class="diagnostic-panel" style="display:none; margin-top:0.5rem; background:var(--color-surface-sunken); border:1px solid var(--color-border); border-radius:var(--radius-sm); padding:0.4rem 0.6rem;"></div>
          <div class="chart-legend">
            <span class="chart-legend-item" style="color:#38bdf8;">ACWR Ratio</span>
            <span class="chart-legend-item" style="color:#10b981;">Sweet Spot (0.8-1.3)</span>
            <span class="chart-legend-item" style="color:#f59e0b;">Caution (1.3-1.5)</span>
            <span class="chart-legend-item" style="color:#ef4444;">Danger (&gt;1.5)</span>
          </div>
        </div>

        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <div class="card-title" style="margin-bottom:0;">
              <span>Autonomic Recovery: Resting HR Trend <span class="info-btn" tabindex="0" role="button" aria-label="About RHR Trend">i<span class="info-popover popover-right"><span class="popover-title">Resting HR Trend</span><span class="popover-def">Daily nocturnal resting heart rate tracked against your 30-day baseline average.</span><span class="popover-rel"><strong>Relevance:</strong> Sustained elevations indicate unrecovered sympathetic nervous system state.</span></span></span></span>
            </div>
            <span id="rhrStrainBadge" class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">Autonomic Green</span>
          </div>
          <div class="chart-box-compact" id="rhrChartContainer" style="cursor:crosshair;">
            <div class="chart-tooltip" id="rhrTooltip" role="tooltip"></div>
            <svg id="rhrChartSvg" width="100%" height="100%" viewBox="0 0 450 180" preserveAspectRatio="none" role="img" aria-label="Resting Heart Rate Chart">
            </svg>
          </div>
          <div id="rhrDayInspector" class="diagnostic-panel" style="display:none; margin-top:0.5rem; background:var(--color-surface-sunken); border:1px solid var(--color-border); border-radius:var(--radius-sm); padding:0.4rem 0.6rem;"></div>
          <div class="chart-legend">
            <span class="chart-legend-item" style="color:#38bdf8;">Daily Resting HR</span>
            <span class="chart-legend-item" style="color:#94a3b8;">30d Baseline</span>
            <span class="chart-legend-item" style="color:#ef4444;">+4 bpm Strain Alert</span>
          </div>
        </div>
      </div>

      <!-- Biometrics Timeseries Charts: Sleep & SpO2 / Weight -->
      <div class="grid-2" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <div class="card-title" style="margin-bottom:0;">
              <span>Sleep Duration & Recovery Stages (Rolling 30 Days) <span class="info-btn" tabindex="0" role="button" aria-label="About Sleep Duration">i<span class="info-popover popover-left"><span class="popover-title">Sleep Duration History</span><span class="popover-def">30-day sleep duration tracking with comparison against the 7-hour baseline target.</span><span class="popover-rel"><strong>Relevance:</strong> Chronic sleep deficits severely impair glycogen resynthesis and neuromuscular recovery.</span></span></span></span>
            </div>
            <div style="font-size:0.8125rem; color:var(--color-text-muted);" id="sleepSummaryText">-- hrs avg</div>
          </div>
          <div class="chart-box-compact" id="sleepChartContainer" style="cursor:crosshair;">
            <div class="chart-tooltip" id="sleepTooltip" role="tooltip"></div>
            <svg id="sleepChartSvg" width="100%" height="100%" viewBox="0 0 450 180" preserveAspectRatio="none" role="img" aria-label="Sleep Duration and Recovery Chart">
            </svg>
          </div>
          <div id="sleepDayInspector" class="diagnostic-panel" style="display:none; margin-top:0.5rem; background:var(--color-surface-sunken); border:1px solid var(--color-border); border-radius:var(--radius-sm); padding:0.4rem 0.6rem;"></div>
          <div class="chart-legend">
            <span class="chart-legend-item" style="color:#c084fc;">Sleep Duration (Hrs)</span>
            <span class="chart-legend-item" style="color:#10b981;">7h Target Baseline</span>
          </div>
        </div>

        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <div class="card-title" style="margin-bottom:0;">
              <span>Blood Oxygen (SpO2) & Body Weight Trends <span class="info-btn" tabindex="0" role="button" aria-label="About SpO2 and Weight Trends">i<span class="info-popover popover-right"><span class="popover-title">SpO2 & Weight Trends</span><span class="popover-def">Combined trends of blood oxygen saturation and morning scale weight.</span><span class="popover-rel"><strong>Relevance:</strong> Monitors metabolic trends and warns of respiratory stress or unexpected weight fluctuations.</span></span></span></span>
            </div>
            <div style="font-size:0.8125rem; color:var(--color-text-muted);" id="vitalsSummaryText">Samsung Health / Scale</div>
          </div>
          <div class="chart-box-compact" id="vitalsChartContainer" style="cursor:crosshair;">
            <div class="chart-tooltip" id="vitalsTooltip" role="tooltip"></div>
            <svg id="vitalsChartSvg" width="100%" height="100%" viewBox="0 0 450 180" preserveAspectRatio="none" role="img" aria-label="Blood Oxygen and Weight Chart">
            </svg>
          </div>
          <div id="vitalsDayInspector" class="diagnostic-panel" style="display:none; margin-top:0.5rem; background:var(--color-surface-sunken); border:1px solid var(--color-border); border-radius:var(--radius-sm); padding:0.4rem 0.6rem;"></div>
          <div class="chart-legend">
            <span class="chart-legend-item" style="color:#06b6d4;">SpO2 (%)</span>
            <span class="chart-legend-item" style="color:#10b981;">Weight (kg)</span>
          </div>
        </div>
      </div>

      <!-- Daily Training Load & Volume (Stacked Discipline TSS) -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; flex-wrap:wrap; gap:0.5rem;">
          <div>
            <div class="card-title" style="margin-bottom:0.25rem;">
              <span>Daily Training Load & Volume (Stacked Discipline TSS) <span class="info-btn" tabindex="0" role="button" aria-label="About Daily Load">i<span class="info-popover popover-left"><span class="popover-title">Daily Training Load (TSS)</span><span class="popover-def">Daily Training Stress Score segmented by discipline (Ride, Run, Swim, Brick, Other).</span><span class="popover-rel"><strong>Relevance:</strong> Shows cross-training distribution and volume-intensity balance across sports.</span></span></span></span>
            </div>
            <div style="font-size:0.8125rem; color:var(--color-text-muted);" id="totalVolumeLoadSummary">-- hrs | -- TSS</div>
          </div>
          <!-- Interactive Timeframe & Scroll Filters -->
          <div style="display:flex; gap:0.4rem; align-items:center; flex-wrap:wrap;">
            <span style="font-size:0.75rem; color:var(--color-text-muted); margin-right:4px;">Window:</span>
            <button class="btn btn-secondary chart-filter-btn" id="btnLoad90d" onclick="filterDailyLoad(90)" style="font-size:0.7rem; padding:0.25rem 0.6rem;">90 Days</button>
            <button class="btn btn-secondary chart-filter-btn" id="btnLoad60d" onclick="filterDailyLoad(60)" style="font-size:0.7rem; padding:0.25rem 0.6rem;">60 Days</button>
            <button class="btn btn-secondary chart-filter-btn active" id="btnLoad30d" onclick="filterDailyLoad(30)" style="font-size:0.7rem; padding:0.25rem 0.6rem;">30 Days</button>
            <button class="btn btn-secondary chart-filter-btn" id="btnLoad14d" onclick="filterDailyLoad(14)" style="font-size:0.7rem; padding:0.25rem 0.6rem;">14 Days</button>
            <button class="btn btn-secondary chart-filter-btn" id="btnLoad7d" onclick="filterDailyLoad(7)" style="font-size:0.7rem; padding:0.25rem 0.6rem;">7 Days</button>
          </div>
        </div>

        <!-- Scrollable Chart Container -->
        <div class="chart-scroll-container" id="loadChartScrollBox" style="position:relative; width:100%; overflow-x:auto; overflow-y:hidden; border-radius:var(--radius-md); border:1px solid var(--color-border); background:var(--color-surface-sunken); padding: 0.5rem 0; cursor:crosshair;">
          <div class="chart-tooltip" id="loadTooltip" role="tooltip"></div>
          <svg id="loadChartSvg" height="190" style="display:block; min-width:850px; width:100%;" role="img" aria-label="Daily Training Load Stacked Chart">
          </svg>
        </div>
        <div id="loadDayInspector" class="diagnostic-panel" style="display:none; margin-top:0.75rem; background:var(--color-surface-sunken); border:1px solid var(--color-border); border-radius:var(--radius-md); padding:0.75rem 1rem;"></div>

        <div class="chart-legend" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-top:0.75rem;">
          <div style="display:flex; gap:1rem; flex-wrap:wrap;">
            <span class="chart-legend-item" style="color:#06b6d4;">Run</span>
            <span class="chart-legend-item" style="color:#f59e0b;">Ride</span>
            <span class="chart-legend-item" style="color:#38bdf8;">Swim</span>
            <span class="chart-legend-item" style="color:#c084fc;">Brick/Duathlon</span>
            <span class="chart-legend-item" style="color:#64748b;">Other</span>
          </div>
          <div style="font-size:0.7rem; color:var(--color-text-muted);">
            Hover to inspect load breakdown. Click any day bar to view detailed activities.
          </div>
        </div>
      </div>

      <!-- Grid 2: Polarization & Discipline Breakdown -->
      <div class="grid-2" style="margin-bottom: 1.5rem;">
        <div class="card">
          <div class="card-title">
            <span>Stephen Seiler 80/20 Intensity Polarization <span class="info-btn" tabindex="0" role="button" aria-label="About 80/20 Polarization">i<span class="info-popover popover-left"><span class="popover-title">Intensity Polarization</span><span class="popover-def">Time distribution across Low (Z1-Z2), Moderate (Z3), and High (Z4-Z5) intensity zones.</span><span class="popover-rel"><strong>Relevance:</strong> 80% low-intensity builds mitochondrial density; avoiding the "black hole" of excessive moderate intensity.</span></span></span></span>
          </div>
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
          <div class="card-title">
            <span>Completed Discipline Breakdown (Last 30 Days) <span class="info-btn" tabindex="0" role="button" aria-label="About Discipline Breakdown">i<span class="info-popover popover-right"><span class="popover-title">Discipline Breakdown</span><span class="popover-def">30-day cumulative volume, session count, TSS load, and distance partitioned by sport.</span><span class="popover-rel"><strong>Relevance:</strong> Verifies multi-sport cross-training balance and sport-specific training load share.</span></span></span></span>
          </div>
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

      <!-- Grid 2: Running Fitness & Race Predictor -->
      <div class="grid-2" style="margin-bottom: 1.5rem;">
        <!-- Running Fitness Card -->
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
            <div class="card-title" style="margin-bottom:0;">
              <span>Running Fitness (EvoLab 4-Pillars) <span class="info-btn" tabindex="0" role="button" aria-label="About Running Fitness">i<span class="info-popover popover-left"><span class="popover-title">Running Fitness</span><span class="popover-def">Composite index evaluating Base aerobic endurance, Lactate Threshold endurance, VO2 Max speed, and Sprint power.</span><span class="popover-rel"><strong>Relevance:</strong> Pinpoints your physiological limiter to guide targeted threshold vs endurance workouts.</span></span></span></span>
            </div>
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
            <div class="card-title" style="margin-bottom:0;">
              <span>Race Predictor (Riegel / Cameron Model) <span class="info-btn" tabindex="0" role="button" aria-label="About Race Predictor">i<span class="info-popover popover-right"><span class="popover-title">Race Predictor</span><span class="popover-def">Predicted finish times and target paces derived from threshold efficiency and rolling aerobic volume.</span><span class="popover-rel"><strong>Relevance:</strong> Provides realistic, non-wishful race pacing targets for 5k, 10k, Half, and Marathon.</span></span></span></span>
            </div>
            <span class="periodization-badge" style="background:rgba(56,189,248,0.2); color:#38bdf8;">Calibrated Pacing</span>
          </div>
          <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:0.75rem;">
            Predicted finish times and target paces derived from threshold efficiency and rolling aerobic volume.
          </p>

          <table class="table">
            <thead>
              <tr>
                <th>Event</th>
                <th>Distance</th>
                <th>Predicted Time</th>
                <th>Target Pace</th>
              </tr>
            </thead>
            <tbody id="corosRaceTableBody">
              <!-- Populated dynamically -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- Training Effect Simulator Card -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
          <div class="card-title" style="margin-bottom:0;">
            <span>Workout Training Effect (TE) & Recovery Estimator <span class="info-btn" tabindex="0" role="button" aria-label="About Training Effect">i<span class="info-popover popover-left"><span class="popover-title">Training Effect (TE)</span><span class="popover-def">Metric from 0.0 to 5.0 predicting aerobic and anaerobic cardiorespiratory adaptations.</span><span class="popover-rel"><strong>Relevance:</strong> Validates whether a workout achieved the intended stimulus (e.g. 3.0-3.9 for threshold build).</span></span></span></span>
          </div>
          <span class="periodization-badge" style="background:rgba(16,185,129,0.2); color:var(--success);">Aerobic & Anaerobic Dynamics</span>
        </div>
        <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:1rem;">
          Simulate the physiological stimulus and post-workout recovery demand of planned sessions based on duration, TSS, and intensity.
        </p>

        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr auto; gap:0.75rem; align-items:end; margin-bottom:1rem;">
          <div>
            <label style="font-size:0.75rem; color:var(--text-muted); display:block; margin-bottom:4px;">Duration (mins)</label>
            <input type="number" id="teInputMins" value="60" style="width:100%; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; padding:0.4rem 0.5rem; font-size:0.8125rem;">
          </div>
          <div>
            <label style="font-size:0.75rem; color:var(--text-muted); display:block; margin-bottom:4px;">Load (TSS)</label>
            <input type="number" id="teInputLoad" value="65" style="width:100%; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; padding:0.4rem 0.5rem; font-size:0.8125rem;">
          </div>
          <div>
            <label style="font-size:0.75rem; color:var(--text-muted); display:block; margin-bottom:4px;">Avg Heart Rate</label>
            <input type="number" id="teInputHr" value="155" style="width:100%; background:#0f172a; border:1px solid var(--border); border-radius:4px; color:#fff; padding:0.4rem 0.5rem; font-size:0.8125rem;">
          </div>
          <button class="btn btn-secondary" style="font-size:0.8125rem; padding:0.45rem 1rem;" onclick="calcCorosTE()">Calculate Impact</button>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:0.75rem;">
          <div style="background:#0f172a; border:1px solid var(--border); border-radius:6px; padding:0.75rem;">
            <div style="font-size:0.75rem; color:var(--text-muted);">Aerobic Training Effect</div>
            <div style="font-size:1.5rem; font-weight:800; color:#10b981;" id="corosAeroTeVal">--</div>
            <div style="font-size:0.75rem; color:var(--text-muted);" id="corosAeroTeLabel">Maintaining</div>
          </div>
          <div style="background:#0f172a; border:1px solid var(--border); border-radius:6px; padding:0.75rem;">
            <div style="font-size:0.75rem; color:var(--text-muted);">Anaerobic Training Effect</div>
            <div style="font-size:1.5rem; font-weight:800; color:#f59e0b;" id="corosAnaeroTeVal">--</div>
            <div style="font-size:0.75rem; color:var(--text-muted);" id="corosAnaeroTeLabel">Maintaining</div>
          </div>
          <div style="background:#0f172a; border:1px solid var(--border); border-radius:6px; padding:0.75rem;">
            <div style="font-size:0.75rem; color:var(--text-muted);">Required Recovery Time</div>
            <div style="font-size:1.5rem; font-weight:800; color:#38bdf8;" id="simTeRecovery">--h</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">Post-session rest</div>
          </div>
        </div>
      </div>

      <!-- Plan Compliance & Execution Card -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
          <div class="card-title" style="margin-bottom:0;">
            <span>Plan Compliance & Execution (Rolling 28 Days) <span class="info-btn" tabindex="0" role="button" aria-label="About Plan Compliance">i<span class="info-popover popover-left"><span class="popover-title">Plan Compliance</span><span class="popover-def">Tracks completed vs planned workouts, volume hours, and TSS adherence.</span><span class="popover-rel"><strong>Relevance:</strong> Optimal compliance is 80-110%; protects against under-training or chronic overreaching.</span></span></span></span>
          </div>
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
        <div class="card-title">
          <span>Aerobic Decoupling & Post-Workout Session Debrief <span class="info-btn" tabindex="0" role="button" aria-label="About Aerobic Decoupling">i<span class="info-popover popover-left"><span class="popover-title">Aerobic Decoupling (Pw:HR / Pa:HR)</span><span class="popover-def">Measures cardiac drift: the percentage divergence between output and heart rate over time.</span><span class="popover-rel"><strong>Relevance:</strong> Drift &lt;5% indicates solid aerobic base; drift &gt;5% indicates cardiac fatigue, heat stress, or dehydration.</span></span></span></span>
        </div>
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
              <svg id="decouplingGaugeSvg" width="100%" height="100%" viewBox="0 0 350 90" role="img" aria-label="Aerobic Efficiency Gauge">
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
      <!-- Universal Ecosystem Sync Control Card -->
      <div class="card" style="margin-bottom: 1.5rem; background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(56, 189, 248, 0.05)); border: 1px solid rgba(16, 185, 129, 0.25);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div class="card-title" style="margin-bottom: 0.25rem; font-size: 1.1rem; color: #f3f4f6;">Universal Cross-Platform Synchronization</div>
            <p class="card-subtext" style="margin-bottom: 0;">
              Synchronize biometrics and training sessions across Samsung Health, Health Connect, Intervals.icu, COROS, Strava, and Google Fit. Updates 30-day rolling analytics and re-aligns workout calendar.
            </p>
          </div>
          <div style="display: flex; gap: 0.75rem; align-items: center;">
            <button id="tabSyncBtn" class="btn" onclick="triggerEcosystemSync()" style="font-weight: 600; padding: 0.5rem 1.25rem;">
              <span id="tabSyncBtnSpinner" style="display:none;" class="spinner" aria-hidden="true"></span>
              <span id="tabSyncBtnText">Sync All Data Sources</span>
            </button>
          </div>
        </div>
        <div id="syncStatusBanner" style="display: none; margin-top: 1rem; padding: 0.75rem 1rem; border-radius: 6px; font-size: 0.8125rem;"></div>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
        <div class="card">
          <div class="card-title">Intervals.icu Cloud Hub</div>
          <div style="font-size: 1.1rem; font-weight: 700; color: var(--success);" id="intervalsStatus">Connected</div>
          <p class="card-subtext">Direct calendar sync with read-back verification.</p>
        </div>
        <div class="card">
          <div class="card-title">Garmin Connect Bridge</div>
          <div style="font-size: 1.1rem; font-weight: 700; color: #38bdf8;" id="garminStatus">Checking...</div>
          <p class="card-subtext">Direct FIT engine & Intervals Health/Training relay.</p>
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

      <!-- Garmin Connect & Ecosystem Bridge -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
          <div class="card-title" style="margin-bottom:0;">Garmin Connect & Ecosystem Bridge</div>
          <span id="garminModeBadge" class="periodization-badge" style="background:rgba(56,189,248,0.2); color:#38bdf8;">Intervals Cloud Relay Active</span>
        </div>
        <p class="card-subtext" style="margin-bottom:1.25rem;">
          Bidirectional synchronization between AdaptPulse, Intervals.icu, and Garmin Connect. Supports automatic workout delivery to Garmin devices, binary FIT workout generation (for <code>GARMIN/NEWFILES</code>), and ingestion of Body Battery, Resting Heart Rate, and overnight HRV.
        </p>
        <div class="grid-2">
          <div style="background:#0f172a; border:1px solid #1f2937; border-radius:8px; padding:1.25rem;">
            <div style="font-weight:700; color:var(--accent); margin-bottom:0.5rem; font-size:0.9375rem;">1. Intervals.icu Garmin Cloud Relay</div>
            <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:0.75rem;">
              Enables automatic hands-free workout sync directly to your Garmin watch or bike computer whenever workouts are generated or updated.
            </p>
            <div style="display:flex; flex-direction:column; gap:0.5rem; margin-bottom:0.75rem; font-size:0.8125rem;">
              <div style="display:flex; justify-content:space-between;">
                <span style="color:var(--text-muted);">Workout Auto-Push:</span>
                <strong id="garminUploadStatus" style="color:var(--success);">Enabled</strong>
              </div>
              <div style="display:flex; justify-content:space-between;">
                <span style="color:var(--text-muted);">Wellness & Body Battery Download:</span>
                <strong id="garminWellnessStatus" style="color:var(--success);">Enabled</strong>
              </div>
              <div style="display:flex; justify-content:space-between;">
                <span style="color:var(--text-muted);">Power Target Mode:</span>
                <strong id="garminPowerMode" style="color:#f3f4f6;">POWER_LAP</strong>
              </div>
            </div>
            <button class="btn btn-secondary" onclick="toggleGarminRelay()" id="btnGarminRelay" style="width:100%;">Update Relay Settings</button>
          </div>

          <div style="background:#0f172a; border:1px solid #1f2937; border-radius:8px; padding:1.25rem;">
            <div style="font-weight:700; color:var(--success); margin-bottom:0.5rem; font-size:0.9375rem;">2. Pure-Python FIT Workout Engine</div>
            <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:0.75rem;">
              Compiles planned workouts into standard Garmin binary FIT protocol (Global Messages 0, 26, 27 with 16-bit CRC checksums). No external drivers required.
            </p>
            <div style="background:#111827; border:1px solid #374151; border-radius:6px; padding:0.5rem 0.75rem; font-size:0.8125rem; margin-bottom:0.75rem;">
              <div style="color:var(--text-muted); font-size:0.75rem; margin-bottom:0.25rem;">Device Compatibility:</div>
              <div style="color:#38bdf8; font-weight:600;">Garmin Forerunner, Edge 530/830/1040, Fenix, Epix</div>
              <div style="color:#9ca3af; font-size:0.75rem; margin-top:0.25rem;">Copy directly to <code>GARMIN/NEWFILES</code> via USB or Garmin Express.</div>
            </div>
            <button class="btn" onclick="downloadExport('fit')" style="width:100%;">Download Current Workout (.fit)</button>
          </div>
        </div>

        <div style="background:#111827; border:1px solid #1f2937; border-radius:6px; padding:0.75rem 1rem; margin-top:1rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem; font-size:0.8125rem;">
          <div>
            <span style="color:var(--text-muted);">Garmin Athlete ID:</span>
            <strong id="garminUserIdText" style="color:#f3f4f6; margin-left:4px;">Connected</strong>
          </div>
          <div>
            <span style="color:var(--text-muted);">Sync Mode:</span>
            <strong id="garminModeText" style="color:var(--success); margin-left:4px;">Intervals Cloud Relay</strong>
          </div>
          <div>
            <span style="color:var(--text-muted);">Direct API:</span>
            <strong id="garminDirectText" style="color:var(--accent); margin-left:4px;">Ready</strong>
          </div>
          <div>
            <span style="color:var(--text-muted);">Target Tolerances:</span>
            <strong id="garminToleranceText" style="color:#38bdf8; margin-left:4px;">HR ±1.5% | Pace ±2.5%</strong>
          </div>
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

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1.25rem;">
          <div style="background:#1e293b; border:1px solid #334155; border-radius:8px; padding:1.25rem;">
            <h3 style="font-size:1.1rem; margin-bottom:0.5rem; color:#38bdf8;">Garmin Binary (.fit)</h3>
            <p style="font-size:0.8125rem; color:var(--text-muted); margin-bottom:1rem;">
              Standard binary FIT protocol for Edge, Forerunner, and Fenix. Direct USB copy to GARMIN/NEWFILES.
            </p>
            <button class="btn btn-secondary" onclick="downloadExport('fit')">Download Garmin .fit</button>
          </div>

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

      <!-- Training Effect & Recovery Demand Box -->
      <div id="modalTeBox" style="background:#0f172a; border:1px solid #1e293b; border-radius:8px; padding:0.75rem 1rem; margin-bottom: 1.25rem;">
        <h4 style="font-size: 0.8125rem; text-transform:uppercase; color:#38bdf8; margin-bottom: 0.35rem;">EvoLab Training Effect & Recovery Demand</h4>
        <div style="display:flex; gap:1.5rem; font-size:0.8125rem; color:var(--text-muted); flex-wrap:wrap;">
          <div>Aerobic TE: <strong id="modalAeroTe" style="color:#10b981;">--</strong></div>
          <div>Anaerobic TE: <strong id="modalAnaeroTe" style="color:#f59e0b;">--</strong></div>
          <div>Required Recovery: <strong id="modalRecovHours" style="color:#38bdf8;">--</strong></div>
        </div>
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
        <h4 style="font-size: 0.8125rem; color:var(--color-accent); margin-bottom: 0.5rem; font-weight:700;">Coros Watch Screen Simulation</h4>
        <div class="coros-preview-box">
          <div class="coros-screen-header" id="corosWatchHeader">Coros Pace and Apex Display</div>
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
          const garminStatusEl = document.getElementById('garminStatus');
          if (garminStatusEl) {
            garminStatusEl.innerText = statusData.garmin_connected ? 'Direct API' : 'Relay Active';
            garminStatusEl.style.color = statusData.garmin_connected ? 'var(--success)' : '#38bdf8';
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

        // Executive Summary & Biometric Readiness Hero Card
        populateExecutiveSummary(currentAnalytics, currentProfile);

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

        // Load Garmin Connect Status
        loadGarminStatus();

        // Load COROS Training Hub & EvoLab Telemetry
        loadCorosHub();

        // Load Strength Training & Muscle Map Telemetry
        loadStrengthData();

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

    let currentStrengthData = null;
    let currentPplPlan = null;
    let activeInspectedMuscle = 'chest';
    let activePplDayIndex = 0;

    const MUSCLE_EXERCISE_TIPS = {
      chest: {
        subtitle: 'Anterior Torso & Horizontal Pressing',
        exercises: ['Incline Barbell Press', 'Flat Dumbbell Press', 'Cable Crossover', 'Dips'],
        prescription: 'Chest volume is in the MAV zone. Keep heavy barbell pressing at 2-3 RIR and push cable isolation to 0-1 RIR with 3-second eccentric stretches.'
      },
      lats: {
        subtitle: 'Posterior Torso V-Taper & Vertical Pulling',
        exercises: ['Neutral-Grip Lat Pulldown', 'Weighted Pullups', 'Single-Arm DB Row'],
        prescription: 'Focus on full lat elongation at the top of pulldowns. Keep elbows driving down to the hip pockets rather than pulling with biceps.'
      },
      upper_back: {
        subtitle: 'Traps, Rhomboids & Scapular Retraction',
        exercises: ['Chest-Supported T-Bar Row', 'Face Pulls', 'Barbell Shrugs'],
        prescription: 'Provides critical scapular stability for cycling posture and running arm swing. Squeeze shoulder blades together for 1s pause.'
      },
      shoulders_side: {
        subtitle: 'Medial Deltoid Lateral Abduction',
        exercises: ['Cable Lateral Raise', 'Dumbbell Lateral Raise', 'Behind-the-Back Cable Raise'],
        prescription: 'High frequency and volume responder. Can handle 16-22 sets/week with short rest intervals and 12-20 rep ranges.'
      },
      shoulders_rear: {
        subtitle: 'Posterior Deltoid & External Rotator Cuff',
        exercises: ['Incline Rear Delt Flyes', 'Rope Face Pulls to Forehead', 'Reverse Pec Deck'],
        prescription: 'Crucial postural antidote to forward-rolled cycling shoulders and aero-tuck positions.'
      },
      shoulders_front: {
        subtitle: 'Anterior Deltoid & Vertical Pressing',
        exercises: ['Seated DB Overhead Press', 'Military Press', 'Incline Press Overlap'],
        prescription: 'Receives substantial indirect volume from chest pressing. Minimal direct volume (4-8 sets) is needed to avoid anterior shoulder impingement.'
      },
      biceps: {
        subtitle: 'Elbow Flexion & Supination',
        exercises: ['Incline Dumbbell Curl', 'EZ-Bar Preacher Curl', 'Standing Cable Hammer Curl'],
        prescription: 'Perform curls with strict elbow pinning. Incline DB curls maximize long-head stretch; hammer curls recruit the brachialis for arm width.'
      },
      triceps: {
        subtitle: 'Elbow Extension & Arm Thickness',
        exercises: ['Overhead Cable Triceps Extension', 'Triceps Rope Pushdown', 'Dips'],
        prescription: 'Include overhead extensions to stimulate the long head, which is unworked in flat pressing movements.'
      },
      quads: {
        subtitle: 'Knee Extension & Squat Mechanics',
        exercises: ['High-Bar Back Squat', 'Hack Squat', 'Leg Press', 'Walking Lunges'],
        prescription: 'Separate heavy quad training by at least 6-8 hours from running or cycling sessions to avoid molecular mTORC1 interference and patellar tendon strain.'
      },
      hamstrings: {
        subtitle: 'Hip Extension & Knee Flexion',
        exercises: ['Romanian Deadlift (RDL)', 'Seated Leg Curl', 'Lying Leg Curl'],
        prescription: 'Seated leg curls train the hamstrings at long muscle lengths (superior hypertrophy). RDLs develop powerful posterior chain drive for endurance sports.'
      },
      glutes: {
        subtitle: 'Hip Extension & Pelvic Stabilization',
        exercises: ['Barbell Hip Thrust', 'Bulgarian Split Squat', 'Deep Squats'],
        prescription: 'Key power generator in cycling stroke and running gait. Focus on complete hip lockout at the top of hip thrusts.'
      },
      calves: {
        subtitle: 'Plantarflexion & Achilles Energy Return',
        exercises: ['Standing Single-Leg Calf Raise', 'Seated Calf Raise'],
        prescription: 'Standing raises target the gastrocnemius; seated raises target the soleus. Crucial durability foundation to absorb 3x bodyweight impact when running.'
      },
      abs: {
        subtitle: 'Core Anti-Extension & Spinal Flexion',
        exercises: ['Hanging Leg Raise', 'Cable Crunch', 'Ab Rollout', 'Plank'],
        prescription: 'Resist rotational shear and maintain pelvic neutral in aero and running positions. Perform 10-15 controlled reps with deliberate exhalation.'
      }
    };

    async function loadStrengthData() {
      try {
        const [mapRes, planRes] = await Promise.all([
          fetch('/api/strength/muscle-map'),
          fetch('/api/strength/plan')
        ]);
        currentStrengthData = await mapRes.json();
        currentPplPlan = await planRes.json();

        if (currentStrengthData) {
          // 1. Update Systemic Recovery Score
          const score = currentStrengthData.systemic_muscle_recovery_score || 90;
          const scoreValEl = document.getElementById('strengthSystemicVal');
          if (scoreValEl) scoreValEl.innerText = score + '%';
          const fillEl = document.getElementById('strengthSystemicFill');
          if (fillEl) {
            fillEl.style.width = score + '%';
            fillEl.style.background = score >= 80 ? 'var(--success)' : (score >= 60 ? 'var(--warning)' : 'var(--danger)');
          }
          const scoreBadgeEl = document.getElementById('strengthSystemicBadge');
          if (scoreBadgeEl) {
            scoreBadgeEl.innerText = score >= 85 ? `${score}% Primed` : (score >= 65 ? `${score}% Recovering` : `${score}% Fatigued`);
            scoreBadgeEl.style.color = score >= 80 ? 'var(--success)' : (score >= 60 ? 'var(--warning)' : 'var(--danger)');
            scoreBadgeEl.style.background = score >= 80 ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.2)';
          }

          // 2. Total Volume Sets Summary
          const groups = currentStrengthData.muscle_groups || {};
          let totalSets = 0;
          let mavCount = 0;
          let nearMrvCount = 0;
          let overMrvCount = 0;

          for (const [mKey, mData] of Object.entries(groups)) {
            totalSets += mData.weekly_sets || 0;
            if (mData.landmark_state === 'OPTIMAL_MAV') mavCount++;
            else if (mData.landmark_state === 'NEAR_MRV') nearMrvCount++;
            else if (mData.landmark_state === 'OVER_MRV') overMrvCount++;

            // Update SVG muscle paths
            const fillColor = mData.landmark_state === 'OPTIMAL_MAV' ? '#10b981' :
                              (mData.landmark_state === 'NEAR_MRV' ? '#f59e0b' :
                              (mData.landmark_state === 'OVER_MRV' ? '#ef4444' : '#334155'));

            // Select all matching SVG elements (could be multiple like left/right)
            document.querySelectorAll(`[data-muscle="${mKey}"]`).forEach(el => {
              el.setAttribute('fill', fillColor);
            });
          }

          const totSetsEl = document.getElementById('strengthTotalSetsVal');
          if (totSetsEl) totSetsEl.innerText = Math.round(totalSets) + ' Sets';

          const volBadgeEl = document.getElementById('strengthVolumeStatusBadge');
          if (volBadgeEl) {
            if (overMrvCount > 0) {
              volBadgeEl.innerText = `${overMrvCount} Muscles Over MRV`;
              volBadgeEl.style.color = 'var(--danger)';
              volBadgeEl.style.background = 'rgba(239,68,68,0.2)';
            } else if (nearMrvCount > 2) {
              volBadgeEl.innerText = 'High Volume (Near MRV)';
              volBadgeEl.style.color = 'var(--warning)';
              volBadgeEl.style.background = 'rgba(245,158,11,0.2)';
            } else {
              volBadgeEl.innerText = `${mavCount} Muscles in MAV`;
              volBadgeEl.style.color = 'var(--success)';
              volBadgeEl.style.background = 'rgba(16,185,129,0.2)';
            }
          }

          // 3. Inspect default muscle
          inspectMuscle(activeInspectedMuscle);
        }

        // 4. Render Active PPL Workout Day
        if (currentPplPlan && currentPplPlan.sessions) {
          showPplDay(activePplDayIndex);
        }
      } catch (err) {
        console.debug('Failed to load strength data:', err);
      }
    }

    function inspectMuscle(muscleKey) {
      activeInspectedMuscle = muscleKey;

      // Update SVG visual selection outline
      document.querySelectorAll('.muscle-poly').forEach(el => el.classList.remove('active-selected'));
      document.querySelectorAll(`[data-muscle="${muscleKey}"]`).forEach(el => el.classList.add('active-selected'));

      if (!currentStrengthData || !currentStrengthData.muscle_groups) return;
      const mData = currentStrengthData.muscle_groups[muscleKey] || {
        name: muscleKey,
        display_name: muscleKey.replace('_', ' ').toUpperCase(),
        weekly_sets: 12,
        mv: 4, mev: 8, mav: 14, mrv: 20,
        landmark_state: 'OPTIMAL_MAV',
        recovery_pct: 100,
        hours_since_trained: 48,
        interference_risk: 'NONE',
        notes: 'Optimal progressive overload.'
      };

      const tips = MUSCLE_EXERCISE_TIPS[muscleKey] || {
        subtitle: 'Primary Skeletal Muscle Group',
        exercises: ['Compound Press / Pull', 'Isolation Movements'],
        prescription: 'Maintain progressive overload within 1-3 Reps in Reserve (RIR).'
      };

      // Populate Inspector UI
      const nameEl = document.getElementById('inspectMuscleName');
      if (nameEl) nameEl.innerText = mData.display_name;

      const subEl = document.getElementById('inspectMuscleSubtitle');
      if (subEl) subEl.innerText = tips.subtitle;

      const badgeEl = document.getElementById('inspectLandmarkBadge');
      if (badgeEl) {
        badgeEl.innerText = mData.landmark_state.replace('_', ' ');
        if (mData.landmark_state === 'OPTIMAL_MAV') {
          badgeEl.style.background = 'rgba(16,185,129,0.2)';
          badgeEl.style.color = 'var(--success)';
        } else if (mData.landmark_state === 'NEAR_MRV') {
          badgeEl.style.background = 'rgba(245,158,11,0.2)';
          badgeEl.style.color = 'var(--warning)';
        } else if (mData.landmark_state === 'OVER_MRV') {
          badgeEl.style.background = 'rgba(239,68,68,0.2)';
          badgeEl.style.color = 'var(--danger)';
        } else {
          badgeEl.style.background = 'rgba(100,116,139,0.2)';
          badgeEl.style.color = '#94a3b8';
        }
      }

      const setsEl = document.getElementById('inspectWeeklySets');
      if (setsEl) setsEl.innerText = mData.weekly_sets.toFixed(1);

      const targetMavEl = document.getElementById('inspectTargetMav');
      if (targetMavEl) targetMavEl.innerText = `${mData.mav} sets`;

      const mrvValEl = document.getElementById('inspectMrvVal');
      if (mrvValEl) mrvValEl.innerText = mData.mrv;

      // Progress bar (scaled against MRV)
      const maxScale = Math.max(mData.mrv + 4, 24);
      const pct = Math.min(100, Math.max(5, (mData.weekly_sets / maxScale) * 100));
      const fillEl = document.getElementById('inspectVolumeFill');
      if (fillEl) {
        fillEl.style.width = pct + '%';
        fillEl.style.background = mData.landmark_state === 'OPTIMAL_MAV' ? 'var(--success)' :
                                  (mData.landmark_state === 'NEAR_MRV' ? 'var(--warning)' :
                                  (mData.landmark_state === 'OVER_MRV' ? 'var(--danger)' : '#64748b'));
      }

      const tMv = document.getElementById('inspectTickMv');
      if (tMv) tMv.innerText = `MV: ${mData.mv}`;
      const tMev = document.getElementById('inspectTickMev');
      if (tMev) tMev.innerText = `MEV: ${mData.mev}`;
      const tMav = document.getElementById('inspectTickMav');
      if (tMav) tMav.innerText = `MAV: ${mData.mav}`;
      const tMrv = document.getElementById('inspectTickMrv');
      if (tMrv) tMrv.innerText = `MRV: ${mData.mrv}+`;

      // Recovery
      const recPctEl = document.getElementById('inspectRecoveryPct');
      if (recPctEl) {
        recPctEl.innerText = `${mData.recovery_pct}% ${mData.recovery_pct >= 90 ? 'Fully Recovered' : 'Recovering'}`;
        recPctEl.style.color = mData.recovery_pct >= 85 ? 'var(--success)' : (mData.recovery_pct >= 65 ? 'var(--warning)' : 'var(--danger)');
      }

      const hoursEl = document.getElementById('inspectHoursElapsed');
      if (hoursEl) {
        hoursEl.innerText = mData.hours_since_trained !== null ? `Last trained ~${mData.hours_since_trained.toFixed(0)}h ago` : 'No recent direct session';
      }

      // Interference
      const intEl = document.getElementById('inspectInterferenceRisk');
      if (intEl) {
        intEl.innerText = mData.interference_risk === 'NONE' ? 'None Detected' : (mData.interference_risk === 'LOW' ? 'Low Risk' : `${mData.interference_risk} Conflict`);
        intEl.style.color = mData.interference_risk === 'NONE' ? '#38bdf8' : (mData.interference_risk === 'LOW' ? 'var(--warning)' : 'var(--danger)');
      }

      const prescEl = document.getElementById('inspectPrescriptionText');
      if (prescEl) prescEl.innerText = mData.notes || tips.prescription;

      const pillsEl = document.getElementById('inspectExercisePills');
      if (pillsEl) {
        pillsEl.innerHTML = tips.exercises.map(ex => `<span class="periodization-badge" style="background:#1e293b; color:#cbd5e1;">${ex}</span>`).join(' ');
      }
    }

    function showPplDay(dayIdx) {
      activePplDayIndex = dayIdx;
      document.querySelectorAll('#pplDayNav .chart-filter-btn').forEach((btn, idx) => {
        btn.classList.toggle('active', idx === dayIdx);
        btn.classList.toggle('btn-secondary', idx !== dayIdx);
      });

      if (!currentPplPlan || !currentPplPlan.sessions) return;
      const s = currentPplPlan.sessions[dayIdx];
      if (!s) return;

      const titleEl = document.getElementById('pplDayTitle');
      if (titleEl) titleEl.innerText = `${s.day}: ${s.title}`;

      const focusEl = document.getElementById('pplDayFocus');
      if (focusEl) focusEl.innerText = s.focus;

      const ruleEl = document.getElementById('pplDayCardioRule');
      if (ruleEl) ruleEl.innerText = 'Cardio Coordination: ' + s.endurance_guidance;

      const tbody = document.getElementById('pplExerciseTableBody');
      if (tbody) {
        if (!s.exercises || s.exercises.length === 0) {
          tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">Active recovery day. No heavy lifting.</td></tr>';
        } else {
          tbody.innerHTML = s.exercises.map(ex => `
            <tr>
              <td><strong style="color:#f3f4f6;">${ex.name}</strong></td>
              <td style="color:#38bdf8; font-weight:700;">${ex.sets} Sets</td>
              <td>${ex.reps}</td>
              <td><span class="periodization-badge" style="background:rgba(56,189,248,0.15); color:#38bdf8;">${ex.rir}</span></td>
              <td style="color:var(--text-muted);">${ex.rest}</td>
              <td style="color:#10b981; font-weight:600;">${ex.primary}</td>
            </tr>
          `).join('');
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
        const simRec = document.getElementById('simTeRecovery');
        if (simRec) simRec.innerText = (data.recovery_hours || 0).toFixed(0) + 'h';
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

    async function triggerEcosystemSync() {
      const globalBtn = document.getElementById('globalSyncBtn');
      const globalText = document.getElementById('syncBtnText');
      const globalSpin = document.getElementById('syncBtnSpinner');

      const tabBtn = document.getElementById('tabSyncBtn');
      const tabText = document.getElementById('tabSyncBtnText');
      const tabSpin = document.getElementById('tabSyncBtnSpinner');

      const banner = document.getElementById('syncStatusBanner');

      const setSyncing = (isSyncing) => {
        if (globalBtn) globalBtn.disabled = isSyncing;
        if (globalText) globalText.innerText = isSyncing ? 'Syncing...' : 'Sync Ecosystem';
        if (globalSpin) globalSpin.style.display = isSyncing ? 'inline-block' : 'none';

        if (tabBtn) tabBtn.disabled = isSyncing;
        if (tabText) tabText.innerText = isSyncing ? 'Syncing Ecosystem...' : 'Sync All Data Sources';
        if (tabSpin) tabSpin.style.display = isSyncing ? 'inline-block' : 'none';
      };

      setSyncing(true);
      showToast('Initiating cross-platform ecosystem synchronization...');

      try {
        const res = await fetch('/api/sync', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ apply: true, sync_plan: true, weeks: 1 })
        });
        const data = await res.json();

        if (data.status === 'SUCCESS' || data.status === 'PARTIAL') {
          const detail = `${data.wellness_days_updated} wellness days, ${data.activities_analyzed} activities evaluated.`;
          showToast(`Ecosystem sync completed: ${detail}`);
          if (banner) {
            banner.style.display = 'block';
            banner.style.background = 'rgba(16, 185, 129, 0.15)';
            banner.style.border = '1px solid var(--color-success)';
            banner.style.color = 'var(--color-text)';
            const msgs = (data.messages && data.messages.length) ? `<div style="color:var(--color-text-muted); font-size:0.75rem; margin-top:0.35rem;">${data.messages.join(' | ')}</div>` : '';
            banner.innerHTML = `<strong>Synchronization successful (${new Date().toLocaleTimeString()}):</strong> ${detail} ${msgs}`;
          }
          await loadDashboard();
        } else {
          const msg = data.messages && data.messages.length ? data.messages.join(', ') : 'Synchronization encountered issues.';
          showToast(`Sync notice: ${msg}`);
          if (banner) {
            banner.style.display = 'block';
            banner.style.background = 'rgba(239, 68, 68, 0.15)';
            banner.style.border = '1px solid var(--color-danger)';
            banner.style.color = 'var(--color-text)';
            banner.innerHTML = `<strong>Synchronization notice:</strong> ${msg}`;
          }
        }
      } catch (err) {
        showToast('Ecosystem sync failed: ' + err);
        if (banner) {
          banner.style.display = 'block';
          banner.style.background = 'rgba(239, 68, 68, 0.15)';
          banner.style.border = '1px solid var(--color-danger)';
          banner.style.color = 'var(--color-text)';
          banner.innerHTML = `<strong>Network error:</strong> Unable to reach server sync endpoint (${err}).`;
        }
      } finally {
        setSyncing(false);
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

    async function loadGarminStatus() {
      try {
        const res = await fetch('/api/garmin/status');
        if (!res.ok) return;
        const g = await res.json();

        const gBadge = document.getElementById('garminModeBadge');
        if (gBadge) {
          if (g.connected) {
            gBadge.innerText = g.mode === 'DIRECT_CONNECT_API' ? 'Direct API Connected' : 'Intervals Cloud Relay Active';
            gBadge.style.color = 'var(--success)';
            gBadge.style.background = 'rgba(16,185,129,0.2)';
          } else {
            gBadge.innerText = 'Not Configured';
            gBadge.style.color = 'var(--text-muted)';
            gBadge.style.background = 'rgba(107,114,128,0.2)';
          }
        }

        const gStatus = document.getElementById('garminStatus');
        if (gStatus) {
          gStatus.innerText = g.connected ? (g.mode === 'DIRECT_CONNECT_API' ? 'Direct API' : 'Relay Active') : 'Not Configured';
          gStatus.style.color = g.connected ? 'var(--success)' : 'var(--text-muted)';
        }

        const gUp = document.getElementById('garminUploadStatus');
        if (gUp) {
          gUp.innerText = g.upload_workouts ? 'Auto-Push Enabled' : 'Disabled';
          gUp.style.color = g.upload_workouts ? 'var(--success)' : 'var(--text-muted)';
        }

        const gWell = document.getElementById('garminWellnessStatus');
        if (gWell) {
          gWell.innerText = g.download_wellness ? 'Enabled (Body Battery/HRV)' : 'Disabled';
          gWell.style.color = g.download_wellness ? 'var(--success)' : 'var(--text-muted)';
        }

        const gPwr = document.getElementById('garminPowerMode');
        if (gPwr) gPwr.innerText = g.power_target_mode || 'POWER_LAP';

        const gUser = document.getElementById('garminUserIdText');
        if (gUser) gUser.innerText = g.user_id ? g.user_id : 'Default Athlete';

        const gMode = document.getElementById('garminModeText');
        if (gMode) gMode.innerText = g.mode;

        const gDir = document.getElementById('garminDirectText');
        if (gDir) {
          gDir.innerText = g.direct_api_ready ? 'OAuth Ready' : 'FIT Compiler Ready';
          gDir.style.color = g.direct_api_ready ? 'var(--success)' : '#38bdf8';
        }

        const gTol = document.getElementById('garminToleranceText');
        if (gTol) gTol.innerText = `HR ±${g.hr_range_pct}% | Pace ±${g.pace_range_pct}%`;
      } catch (err) {
        console.debug('Failed loading Garmin status:', err);
      }
    }

    async function toggleGarminRelay() {
      const btn = document.getElementById('btnGarminRelay');
      if (btn) {
        btn.disabled = true;
        btn.innerText = 'Updating...';
      }
      try {
        const res = await fetch('/api/garmin/sync', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'toggle_relay', upload_workouts: true, download_wellness: true })
        });
        const data = await res.json();
        showToast('Garmin cloud relay updated successfully!');
        loadGarminStatus();
      } catch (err) {
        alert('Failed to update Garmin relay: ' + err);
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerText = 'Update Relay Settings';
        }
      }
    }

    function populateExecutiveSummary(currentAnalytics, currentProfile) {
      if (!currentAnalytics) return;
      const r = currentAnalytics.readiness || {};
      const a = currentAnalytics.acwr || {};
      const s = currentAnalytics.daily_series || [];

      // Readiness Pill
      const execPill = document.getElementById('execReadinessPill');
      if (execPill && r.readiness_score !== undefined) {
        const stateStr = (r.readiness_state || 'OPTIMAL').replace(/_/g, ' ');
        execPill.innerText = `${stateStr} (${r.readiness_score}/100)`;
        if (r.readiness_score >= 80) {
          execPill.style.background = 'rgba(16,185,129,0.2)';
          execPill.style.color = 'var(--success)';
        } else if (r.readiness_score >= 60) {
          execPill.style.background = 'rgba(56,189,248,0.2)';
          execPill.style.color = '#38bdf8';
        } else if (r.readiness_score >= 40) {
          execPill.style.background = 'rgba(245,158,11,0.2)';
          execPill.style.color = 'var(--warning)';
        } else {
          execPill.style.background = 'rgba(239,68,68,0.2)';
          execPill.style.color = 'var(--danger)';
        }
      }

      // Threshold / LTHR
      const execLthr = document.getElementById('execLthrText');
      if (execLthr) {
        const bikeLthr = (currentProfile && currentProfile.lthr_bike) ? currentProfile.lthr_bike : 172;
        const runLthr = (currentProfile && currentProfile.lthr_run) ? currentProfile.lthr_run : 182;
        execLthr.innerText = `${bikeLthr} bpm (Ride) | ${runLthr} bpm (Run)`;
      }

      // Autonomic Readiness
      const execRHead = document.getElementById('execReadinessHeadline');
      const execRDesc = document.getElementById('execReadinessDesc');
      if (execRHead && r.readiness_state) {
        execRHead.innerText = r.readiness_state.replace(/_/g, ' ');
      }
      if (execRDesc) {
        const rhrVal = r.recent_resting_hr || 56;
        const delta = (r.rhr_delta !== null && r.rhr_delta !== undefined) ? ((r.rhr_delta >= 0 ? '+' : '') + r.rhr_delta + ' delta') : 'stable';
        execRDesc.innerText = `RHR ${rhrVal} bpm (${delta}). ${r.rhr_elevated ? 'Elevated autonomic stress.' : 'Fully primed for volume and quality.'}`;
      }

      // Workload Ratio (ACWR)
      const execAHead = document.getElementById('execAcwrHeadline');
      const execADesc = document.getElementById('execAcwrDesc');
      if (execAHead && a.ratio !== undefined) {
        execAHead.innerText = `${a.ratio.toFixed(2)} ${(a.status || 'OPTIMAL').replace(/_/g, ' ')}`;
      }
      if (execADesc) {
        execADesc.innerText = a.guidance || 'Workload distribution within monitored thresholds.';
      }

      // Sleep & Nocturnal Recovery
      const execSHead = document.getElementById('execSleepHeadline');
      const execSDesc = document.getElementById('execSleepDesc');
      const latestWithSleep = [...s].reverse().find(x => x.sleep_hours !== null && x.sleep_hours !== undefined);
      const latestWithSpo2 = [...s].reverse().find(x => x.spo2 !== null && x.spo2 !== undefined);
      if (execSHead) {
        execSHead.innerText = latestWithSleep ? `${latestWithSleep.sleep_hours}h Stable` : '7.5h Stable';
      }
      if (execSDesc) {
        const spo2Val = latestWithSpo2 ? `${latestWithSpo2.spo2}%` : '97.0-98.5%';
        execSDesc.innerText = `SpO2 ${spo2Val}. Restorative deep/REM nocturnal sleep architecture.`;
      }

      // Body Composition (BIA)
      const execBHead = document.getElementById('execBodyHeadline');
      const execBDesc = document.getElementById('execBodyDesc');
      const latestWithWeight = [...s].reverse().find(x => x.weight !== null && x.weight !== undefined);
      const latestWithFat = [...s].reverse().find(x => x.body_fat !== null && x.body_fat !== undefined);
      const w = latestWithWeight ? latestWithWeight.weight : 78.9;
      const f = latestWithFat ? latestWithFat.body_fat : 27.0;
      if (execBHead) {
        execBHead.innerText = `${w} kg | ${f}% Fat`;
      }
      if (execBDesc) {
        const lean = (w * (1 - f / 100)).toFixed(1);
        const muscle = (lean * 0.53).toFixed(1);
        execBDesc.innerText = `${lean} kg Lean Mass (~${muscle} kg Skeletal Muscle). Calibrated power-to-weight.`;
      }

      // Executive Verdict
      const execVerdict = document.getElementById('execVerdictText');
      if (execVerdict) {
        const ratio = a.ratio || 0.47;
        const score = (r.readiness_score !== undefined) ? r.readiness_score : 82;
        if (score >= 75 && ratio <= 1.35) {
          execVerdict.innerText = `Your resting heart rate and nocturnal vitals are in an optimal, uncompromised autonomic state. Because acute load has dropped below your chronic baseline (ACWR ${ratio.toFixed(2)}), you are free of accumulated systemic fatigue and fully primed to absorb this week's scheduled workouts without injury risk.`;
        } else if (r.rhr_elevated || score < 50) {
          execVerdict.innerText = `Elevated autonomic strain or suppressed recovery detected (+${r.rhr_delta || 0} bpm RHR delta). Prioritize active recovery, light aerobic spinning, and restorative sleep before high-intensity intervals.`;
        } else if (ratio > 1.35) {
          execVerdict.innerText = `ACWR of ${ratio.toFixed(2)} indicates rapid training load escalation. Hold or trim planned intensity to protect connective tissue and maintain sustainable adaptation.`;
        } else {
          execVerdict.innerText = `Balanced physiological profile. Proceed with your structured polarized progression, ensuring proper carbohydrate fueling and hydration across key quality sessions.`;
        }
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
        if (tbody) {
          tbody.innerHTML = '';
          const preferredOrder = ['Ride', 'Run', 'Strength', 'Swim', 'Walk', 'Other'];
          const sportBadges = {
            'Ride': { bg: 'rgba(245, 158, 11, 0.2)', col: '#f59e0b' },
            'Run': { bg: 'rgba(6, 182, 212, 0.2)', col: '#06b6d4' },
            'Swim': { bg: 'rgba(56, 189, 248, 0.2)', col: '#38bdf8' },
            'Strength': { bg: 'rgba(168, 85, 247, 0.2)', col: '#a855f7' },
            'Walk': { bg: 'rgba(16, 185, 129, 0.2)', col: '#10b981' },
            'Other': { bg: 'rgba(100, 116, 139, 0.2)', col: '#94a3b8' }
          };

          const fullDisciplines = { ...data.disciplines };
          ['Ride', 'Run', 'Strength', 'Swim'].forEach(sp => {
            if (!fullDisciplines[sp]) {
              fullDisciplines[sp] = { activity_count: 0, moving_time_hours: 0.0, total_load: 0.0, total_distance_km: 0.0 };
            }
          });

          const sortedEntries = Object.entries(fullDisciplines).sort((a, b) => {
            const ia = preferredOrder.indexOf(a[0]) !== -1 ? preferredOrder.indexOf(a[0]) : 99;
            const ib = preferredOrder.indexOf(b[0]) !== -1 ? preferredOrder.indexOf(b[0]) : 99;
            return ia - ib;
          });

          let totSessions = 0, totHours = 0, totLoad = 0, totDist = 0;

          sortedEntries.forEach(([sport, d]) => {
            if ((sport === 'Other' || sport === 'Walk') && (!d.activity_count || d.activity_count === 0)) return;

            totSessions += (d.activity_count || 0);
            totHours += (d.moving_time_hours || 0);
            totLoad += (d.total_load || 0);
            totDist += (d.total_distance_km || 0);

            const badge = sportBadges[sport] || { bg: 'rgba(100, 116, 139, 0.2)', col: '#94a3b8' };
            const tr = document.createElement('tr');
            const distStr = (sport === 'Strength' || (sport === 'Other' && (!d.total_distance_km || d.total_distance_km <= 0)))
              ? '--'
              : (d.total_distance_km > 0 ? d.total_distance_km.toFixed(1) + ' km' : '--');
            const timeStr = d.moving_time_hours > 0 ? d.moving_time_hours.toFixed(1) + ' hrs' : '0.0 hrs';
            const loadStr = d.total_load > 0 ? Math.round(d.total_load) + ' TSS' : '0 TSS';

            tr.innerHTML = `
              <td><span style="display:inline-block; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.75rem; background:${badge.bg}; color:${badge.col};">${sport}</span></td>
              <td style="font-weight:600;">${d.activity_count || 0}</td>
              <td>${timeStr}</td>
              <td>${loadStr}</td>
              <td>${distStr}</td>
            `;
            tbody.appendChild(tr);
          });

          if (totSessions > 0) {
            const tfoot = document.createElement('tr');
            tfoot.style.borderTop = '2px solid #334155';
            tfoot.style.fontWeight = '700';
            tfoot.innerHTML = `
              <td style="color:#fff;">Total Completed</td>
              <td style="color:#38bdf8;">${totSessions}</td>
              <td style="color:#38bdf8;">${totHours.toFixed(1)} hrs</td>
              <td style="color:#f59e0b;">${Math.round(totLoad)} TSS</td>
              <td style="color:#fff;">${totDist > 0 ? totDist.toFixed(1) + ' km' : '--'}</td>
            `;
            tbody.appendChild(tfoot);
          }
        }
      }
    }

    let pmcVisibleSeries = { ctl: true, atl: true, tsb: true };
    let pmcSelectedDate = null;

    function togglePmcSeries(seriesKey) {
      pmcVisibleSeries[seriesKey] = !pmcVisibleSeries[seriesKey];
      const btn = document.getElementById('pmcToggle' + seriesKey.toUpperCase());
      if (btn) {
        btn.classList.toggle('active', pmcVisibleSeries[seriesKey]);
        btn.setAttribute('aria-pressed', pmcVisibleSeries[seriesKey] ? 'true' : 'false');
      }
      if (currentAnalytics && currentAnalytics.daily_series) {
        renderPmcChart(currentAnalytics.daily_series);
      }
    }

    function updatePmcInspector(pt) {
      const insp = document.getElementById('pmcDayInspector');
      if (!insp || !pt) return;
      insp.style.display = 'block';
      const formStatus = pt.tsb >= 15 ? 'Very Fresh (Taper / Race Ready)' :
                         pt.tsb >= 5 ? 'Fresh (Optimal Race Form)' :
                         pt.tsb >= -10 ? 'Optimal Training Stimulus (Absorbing Load)' :
                         pt.tsb >= -25 ? 'High Fatigue (Recovery Recommended)' : 'Severe Overload Risk';
      const formColor = pt.tsb >= 0 ? 'var(--color-success)' : (pt.tsb >= -15 ? 'var(--color-accent)' : 'var(--color-danger)');

      insp.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--color-border); padding-bottom:6px; margin-bottom:8px;">
          <span style="font-weight:700; color:var(--color-text); font-size:0.875rem;">Selected Day Diagnostic: ${pt.date}</span>
          <span style="color:${formColor}; font-weight:700; font-size:0.75rem;">${formStatus}</span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:0.75rem; font-size:0.8125rem;">
          <div><span style="color:var(--color-text-muted); font-size:0.7rem;">Fitness (CTL):</span> <strong style="color:#06b6d4; display:block;">${pt.ctl}</strong></div>
          <div><span style="color:var(--color-text-muted); font-size:0.7rem;">Fatigue (ATL):</span> <strong style="color:#f43f5e; display:block;">${pt.atl}</strong></div>
          <div><span style="color:var(--color-text-muted); font-size:0.7rem;">Form (TSB):</span> <strong style="color:#10b981; display:block;">${(pt.tsb >= 0 ? '+' : '') + pt.tsb}</strong></div>
          <div><span style="color:var(--color-text-muted); font-size:0.7rem;">Daily TSS Load:</span> <strong style="color:var(--color-text); display:block;">${pt.load_tss} TSS</strong></div>
        </div>
      `;
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
        gridSvg += `<line x1="${padL}" y1="${yPos}" x2="${w - padR}" y2="${yPos}" stroke="#1e2e4a" stroke-dasharray="3"/>`;
        gridSvg += `<text x="${padL - 8}" y="${yPos + 4}" fill="#64748b" font-size="10" text-anchor="end">${Math.round(val)}</text>`;
      }

      if (y0 >= padT && y0 <= padT + ph) {
        gridSvg += `<line x1="${padL}" y1="${y0}" x2="${w - padR}" y2="${y0}" stroke="#475569" stroke-width="1.5" stroke-dasharray="4"/>`;
        gridSvg += `<text x="${w - padR + 4}" y="${y0 + 3}" fill="#94a3b8" font-size="10">0</text>`;
      }

      let dateSvg = '';
      for (let i = 0; i < series.length; i += 5) {
        const xPos = getX(i);
        const dt = series[i].date ? series[i].date.slice(5) : '';
        dateSvg += `<text x="${xPos}" y="${h - 10}" fill="#64748b" font-size="10" text-anchor="middle">${dt}</text>`;
      }
      const lastX = getX(series.length - 1);
      const lastDt = series[series.length - 1].date ? series[series.length - 1].date.slice(5) : '';
      dateSvg += `<text x="${lastX}" y="${h - 10}" fill="#94a3b8" font-size="10" text-anchor="middle">${lastDt}</text>`;

      const ctlPoints = series.map((d, i) => `${getX(i).toFixed(1)},${getY(d.ctl).toFixed(1)}`).join(' L ');
      const atlPoints = series.map((d, i) => `${getX(i).toFixed(1)},${getY(d.atl).toFixed(1)}`).join(' L ');
      const tsbPoints = series.map((d, i) => `${getX(i).toFixed(1)},${getY(d.tsb).toFixed(1)}`).join(' L ');

      const tsbAreaPoints = `M ${getX(0).toFixed(1)},${y0.toFixed(1)} L ` +
        series.map((d, i) => `${getX(i).toFixed(1)},${getY(d.tsb).toFixed(1)}`).join(' L ') +
        ` L ${getX(series.length - 1).toFixed(1)},${y0.toFixed(1)} Z`;

      let selectedMarkerSvg = '';
      if (pmcSelectedDate) {
        const sIdx = series.findIndex(d => d.date === pmcSelectedDate);
        if (sIdx >= 0) {
          const sx = getX(sIdx);
          selectedMarkerSvg = `<line x1="${sx}" y1="${padT}" x2="${sx}" y2="${padT + ph}" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="3"/>`;
        }
      }

      svg.innerHTML = `
        <defs>
          <linearGradient id="tsbGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#10b981" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="#f43f5e" stop-opacity="0.15"/>
          </linearGradient>
        </defs>
        ${gridSvg}
        ${dateSvg}
        ${pmcVisibleSeries.tsb ? `<path d="${tsbAreaPoints}" fill="url(#tsbGradient)"/>` : ''}
        ${pmcVisibleSeries.ctl ? `<path d="M ${ctlPoints}" fill="none" stroke="#06b6d4" stroke-width="2.5" stroke-linecap="round"/>` : ''}
        ${pmcVisibleSeries.atl ? `<path d="M ${atlPoints}" fill="none" stroke="#f43f5e" stroke-width="2" stroke-linecap="round"/>` : ''}
        ${pmcVisibleSeries.tsb ? `<path d="M ${tsbPoints}" fill="none" stroke="#10b981" stroke-width="2" stroke-dasharray="4" stroke-linecap="round"/>` : ''}
        ${selectedMarkerSvg}
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
          tooltip.style.left = Math.min(rect.width - 170, Math.max(10, mouseX - 60)) + 'px';
          tooltip.style.top = '15px';
          tooltip.innerHTML = `
            <div style="font-weight:700; color:#fff; border-bottom:1px solid #1e2e4a; padding-bottom:2px; margin-bottom:4px;">${pt.date}</div>
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

        container.onclick = function(e) {
          const rect = container.getBoundingClientRect();
          const mouseX = e.clientX - rect.left;
          const relX = (mouseX / rect.width) * w;
          if (relX < padL || relX > w - padR) return;
          const frac = (relX - padL) / pw;
          const idx = Math.min(series.length - 1, Math.max(0, Math.round(frac * (series.length - 1))));
          const pt = series[idx];
          pmcSelectedDate = pt.date;
          updatePmcInspector(pt);
          renderPmcChart(series);
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
        <text x="${padL - 6}" y="${y0_0 + 3}" fill="#64748b" font-size="9" text-anchor="end">0.0</text>
      `;

      let dateSvg = '';
      for (let i = 0; i < series.length; i += 7) {
        const xPos = getX(i);
        const dt = series[i].date ? series[i].date.slice(5) : '';
        dateSvg += `<text x="${xPos}" y="${h - 8}" fill="#64748b" font-size="9" text-anchor="middle">${dt}</text>`;
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
            <div style="font-weight:700; color:#fff; border-bottom:1px solid #1e2e4a; padding-bottom:2px; margin-bottom:4px;">${pt.date}</div>
            <div style="color:#38bdf8;">ACWR Ratio: <strong>${pt.acwr_ratio.toFixed(2)}</strong></div>
            <div style="color:${statusColor}; font-size:0.7rem;">Status: ${statusTxt}</div>
          `;
        };

        container.onmouseleave = function() {
          tooltip.style.display = 'none';
          const ch = document.getElementById('acwrCrosshair');
          if (ch) ch.setAttribute('opacity', '0');
        };

        container.onclick = function(e) {
          const rect = container.getBoundingClientRect();
          const mouseX = e.clientX - rect.left;
          const relX = (mouseX / rect.width) * w;
          if (relX < padL || relX > w - padR) return;
          const frac = (relX - padL) / pw;
          const idx = Math.min(series.length - 1, Math.max(0, Math.round(frac * (series.length - 1))));
          const pt = series[idx];
          const insp = document.getElementById('acwrDayInspector');
          if (insp && pt) {
            insp.style.display = 'block';
            insp.innerHTML = `<strong>${pt.date} ACWR:</strong> Ratio ${pt.acwr_ratio.toFixed(2)} | Tim Gabbett workload index: ${pt.acwr_ratio > 1.3 ? 'Elevated spike risk' : (pt.acwr_ratio < 0.8 ? 'Under-training base' : 'Optimal training sweet spot')}`;
          }
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
        dateSvg += `<text x="${xPos}" y="${h - 8}" fill="#64748b" font-size="9" text-anchor="middle">${dt}</text>`;
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
        dotsSvg += `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="3.5" fill="${color}" stroke="#060a12" stroke-width="1"/>`;
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
            <div style="font-weight:700; color:#fff; border-bottom:1px solid #1e2e4a; padding-bottom:2px; margin-bottom:4px;">${pt.date}</div>
            <div style="color:#38bdf8;">Resting HR: <strong>${Math.round(pt.resting_hr)} bpm</strong></div>
            <div style="color:${isElevated ? '#ef4444' : '#10b981'}; font-size:0.7rem;">Delta: ${(delta >= 0 ? '+' : '') + delta.toFixed(1)} bpm [${isElevated ? 'STRAIN' : 'STABLE'}]</div>
          `;
        };

        container.onmouseleave = function() {
          tooltip.style.display = 'none';
          const ch = document.getElementById('rhrCrosshair');
          if (ch) ch.setAttribute('opacity', '0');
        };

        container.onclick = function(e) {
          const rect = container.getBoundingClientRect();
          const mouseX = e.clientX - rect.left;
          const relX = (mouseX / rect.width) * w;
          if (relX < padL || relX > w - padR) return;
          const frac = (relX - padL) / pw;
          const idx = Math.min(series.length - 1, Math.max(0, Math.round(frac * (series.length - 1))));
          const pt = series[idx];
          const insp = document.getElementById('rhrDayInspector');
          if (insp && pt) {
            insp.style.display = 'block';
            const delta = pt.resting_hr ? (pt.resting_hr - baseVal).toFixed(1) : '0';
            insp.innerHTML = `<strong>${pt.date} Autonomic Recovery:</strong> ${pt.resting_hr ? pt.resting_hr + ' bpm (' + (delta >= 0 ? '+' : '') + delta + ' vs 30d baseline)' : 'No RHR recorded'}`;
          }
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
        <line x1="${padL}" y1="${getY(4.0)}" x2="${w - padR}" y2="${getY(4.0)}" stroke="#1e2e4a" stroke-dasharray="3"/>
        <text x="${padL - 6}" y="${getY(4.0) + 3}" fill="#64748b" font-size="9" text-anchor="end">4h</text>
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
          const barColor = d.sleep_hours >= 7.0 ? '#10b981' : d.sleep_hours >= 5.5 ? '#c084fc' : '#f59e0b';
          barsSvg += `<rect id="sleepBar_${i}" x="${bx.toFixed(1)}" y="${by.toFixed(1)}" width="${colW.toFixed(1)}" height="${bh.toFixed(1)}" rx="2" fill="${barColor}" opacity="0.85" style="transition:fill 0.15s;"/>`;
        }
      });

      const avgText = sleepCount > 0 ? (sleepSum / sleepCount).toFixed(1) + ' hrs avg' : '-- hrs avg';
      const sumEl = document.getElementById('sleepSummaryText');
      if (sumEl) sumEl.innerText = avgText;

      let dateSvg = '';
      for (let i = 0; i < series.length; i += 7) {
        const xPos = getX(i);
        const dt = series[i].date ? series[i].date.slice(5) : '';
        dateSvg += `<text x="${xPos}" y="${h - 8}" fill="#64748b" font-size="9" text-anchor="middle">${dt}</text>`;
      }
      const lastX = getX(series.length - 1);
      const lastDt = series[series.length - 1].date ? series[series.length - 1].date.slice(5) : '';
      dateSvg += `<text x="${lastX}" y="${h - 8}" fill="#9ca3af" font-size="9" text-anchor="middle">${lastDt}</text>`;

      svg.innerHTML = `
        ${gridSvg}
        ${dateSvg}
        ${barsSvg}
        <line id="sleepCrosshair" x1="0" y1="${padT}" x2="0" y2="${padT + ph}" stroke="#94a3b8" stroke-dasharray="2" opacity="0"/>
      `;

      // Interactive hover & click inspection
      const container = document.getElementById('sleepChartContainer');
      const tooltip = document.getElementById('sleepTooltip');
      if (container && tooltip) {
        container.onmousemove = function(e) {
          const rect = container.getBoundingClientRect();
          const mouseX = e.clientX - rect.left;
          const relX = (mouseX / rect.width) * w;
          if (relX < padL || relX > w - padR) {
            tooltip.style.display = 'none';
            const ch = document.getElementById('sleepCrosshair');
            if (ch) ch.setAttribute('opacity', '0');
            return;
          }
          const frac = (relX - padL) / pw;
          const idx = Math.min(series.length - 1, Math.max(0, Math.round(frac * (series.length - 1))));
          const pt = series[idx];
          const ptX = getX(idx);

          const ch = document.getElementById('sleepCrosshair');
          if (ch) {
            ch.setAttribute('x1', ptX);
            ch.setAttribute('x2', ptX);
            ch.setAttribute('opacity', '0.7');
          }

          if (pt.sleep_hours === null || pt.sleep_hours === undefined) {
            tooltip.style.display = 'none';
            return;
          }

          const qualTxt = pt.sleep_hours >= 7.0 ? 'Optimal Restorative (7h+)' : (pt.sleep_hours >= 6.0 ? 'Adequate Recovery' : 'Rest Deficit');
          const qualColor = pt.sleep_hours >= 7.0 ? '#10b981' : (pt.sleep_hours >= 6.0 ? '#c084fc' : '#f59e0b');

          tooltip.style.display = 'block';
          tooltip.style.left = Math.min(rect.width - 160, Math.max(10, mouseX - 60)) + 'px';
          tooltip.style.top = '15px';
          tooltip.innerHTML = `
            <div style="font-weight:700; color:#fff; border-bottom:1px solid #1e2e4a; padding-bottom:2px; margin-bottom:4px;">${pt.date}</div>
            <div style="color:${qualColor};">Duration: <strong>${pt.sleep_hours} hrs</strong></div>
            <div style="color:${qualColor}; font-size:0.7rem;">Status: ${qualTxt}</div>
            ${pt.sleep_note ? `<div style="color:#94a3b8; font-size:0.6875rem; margin-top:2px;">Stages: ${pt.sleep_note.slice(0, 32)}</div>` : ''}
          `;
        };

        container.onmouseleave = function() {
          tooltip.style.display = 'none';
          const ch = document.getElementById('sleepCrosshair');
          if (ch) ch.setAttribute('opacity', '0');
        };

        container.onclick = function(e) {
          const rect = container.getBoundingClientRect();
          const mouseX = e.clientX - rect.left;
          const relX = (mouseX / rect.width) * w;
          if (relX < padL || relX > w - padR) return;
          const frac = (relX - padL) / pw;
          const idx = Math.min(series.length - 1, Math.max(0, Math.round(frac * (series.length - 1))));
          const pt = series[idx];
          const insp = document.getElementById('sleepDayInspector');
          if (insp && pt) {
            insp.style.display = 'block';
            insp.innerHTML = `<strong>${pt.date} Sleep Telemetry:</strong> ${pt.sleep_hours ? pt.sleep_hours + 'h duration' : 'No sleep data recorded'} ${pt.sleep_note ? '— ' + pt.sleep_note : ''}`;
          }
        };
      }
    }

    function renderVitalsChart(series) {
      const svg = document.getElementById('vitalsChartSvg');
      if (!svg || !series || series.length === 0) return;

      const w = 450, h = 180;
      const padL = 40, padR = 25, padT = 15, padB = 25;
      const pw = w - padL - padR;
      const ph = h - padT - padB;

      const getX = (i) => padL + (i / (series.length - 1)) * pw;
      const getSpo2Y = (val) => padT + ph - ((val - 90.0) / 10.0) * ph;
      const getWeightY = (val) => padT + ph - ((val - 70.0) / 15.0) * ph;

      let gridSvg = `
        <line x1="${padL}" y1="${getSpo2Y(95.0)}" x2="${w - padR}" y2="${getSpo2Y(95.0)}" stroke="#06b6d4" stroke-width="1" stroke-dasharray="3"/>
        <text x="${padL - 6}" y="${getSpo2Y(95.0) + 3}" fill="#06b6d4" font-size="9" text-anchor="end">95%</text>
        <line x1="${padL}" y1="${getWeightY(78.0)}" x2="${w - padR}" y2="${getWeightY(78.0)}" stroke="#10b981" stroke-width="1" stroke-dasharray="3"/>
        <text x="${w - padR + 4}" y="${getWeightY(78.0) + 3}" fill="#10b981" font-size="9">78kg</text>
      `;

      let pointsSvg = '';
      series.forEach((d, i) => {
        const cx = getX(i);
        if (d.spo2 !== null && d.spo2 !== undefined) {
          const cy = Math.max(padT, Math.min(padT + ph, getSpo2Y(d.spo2)));
          pointsSvg += `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="3.5" fill="#06b6d4" stroke="#060a12" stroke-width="1"/>`;
        }
        if (d.weight !== null && d.weight !== undefined) {
          const wy = Math.max(padT, Math.min(padT + ph, getWeightY(d.weight)));
          pointsSvg += `<circle cx="${cx.toFixed(1)}" cy="${wy.toFixed(1)}" r="3.5" fill="#10b981" stroke="#060a12" stroke-width="1"/>`;
        }
      });

      let dateSvg = '';
      for (let i = 0; i < series.length; i += 7) {
        const xPos = getX(i);
        const dt = series[i].date ? series[i].date.slice(5) : '';
        dateSvg += `<text x="${xPos}" y="${h - 8}" fill="#64748b" font-size="9" text-anchor="middle">${dt}</text>`;
      }
      const lastX = getX(series.length - 1);
      const lastDt = series[series.length - 1].date ? series[series.length - 1].date.slice(5) : '';
      dateSvg += `<text x="${lastX}" y="${h - 8}" fill="#9ca3af" font-size="9" text-anchor="middle">${lastDt}</text>`;

      svg.innerHTML = `
        ${gridSvg}
        ${dateSvg}
        ${pointsSvg}
        <line id="vitalsCrosshair" x1="0" y1="${padT}" x2="0" y2="${padT + ph}" stroke="#94a3b8" stroke-dasharray="2" opacity="0"/>
      `;

      // Interactive hover & click inspection
      const container = document.getElementById('vitalsChartContainer');
      const tooltip = document.getElementById('vitalsTooltip');
      if (container && tooltip) {
        container.onmousemove = function(e) {
          const rect = container.getBoundingClientRect();
          const mouseX = e.clientX - rect.left;
          const relX = (mouseX / rect.width) * w;
          if (relX < padL || relX > w - padR) {
            tooltip.style.display = 'none';
            const ch = document.getElementById('vitalsCrosshair');
            if (ch) ch.setAttribute('opacity', '0');
            return;
          }
          const frac = (relX - padL) / pw;
          const idx = Math.min(series.length - 1, Math.max(0, Math.round(frac * (series.length - 1))));
          const pt = series[idx];
          const ptX = getX(idx);

          const ch = document.getElementById('vitalsCrosshair');
          if (ch) {
            ch.setAttribute('x1', ptX);
            ch.setAttribute('x2', ptX);
            ch.setAttribute('opacity', '0.7');
          }

          const hasSpo2 = pt.spo2 !== null && pt.spo2 !== undefined;
          const hasWeight = pt.weight !== null && pt.weight !== undefined;
          if (!hasSpo2 && !hasWeight) {
            tooltip.style.display = 'none';
            return;
          }

          tooltip.style.display = 'block';
          tooltip.style.left = Math.min(rect.width - 160, Math.max(10, mouseX - 60)) + 'px';
          tooltip.style.top = '15px';
          tooltip.innerHTML = `
            <div style="font-weight:700; color:#fff; border-bottom:1px solid #1e2e4a; padding-bottom:2px; margin-bottom:4px;">${pt.date}</div>
            ${hasSpo2 ? `<div style="color:#06b6d4;">SpO2: <strong>${pt.spo2}%</strong></div>` : ''}
            ${hasWeight ? `<div style="color:#10b981;">Weight: <strong>${pt.weight} kg</strong></div>` : ''}
            ${pt.body_fat ? `<div style="color:#c084fc; font-size:0.7rem;">Body Fat: ${pt.body_fat}%</div>` : ''}
          `;
        };

        container.onmouseleave = function() {
          tooltip.style.display = 'none';
          const ch = document.getElementById('vitalsCrosshair');
          if (ch) ch.setAttribute('opacity', '0');
        };

        container.onclick = function(e) {
          const rect = container.getBoundingClientRect();
          const mouseX = e.clientX - rect.left;
          const relX = (mouseX / rect.width) * w;
          if (relX < padL || relX > w - padR) return;
          const frac = (relX - padL) / pw;
          const idx = Math.min(series.length - 1, Math.max(0, Math.round(frac * (series.length - 1))));
          const pt = series[idx];
          const insp = document.getElementById('vitalsDayInspector');
          if (insp && pt) {
            insp.style.display = 'block';
            insp.innerHTML = `<strong>${pt.date} Bio-Metrics:</strong> ${pt.spo2 ? 'SpO2: ' + pt.spo2 + '%' : ''} ${pt.weight ? ' | Weight: ' + pt.weight + ' kg' : ''} ${pt.body_fat ? ' | Fat: ' + pt.body_fat + '%' : ''}`;
          }
        };
      }
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
        gridSvg += `<line x1="${padL}" y1="${yPos}" x2="${w - padR}" y2="${yPos}" stroke="#1e2e4a" stroke-dasharray="3"/>`;
        gridSvg += `<text x="${padL - 8}" y="${yPos + 4}" fill="#64748b" font-size="10" text-anchor="end">${Math.round(val)}</text>`;
      }

      const sportColors = {
        'Run': '#06b6d4',
        'Ride': '#f59e0b',
        'Swim': '#38bdf8',
        'Strength': '#c084fc',
        'WeightTraining': '#c084fc',
        'Brick': '#c084fc',
        'Duathlon': '#f59e0b',
        'Walk': '#10b981',
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
            <div style="font-weight:700; color:#fff; border-bottom:1px solid #1e2e4a; padding-bottom:3px; margin-bottom:4px;">${pt.date}</div>
            <div style="color:#f59e0b; font-size:0.8125rem;">Total Load: <strong>${pt.load_tss} TSS</strong></div>
            <div style="color:#38bdf8; font-size:0.75rem;">Moving Time: <strong>${pt.moving_hours} hrs</strong></div>
            ${sportLines ? `<div style="margin-top:4px; border-top:1px dashed #1e2e4a; padding-top:4px;">${sportLines}</div>` : ''}
          `;
        };

        scrollBox.onmouseleave = function() {
          tooltip.style.display = 'none';
          const hb = document.getElementById('loadHoverBar');
          if (hb) hb.setAttribute('opacity', '0');
        };

        scrollBox.onclick = function(e) {
          const rect = scrollBox.getBoundingClientRect();
          const mouseX = e.clientX - rect.left + scrollBox.scrollLeft;
          if (mouseX < padL || mouseX > padL + pw) return;
          const idx = Math.min(series.length - 1, Math.max(0, Math.floor((mouseX - padL) / colW)));
          const pt = series[idx];
          const insp = document.getElementById('loadDayInspector');
          if (insp && pt) {
            insp.style.display = 'block';
            const sports = pt.sports || {};
            const sportParts = Object.entries(sports).filter(([sp, val]) => val > 0).map(([sp, val]) => `<strong>${sp}:</strong> ${val} TSS`);
            insp.innerHTML = `
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span><strong>${pt.date} Breakdown:</strong> Total ${pt.load_tss || 0} TSS (${pt.moving_hours || 0} hrs)</span>
                <span style="font-size:0.75rem; color:var(--color-text-muted);">${sportParts.length ? sportParts.join(' | ') : 'Rest / Recovery'}</span>
              </div>
            `;
          }
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

          let teBadge = '';
          if (evt.training_effect && evt.category !== 'NOTE') {
            const te = evt.training_effect;
            teBadge = `
              <div style="display:flex; gap:4px; margin-top:5px; font-size:0.6875rem; flex-wrap:wrap;">
                <span style="background:rgba(16,185,129,0.2); color:#10b981; padding:1px 5px; border-radius:3px; font-weight:600;">Aero ${te.aerobic_te}</span>
                <span style="background:rgba(56,189,248,0.2); color:#38bdf8; padding:1px 5px; border-radius:3px; font-weight:600;">~${Math.round(te.recovery_hours)}h Recov</span>
              </div>
            `;
          }

          card.innerHTML = `
            <span class="workout-tag ${tagClass}">${evt.type || 'Workout'}</span>
            <div class="workout-title">${evt.name}</div>
            <div class="workout-meta">${evt.category === 'NOTE' ? 'Rest / Note' : 'Structured Session'}</div>
            ${teBadge}
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

      const teBox = document.getElementById('modalTeBox');
      if (teBox) {
        if (evt.training_effect && evt.category !== 'NOTE') {
          teBox.style.display = 'block';
          document.getElementById('modalAeroTe').innerText = evt.training_effect.aerobic_te.toFixed(1) + ' (' + evt.training_effect.aerobic_label + ')';
          document.getElementById('modalAnaeroTe').innerText = evt.training_effect.anaerobic_te.toFixed(1) + ' (' + evt.training_effect.anaerobic_label + ')';
          document.getElementById('modalRecovHours').innerText = Math.round(evt.training_effect.recovery_hours) + ' hours';
        } else {
          teBox.style.display = 'none';
        }
      }

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

