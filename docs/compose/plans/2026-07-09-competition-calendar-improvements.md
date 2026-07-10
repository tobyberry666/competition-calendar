# Competition Calendar Improvements Plan

> **For agentic workers:** Use compose:subagent to implement tasks in parallel.

**Goal:** Fix critical bugs and add missing features to the competition-calendar project.

**Architecture:** Independent fixes across crawlers, workflow, and frontend.

**Tech Stack:** Python (requests, BeautifulSoup), vanilla JS/HTML/CSS, GitHub Actions.

## Tasks

### Task 1: Fix GitHub Actions deploy (Critical)
- **Files:** `.github/workflows/daily-update.yml`
- **Change:** Add `environment: name: github-pages` to deploy job, fix missing deploy job `needs`

### Task 2: Call crawl_saikr_detail in crawl_all (Critical)
- **Files:** `crawlers/saikr.py`
- **Change:** In `crawl_all()`, iterate results and call `crawl_saikr_detail()` for each to fill registration_deadline, contest_start, location

### Task 3: Create unified categories module
- **Files:** Create `crawlers/categories.py`, modify `saikr.py`, `jingsai52.py`, `jingrace.py`
- **Change:** Extract all CATEGORY_MAP to shared module, standardize categories

### Task 4: Add retry to all crawlers
- **Files:** Create `crawlers/retry.py`, modify `saikr.py`, `jingsai52.py`, `jingrace.py`, `icpc.py`, `hackalist.py`
- **Change:** Add simple retry decorator for HTTP requests

### Task 5: Add SEO meta tags
- **Files:** `frontend/index.html`
- **Change:** Add meta description, keywords, Open Graph tags

### Task 6: Add calendar day click interaction
- **Files:** `frontend/app.js`, `frontend/style.css`
- **Change:** Show popup/modal with day's competitions when clicking a calendar day

### Task 7: Add data backup with timestamps
- **Files:** `main.py`
- **Change:** Save daily backup as `data/competitions-YYYY-MM-DD.json`, keep last 30 days
