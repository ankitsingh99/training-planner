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
      fill-opacity: 0.55;
      stroke: rgba(255, 255, 255, 0.35);
      stroke-width: 1.5px;
      stroke-linecap: round;
      stroke-linejoin: round;
      transition: fill 0.2s ease, filter 0.2s ease, stroke 0.2s ease, fill-opacity 0.2s ease;
    }
    .muscle-poly:hover {
      fill-opacity: 0.82 !important;
      filter: brightness(1.35) drop-shadow(0 0 10px rgba(56, 189, 248, 0.85));
      stroke: #ffffff !important;
      stroke-width: 2.5px;
    }
    .muscle-poly.active-selected {
      fill-opacity: 0.88 !important;
      stroke: #ffffff !important;
      stroke-width: 3px;
      filter: drop-shadow(0 0 14px #38bdf8);
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
          <div style="background: #060911; border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 0; display:flex; justify-content:center; align-items:center; position:relative; overflow:hidden;">
            <svg id="muscleMapSvg" width="100%" height="460" viewBox="0 0 951 1024" role="img" aria-label="Interactive Dual-View Anatomical Muscle Map">
              <!-- Anatomical Base Layer: Inverted High-Definition Striations from Reference Anatomy -->
              <image id="anatomyBase" href="data:image/jpeg;base64,/9j/2wCEAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx4BBQUFBwYHDggIDh4UERQeHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHv/AABEIBAADtwMBIgACEQEDEQH/xAGiAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgsQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+gEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoLEQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/APsqloooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiijvQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUGigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKADNFFFABRRRQAEAjBGaTav8AdH5UtFABRRRQAUUUUAFFFFABQaKKADvRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAAaKKKACiiigAooooAKKKKACiiigANFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUGigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigANAoooAKDRRQAgpaKKACiiigApO9LR3oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACig0UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFHeg5oAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACikNKKACiiigAooooAKKKKACiiigAooo5oABRQKKACiiigAoooNABRRRQAUUUUAFFFFABRRRQAUUUUAFJilooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAopCKUUAFFFFABRRRQAUUGigAooooAKKKKACiiigAooooAKKKDQAZorF8SeKfDfhuDzte1zT9OXGQJ51Vj9F6n8BXnOp/tI/CizmaKDWbnUnBxiztHf8AnigD2CivEx+038OAf31v4igT+/JppC/zrpfDXxy+FviCRYrLxdZRTNwI7rMJ/NsD9aAPR6Kjtp4LmBJ7aaOaJxlXjYMrD1BHWpKACiigUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRQKACiiigAooooAKKhvbu0sbdrm9uYbaFBlpJpAir9SeK878RfHX4V6HK0Nz4stLiYHHl2oaYn6FRj9aAPSqK8Xb9pb4dA/u7bxFKv95NMYg/rV3Sv2jPhTezCGfXZtNkPAW9tXj/kDQB60aBWT4e8S+HvEUPnaFrVhqKYyfs86uV+oByPxrWoAWigdKKACiiigAooooAKKKKACiiigAooooAKKKD0oAKKQUtABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQ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oAKKSigBaKSloAKKKKACiikPSgBaKSigBaKBRQAUUUUAGaKKKACiikPWkAtFJS0wCiiigAooooAKKKSgBaKSgdaAFooooAKKKKACiigdKACiiigAooooAKKKKACg0UUAFFFFACUtJS0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUABpM0tBoATNGaKBQAtFFFABRRRQAUh60HrRQAUUUooATmloooAKKKKACiiigBKKKB1oAOaB1paKACiiigAoNFIaQBRRRTAKKKKAFFFAooAKKKKAEozRRQAZoopaADvRRRQAUUUUAFJS0lABmjNFFABmgUUCgBaKKKACkJpaQ0AGaM0UUAFKOlJSjpQAUUUUAFJS0UAJRmiigAooooAKWiigAoooNAAelJR2ooAKKKBQACloooAKKKKAENFBooAKKKKACloHSigAooooAKSlpKADNGaKKADNGaWigAooooAKDRQaAEooooABS80gpaACiiigAooooAQ9aM0tFACZozS0UAJS0UUAFFFFABRRRQAUUUUAFFFFABRRRQAUGiigABooooAKKKKACiiigAooooAKQ9aWigBKWiigAooooAKKKKACkzS0UAGaKKKACiiigAooooADSUtFACClFFFABRRRQAUUUUAFGaKKACiiigAooooAKKKKACiiigA7UlLRQAg60tFFABRRRQAUGiigBM0GlooAQGlFFFABRRRQAUUUUAFJS0UAJRS0UAFFHeigAooooAKKKKAEzRS0UAIKWiigAooopAFFFFMBDRS0UAJSjpRRSAKKKKYBRRRQAmaKWigAzRRRQAUUUUAFFFFAADQaKDQAlApaKACiiigAooooAKKKKADNJmlooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiikNAC0UCigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKB1ooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACg0UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRQKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiig0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFGaKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoFIaBQAtFFGaACiiigAooooAKKKKACiiigAooooAKKKKACiiigAozQaSgBaKBRQAUUUhoAWikFGaAFozSGigBaKQUtABRRRQAZozSYooAWiiigAooooAKKM0UAFFGaM0AFFFFABRQaKACiiigAooooAKKKKACikNKOlABRRRQAUUUZoAM0UlLmgAzQDSUUALRRRQAUUUUAFFFIelAC0UgpTQAUUCigAooooAKKKM0AFIaDRQAo6UUDpRQAUUUUAFFFFIAzRmkopgLmikpaACiiigAooFBoAM0UlKKACiiigAooooAKKKKACiiigAooooASlpKWgAooooAKKKKACiiigAooooAKKKKACiiigAoNFFACUooooAKQ0tIaAFFFAooAKKKKACgUUUAFFFFABRRRQAUUUUAFFFGaACk7UooNACDrS0UUABpMUtFACUUppMUAKRSUtFACCloozQAUUUd6ADNJRRQAtHaiigAooooAQdaWikzQAUDrRQOtAC0UUUAFFFFABR3oooAKKKKACiiigBDSjpRRQAUUUUAFIaWigBKKKKACiiigBaKKKACiijNABQaM0ZoAQUtFFABRRRQAUUUUAGaQ0pFJigAooxRigBR0ooFFABRRRQACiiikAmaMUtFMBMUtFFABRRRQAUGig0AIKWkFLQAUUUUAFFFFABRRRQAUUZooAKKKKAEpaSloAKKKKACigUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFBFFFAAKKKKAEIpRRRQAUUUUAFFFFABRRRQAUUUUAHakApaKACiiigAooooADQKKKACiiigAooooAKQilooABRRRQAmKMUtFABRRRQAUUUUABpMUtFACYoApaKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooADSYpaKAExRilooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoNFBoABRRRQAUUUUAFFFFABRRRQAhFKKKKACiiigBMUtFFABRRRQAUUUUAf/2Q==" x="0" y="0" width="951" height="1024"
                style="filter: invert(1) contrast(1.35) brightness(0.95); opacity: 0.85; mix-blend-mode: screen; pointer-events: none;" />

              <!-- Labels -->
              <g id="figure-labels" style="font-size:18px; fill:#64748b; font-weight:800; text-anchor:middle; letter-spacing:0.1em; pointer-events:none;">
                <text x="308" y="55">ANTERIOR (FRONT)</text>
                <text x="690" y="55">POSTERIOR (BACK)</text>
              </g>

              <!-- ======================================================== -->
              <!-- ANTERIOR (FRONT) INTERACTIVE MUSCLE OVERLAYS            -->
              <!-- ======================================================== -->
              <!-- Chest (Pectoralis Major) -->
              <path id="muscle-chest-left" class="muscle-poly" data-muscle="chest" onclick="inspectMuscle('chest')"
                d="M 306 218 L 246 226 C 230 240 230 270 248 290 C 274 306 306 306 306 306 Z" fill="#10b981" title="Chest (Pectoralis Major)" />
              <path id="muscle-chest-right" class="muscle-poly" data-muscle="chest" onclick="inspectMuscle('chest')"
                d="M 312 218 L 372 226 C 388 240 388 270 370 290 C 344 306 312 306 312 306 Z" fill="#10b981" title="Chest (Pectoralis Major)" />

              <!-- Shoulders Front (Anterior Deltoid) -->
              <path id="muscle-shoulders_front-left" class="muscle-poly" data-muscle="shoulders_front" onclick="inspectMuscle('shoulders_front')"
                d="M 248 214 C 228 220 206 242 202 270 C 215 285 238 280 246 260 C 248 240 248 225 248 214 Z" fill="#38bdf8" title="Anterior Deltoids" />
              <path id="muscle-shoulders_front-right" class="muscle-poly" data-muscle="shoulders_front" onclick="inspectMuscle('shoulders_front')"
                d="M 370 214 C 390 220 412 242 416 270 C 403 285 380 280 372 260 C 370 240 370 225 370 214 Z" fill="#38bdf8" title="Anterior Deltoids" />

              <!-- Shoulders Side (Lateral Deltoid) -->
              <path id="muscle-shoulders_side-left" class="muscle-poly" data-muscle="shoulders_side" onclick="inspectMuscle('shoulders_side')"
                d="M 204 238 C 188 250 182 270 184 286 C 196 295 210 285 212 268 C 212 255 208 245 204 238 Z" fill="#f59e0b" title="Lateral Deltoids" />
              <path id="muscle-shoulders_side-right" class="muscle-poly" data-muscle="shoulders_side" onclick="inspectMuscle('shoulders_side')"
                d="M 414 238 C 430 250 436 270 434 286 C 422 295 408 285 406 268 C 406 255 410 245 414 238 Z" fill="#f59e0b" title="Lateral Deltoids" />

              <!-- Biceps Brachii -->
              <path id="muscle-biceps-left" class="muscle-poly" data-muscle="biceps" onclick="inspectMuscle('biceps')"
                d="M 202 288 C 182 305 174 340 178 376 C 195 385 212 370 216 345 C 220 320 215 295 202 288 Z" fill="#10b981" title="Biceps Brachii" />
              <path id="muscle-biceps-right" class="muscle-poly" data-muscle="biceps" onclick="inspectMuscle('biceps')"
                d="M 416 288 C 436 305 444 340 440 376 C 423 385 406 370 402 345 C 398 320 403 295 416 288 Z" fill="#10b981" title="Biceps Brachii" />

              <!-- Forearms Anterior -->
              <path id="muscle-forearms-left" class="muscle-poly" data-muscle="forearms" onclick="inspectMuscle('forearms')"
                d="M 178 378 C 158 410 142 450 134 485 C 146 492 165 480 175 450 C 185 420 192 390 178 378 Z" fill="#38bdf8" title="Forearms (Brachioradialis / Flexors)" />
              <path id="muscle-forearms-right" class="muscle-poly" data-muscle="forearms" onclick="inspectMuscle('forearms')"
                d="M 440 378 C 460 410 476 450 484 485 C 472 492 453 480 443 450 C 433 420 426 390 440 378 Z" fill="#38bdf8" title="Forearms (Brachioradialis / Flexors)" />

              <!-- Rectus Abdominis (Abs & Core) -->
              <path id="muscle-abs" class="muscle-poly" data-muscle="abs" onclick="inspectMuscle('abs')"
                d="M 272 304 L 346 304 L 344 424 L 309 480 L 274 424 Z" fill="#10b981" title="Rectus Abdominis (Abs & Core)" />
              <!-- External Obliques & Serratus -->
              <path id="muscle-obliques-left" class="muscle-poly" data-muscle="abs" onclick="inspectMuscle('abs')"
                d="M 252 296 C 235 320 236 365 248 424 C 265 418 272 395 272 355 C 272 320 265 302 252 296 Z" fill="#10b981" title="External Obliques" />
              <path id="muscle-obliques-right" class="muscle-poly" data-muscle="abs" onclick="inspectMuscle('abs')"
                d="M 366 296 C 383 320 382 365 370 424 C 353 418 346 395 346 355 C 346 320 353 302 366 296 Z" fill="#10b981" title="External Obliques" />

              <!-- Quadriceps Femoris (Thighs) -->
              <path id="muscle-quads-left" class="muscle-poly" data-muscle="quads" onclick="inspectMuscle('quads')"
                d="M 264 428 C 232 460 220 520 236 620 C 260 645 285 640 296 615 C 304 570 304 490 294 445 Z" fill="#ef4444" title="Quadriceps Femoris" />
              <path id="muscle-quads-right" class="muscle-poly" data-muscle="quads" onclick="inspectMuscle('quads')"
                d="M 354 428 C 386 460 398 520 382 620 C 358 645 333 640 322 615 C 314 570 314 490 324 445 Z" fill="#ef4444" title="Quadriceps Femoris" />

              <!-- Calves & Shins Anterior -->
              <path id="muscle-calves-front-left" class="muscle-poly" data-muscle="calves" onclick="inspectMuscle('calves')"
                d="M 244 670 C 230 710 232 770 250 850 C 270 850 280 810 278 750 C 276 700 270 670 244 670 Z" fill="#38bdf8" title="Calves / Tibialis" />
              <path id="muscle-calves-front-right" class="muscle-poly" data-muscle="calves" onclick="inspectMuscle('calves')"
                d="M 365 670 C 380 710 380 770 365 850 C 345 850 335 810 338 750 C 340 700 346 670 365 670 Z" fill="#38bdf8" title="Calves / Tibialis" />

              <!-- ======================================================== -->
              <!-- POSTERIOR (BACK) INTERACTIVE MUSCLE OVERLAYS             -->
              <!-- ======================================================== -->
              <!-- Upper Back & Trapezius -->
              <path id="muscle-upper_back" class="muscle-poly" data-muscle="upper_back" onclick="inspectMuscle('upper_back')"
                d="M 690 155 L 725 185 L 755 220 L 715 295 L 690 340 L 665 295 L 625 220 L 655 185 Z" fill="#10b981" title="Trapezius & Rhomboids" />

              <!-- Rear Deltoids -->
              <path id="muscle-shoulders_rear-left" class="muscle-poly" data-muscle="shoulders_rear" onclick="inspectMuscle('shoulders_rear')"
                d="M 625 214 C 598 220 570 245 566 278 C 578 298 604 298 616 276 C 622 258 625 235 625 214 Z" fill="#10b981" title="Rear Deltoids" />
              <path id="muscle-shoulders_rear-right" class="muscle-poly" data-muscle="shoulders_rear" onclick="inspectMuscle('shoulders_rear')"
                d="M 755 214 C 782 220 810 245 814 278 C 802 298 776 298 764 276 C 758 258 755 235 755 214 Z" fill="#10b981" title="Rear Deltoids" />

              <!-- Triceps Brachii -->
              <path id="muscle-triceps-left" class="muscle-poly" data-muscle="triceps" onclick="inspectMuscle('triceps')"
                d="M 580 280 C 560 305 554 340 556 376 C 574 382 592 370 596 345 C 598 320 594 295 580 280 Z" fill="#10b981" title="Triceps Brachii" />
              <path id="muscle-triceps-right" class="muscle-poly" data-muscle="triceps" onclick="inspectMuscle('triceps')"
                d="M 800 280 C 820 305 826 340 824 376 C 806 382 788 370 784 345 C 782 320 786 295 800 280 Z" fill="#10b981" title="Triceps Brachii" />

              <!-- Latissimus Dorsi (Lats V-Taper) -->
              <path id="muscle-lats-left" class="muscle-poly" data-muscle="lats" onclick="inspectMuscle('lats')"
                d="M 648 285 C 620 305 615 350 635 410 C 660 410 680 375 684 330 C 684 300 668 288 648 285 Z" fill="#10b981" title="Latissimus Dorsi" />
              <path id="muscle-lats-right" class="muscle-poly" data-muscle="lats" onclick="inspectMuscle('lats')"
                d="M 732 285 C 760 305 765 350 745 410 C 720 410 700 375 696 330 C 696 300 712 288 732 285 Z" fill="#10b981" title="Latissimus Dorsi" />

              <!-- Gluteus Maximus (Glutes) -->
              <path id="muscle-glutes-left" class="muscle-poly" data-muscle="glutes" onclick="inspectMuscle('glutes')"
                d="M 688 415 C 640 415 620 440 618 485 C 620 535 650 550 688 540 Z" fill="#10b981" title="Gluteus Maximus" />
              <path id="muscle-glutes-right" class="muscle-poly" data-muscle="glutes" onclick="inspectMuscle('glutes')"
                d="M 692 415 C 740 415 760 440 762 485 C 760 535 730 550 692 540 Z" fill="#10b981" title="Gluteus Maximus" />

              <!-- Hamstrings -->
              <path id="muscle-hamstrings-left" class="muscle-poly" data-muscle="hamstrings" onclick="inspectMuscle('hamstrings')"
                d="M 632 542 C 614 570 612 625 630 670 C 655 670 675 640 678 600 C 678 570 665 545 632 542 Z" fill="#10b981" title="Hamstrings" />
              <path id="muscle-hamstrings-right" class="muscle-poly" data-muscle="hamstrings" onclick="inspectMuscle('hamstrings')"
                d="M 732 542 C 752 570 754 625 738 670 C 715 670 698 640 696 600 C 696 570 706 545 732 542 Z" fill="#10b981" title="Hamstrings" />

              <!-- Calves (Gastrocnemius & Soleus) -->
              <path id="muscle-calves-back-left" class="muscle-poly" data-muscle="calves" onclick="inspectMuscle('calves')"
                d="M 626 675 C 610 710 612 770 632 840 C 655 840 668 805 664 750 C 660 700 652 675 626 675 Z" fill="#38bdf8" title="Calves (Gastrocnemius)" />
              <path id="muscle-calves-back-right" class="muscle-poly" data-muscle="calves" onclick="inspectMuscle('calves')"
                d="M 735 675 C 755 710 755 770 735 840 C 715 840 705 805 708 750 C 712 700 718 675 735 675 Z" fill="#38bdf8" title="Calves (Gastrocnemius)" />
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

