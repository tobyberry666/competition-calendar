// XCPC Navigator — SPA with hash routing
(function () {
    'use strict';

    let allCompetitions = [];
    let favorites = JSON.parse(localStorage.getItem('xcpc_favorites') || '[]');
    let countdownTimer = null;

    const TYPE_TABS = [
        { key: 'all', label: '全部' },
        { key: 'icpc', label: 'ICPC/CCPC' },
        { key: 'lanqiao', label: '蓝桥杯' },
        { key: 'math', label: '数学建模' },
        { key: 'innovation', label: '创新创业' },
        { key: 'other', label: '其他' }
    ];

    const DIFFICULTIES = ['全部', '入门', '中级', '高级'];

    const TIME_RANGES = [
        { key: 'all', label: '全部' },
        { key: 'week', label: '本周' },
        { key: 'month', label: '本月' },
        { key: 'quarter', label: '未来三个月' }
    ];

    const CITIES = [
        '全国', '线上',
        '北京', '上海', '广州', '深圳', '成都', '杭州', '南京', '武汉',
        '西安', '重庆', '天津', '长沙', '郑州', '苏州', '厦门', '青岛',
        '大连', '哈尔滨', '沈阳', '济南', '合肥', '福州', '昆明', '贵阳',
        '兰州', '太原', '石家庄', '长春', '南昌', '南宁', '海口', '银川',
        '西宁', '呼和浩特', '乌鲁木齐', '拉萨'
    ];

    // ── Init ──
    document.addEventListener('DOMContentLoaded', () => {
        loadData();
        window.addEventListener('hashchange', route);
        route();
    });

    async function loadData() {
        try {
            const res = await fetch('data.json?t=' + Date.now());
            const data = await res.json();
            allCompetitions = data.competitions || data || [];
            // Normalize: ensure array of objects with required fields
            if (Array.isArray(allCompetitions)) {
                allCompetitions = allCompetitions.map(c => ({
                    ...c,
                    subcategory: c.subcategory || [],
                    timeline: c.timeline || {},
                    location: c.location || {}
                }));
            }
        } catch (e) {
            console.error('Failed to load data:', e);
            allCompetitions = [];
        }
    }

    // ── Routing ──
    function route() {
        clearCountdown();
        const hash = location.hash || '#/';
        const app = document.getElementById('app');

        // Update nav active
        document.querySelectorAll('.nav-link').forEach(el => {
            el.classList.toggle('active', el.getAttribute('href') === hash || el.getAttribute('href') === hash.split('/').slice(0, 2).join('/'));
        });

        if (hash === '#/' || hash === '#' || hash === '') {
            renderDashboard(app);
        } else if (hash === '#/all') {
            renderAll(app);
        } else if (hash === '#/favorites') {
            renderFavorites(app);
        } else if (hash.startsWith('#/detail/')) {
            const id = decodeURIComponent(hash.replace('#/detail/', ''));
            renderDetail(app, id);
        } else {
            renderDashboard(app);
        }
        window.scrollTo(0, 0);
    }

    // ── Helpers ──
    function today() { return new Date(); }

    function daysBetween(a, b) {
        const msPerDay = 86400000;
        const utcA = Date.UTC(a.getFullYear(), a.getMonth(), a.getDate());
        const utcB = Date.UTC(b.getFullYear(), b.getMonth(), b.getDate());
        return Math.floor((utcB - utcA) / msPerDay);
    }

    function parseDate(str) {
        if (!str) return null;
        const d = new Date(str);
        return isNaN(d.getTime()) ? null : d;
    }

    function formatDate(str) {
        const d = parseDate(str);
        if (!d) return str || '';
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    }

    function countdownText(deadline) {
        const d = parseDate(deadline);
        if (!d) return null;
        const now = today();
        const diffMs = d.getTime() - now.getTime();
        if (diffMs < 0) return { text: '已截止', urgent: true, days: -1 };
        const days = Math.floor(diffMs / 86400000);
        const hours = Math.floor((diffMs % 86400000) / 3600000);
        if (days > 0) return { text: `还有${days}天${hours}时`, urgent: days < 3, warning: days < 7, days };
        return { text: `还有${hours}时`, urgent: true, days: 0 };
    }

    function isFavorited(id) {
        return favorites.includes(id);
    }

    function toggleFavorite(e, id) {
        e.stopPropagation();
        if (isFavorited(id)) {
            favorites = favorites.filter(f => f !== id);
        } else {
            favorites.push(id);
        }
        localStorage.setItem('xcpc_favorites', JSON.stringify(favorites));
        route();
    }

    function matchType(comp) {
        const subs = (comp.subcategory || []).map(s => s.toLowerCase());
        const name = (comp.name || '').toLowerCase();
        const cat = (comp.category || '').toLowerCase();
        return subs.some(s => s.includes('icpc') || s.includes('ccpc')) ||
               name.includes('icpc') || name.includes('ccpc') || cat.includes('icpc');
    }

    function matchLanqiao(comp) {
        const name = (comp.name || '').toLowerCase();
        return name.includes('蓝桥杯');
    }

    function matchMath(comp) {
        const name = (comp.name || '').toLowerCase();
        return name.includes('数学建模') || name.includes('math');
    }

    function matchInnovation(comp) {
        const name = (comp.name || '').toLowerCase();
        const cat = (comp.category || '').toLowerCase();
        return name.includes('互联网+') || name.includes('创新创业') || name.includes('挑战杯') ||
               cat.includes('创新创业');
    }

    function getFiltered(typeKey, difficulty, timeRange, search, city) {
        return allCompetitions.filter(comp => {
            // Type filter
            if (typeKey !== 'all') {
                if (typeKey === 'icpc' && !matchType(comp)) return false;
                if (typeKey === 'lanqiao' && !matchLanqiao(comp)) return false;
                if (typeKey === 'math' && !matchMath(comp)) return false;
                if (typeKey === 'innovation' && !matchInnovation(comp)) return false;
                if (typeKey === 'other') {
                    if (matchType(comp) || matchLanqiao(comp) || matchMath(comp) || matchInnovation(comp)) return false;
                }
            }
            // Difficulty
            if (difficulty !== '全部' && comp.difficulty !== difficulty) return false;
            // Search
            if (search && !(comp.name || '').toLowerCase().includes(search.toLowerCase())) return false;
            // City
            if (city !== '全国') {
                const loc = comp.location || {};
                const display = (loc.display || '').toLowerCase();
                const c = (loc.city || '').toLowerCase();
                const p = (loc.province || '').toLowerCase();
                if (city === '线上') {
                    if (!display.includes('线上') && !display.includes('远程')) return false;
                } else {
                    if (!c.includes(city.toLowerCase()) && !p.includes(city.toLowerCase()) && !display.includes(city.toLowerCase())) return false;
                }
            }
            // Time range
            if (timeRange !== 'all') {
                const now = today();
                const deadline = parseDate(comp.timeline && comp.timeline.competitionDate);
                if (!deadline) {
                    // If no date, only include in 'all'
                    if (timeRange !== 'all') return false;
                } else {
                    if (timeRange === 'week' && daysBetween(now, deadline) > 7) return false;
                    if (timeRange === 'month' && daysBetween(now, deadline) > 30) return false;
                    if (timeRange === 'quarter' && daysBetween(now, deadline) > 90) return false;
                }
            }
            return true;
        });
    }

    function renderCard(comp) {
        const cd = countdownText(comp.timeline && comp.timeline.registrationDeadline);
        const tags = [];
        if (comp.category) tags.push(`<span class="tag tag-category">${esc(comp.category)}</span>`);
        if (comp.difficulty) tags.push(`<span class="tag tag-difficulty-${comp.difficulty}">${esc(comp.difficulty)}</span>`);
        (comp.subcategory || []).forEach(s => tags.push(`<span class="tag tag-sub">${esc(s)}</span>`));

        let countdownHtml = '';
        if (cd) {
            const cls = cd.urgent ? 'countdown-urgent' : cd.warning ? 'countdown-warning' : 'countdown-normal';
            countdownHtml = `<span class="countdown ${cls}">${esc(cd.text)}</span>`;
        }

        const favStar = isFavorited(comp.id) ? '⭐' : '☆';

        return `<div class="competition-card" onclick="location.hash='#/detail/${encodeURIComponent(comp.id)}'">
            <div class="card-top">
                <span class="card-name">${esc(comp.name || '未命名')}</span>
                ${tags.join('')}
                <button class="btn btn-outline" style="padding:2px 8px;font-size:0.7rem;min-width:auto;" onclick="window._toggleFav(event,'${esc(comp.id)}')">${favStar} 收藏</button>
            </div>
            <div class="card-meta">
                ${cd ? `<span>⏰ 报名截止：${esc(comp.timeline && comp.timeline.registrationDeadline || '')} ${countdownHtml}</span>` : ''}
                ${comp.timeline && comp.timeline.competitionDate ? `<span>📅 比赛：${esc(comp.timeline.competitionDate)}</span>` : ''}
                ${comp.location ? `<span>📍 ${esc(comp.location.display || comp.location.city || comp.location.province || '')}</span>` : ''}
                ${comp.source ? `<span>来源：${esc(comp.source)}</span>` : ''}
            </div>
        </div>`;
    }

    function esc(str) {
        if (!str) return '';
        const d = document.createElement('div');
        d.textContent = str;
        return d.innerHTML;
    }

    function startCountdownUpdates() {
        clearCountdown();
        countdownTimer = setInterval(() => {
            document.querySelectorAll('.countdown[data-deadline]').forEach(el => {
                const cd = countdownText(el.dataset.deadline);
                if (cd) {
                    el.textContent = cd.text;
                    el.className = 'countdown ' + (cd.urgent ? 'countdown-urgent' : cd.warning ? 'countdown-warning' : 'countdown-normal');
                }
            });
        }, 60000);
    }

    function clearCountdown() {
        if (countdownTimer) { clearInterval(countdownTimer); countdownTimer = null; }
    }

    // ── Dashboard ──
    function renderDashboard(app) {
        const now = today();
        const upcomingDeadline = allCompetitions.filter(c => {
            const d = parseDate(c.timeline && c.timeline.registrationDeadline);
            return d && daysBetween(now, d) >= 0 && daysBetween(now, d) <= 7;
        });
        const upcomingStart = allCompetitions.filter(c => {
            const d = parseDate(c.timeline && c.timeline.competitionDate);
            return d && daysBetween(now, d) >= 0 && daysBetween(now, d) <= 30;
        });
        const cats = new Set(allCompetitions.map(c => c.category).filter(Boolean));

        app.innerHTML = `
            <div class="dash-header">
                <div class="dash-title">&lt;XCPC Navigator/&gt;</div>
                <div class="dash-subtitle">中国大学生程序设计竞赛导航</div>
            </div>

            <div class="stats-bar">
                <div class="stat-item">
                    <span class="stat-value">${allCompetitions.length}</span>
                    <span class="stat-label">Total Competitions</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${upcomingDeadline.length}</span>
                    <span class="stat-label">7-day Deadlines</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${cats.size}</span>
                    <span class="stat-label">Categories</span>
                </div>
            </div>

            ${upcomingDeadline.length > 0 ? `
                <div class="section-header">
                    <span class="section-title">🔥 即将截止 (7天内)</span>
                    <span class="section-count">${upcomingDeadline.length}</span>
                </div>
                <div class="card-list">${upcomingDeadline.map(renderCard).join('')}</div>
            ` : ''}

            ${upcomingStart.length > 0 ? `
                <div class="section-header">
                    <span class="section-title">📅 即将开始 (30天内)</span>
                    <span class="section-count">${upcomingStart.length}</span>
                </div>
                <div class="card-list">${upcomingStart.map(renderCard).join('')}</div>
            ` : ''}

            <div class="section-header">
                <span class="section-title">📋 全部竞赛</span>
                <span class="section-count">${allCompetitions.length}</span>
            </div>
            ${renderFilterBar('all', '全部', 'all', '', '全部')}
            <div class="card-list" id="filteredCards">
                ${allCompetitions.slice(0, 50).map(renderCard).join('')}
            </div>
        `;

        bindFilters();
        startCountdownUpdates();
    }

    function renderFilterBar(typeKey, difficulty, timeRange, search, city) {
        return `<div class="filter-bar">
            <div class="filter-row">
                <span class="filter-label">Type</span>
                <div class="filter-tabs">
                    ${TYPE_TABS.map(t => `<button class="filter-tab ${t.key === typeKey ? 'active' : ''}" data-type="${t.key}">${t.label}</button>`).join('')}
                </div>
            </div>
            <div class="filter-row">
                <span class="filter-label">Difficulty</span>
                <select class="filter-select" id="filterDifficulty">
                    ${DIFFICULTIES.map(d => `<option ${d === difficulty ? 'selected' : ''}>${d}</option>`).join('')}
                </select>
                <span class="filter-label" style="margin-left:12px;">Time</span>
                <select class="filter-select" id="filterTime">
                    ${TIME_RANGES.map(t => `<option value="${t.key}" ${t.key === timeRange ? 'selected' : ''}>${t.label}</option>`).join('')}
                </select>
                <span class="filter-label" style="margin-left:12px;">City</span>
                <select class="filter-select" id="filterCity">
                    ${CITIES.map(c => `<option ${c === city ? 'selected' : ''}>${c}</option>`).join('')}
                </select>
            </div>
            <div class="filter-row">
                <input class="filter-input" id="filterSearch" placeholder="搜索竞赛名称..." value="${esc(search)}">
            </div>
        </div>`;
    }

    function bindFilters() {
        let currentType = 'all';

        document.querySelectorAll('.filter-tab[data-type]').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.filter-tab[data-type]').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                currentType = tab.dataset.type;
                applyFilters();
            });
        });

        ['filterDifficulty', 'filterTime', 'filterCity', 'filterSearch'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener(el.tagName === 'INPUT' ? 'input' : 'change', applyFilters);
            }
        });

        function applyFilters() {
            const typeKey = currentType;
            const diff = document.getElementById('filterDifficulty').value;
            const time = document.getElementById('filterTime').value;
            const search = document.getElementById('filterSearch').value.trim();
            const city = document.getElementById('filterCity').value;
            const filtered = getFiltered(typeKey, diff, time, search, city);
            const container = document.getElementById('filteredCards');
            if (container) {
                container.innerHTML = filtered.length > 0 ? filtered.map(renderCard).join('') : '<div class="empty-state"><div class="empty-state-text">没有匹配的竞赛</div></div>';
            }
        }
    }

    // ── All competitions page ──
    function renderAll(app) {
        app.innerHTML = `
            <div class="dash-header">
                <div class="dash-title">全部竞赛</div>
                <div class="dash-subtitle">共 ${allCompetitions.length} 项</div>
            </div>
            ${renderFilterBar('all', '全部', 'all', '', '全部')}
            <div class="card-list" id="filteredCards">
                ${allCompetitions.map(renderCard).join('')}
            </div>
        `;
        bindFilters();
        startCountdownUpdates();
    }

    // ── Favorites ──
    function renderFavorites(app) {
        const favComps = allCompetitions.filter(c => favorites.includes(c.id));
        if (favComps.length === 0) {
            app.innerHTML = `
                <div class="dash-header">
                    <div class="dash-title">⭐ 我的赛季</div>
                    <div class="dash-subtitle">收藏的竞赛</div>
                </div>
                <div class="empty-state">
                    <div class="empty-state-icon">☆</div>
                    <div class="empty-state-text">还没有收藏任何竞赛<br>点击卡片上的收藏按钮开始</div>
                </div>
            `;
            return;
        }
        app.innerHTML = `
            <div class="dash-header">
                <div class="dash-title">⭐ 我的赛季</div>
                <div class="dash-subtitle">已收藏 ${favComps.length} 项</div>
            </div>
            <div class="card-list">
                ${favComps.map(renderCard).join('')}
            </div>
        `;
        startCountdownUpdates();
    }

    // ── Detail page ──
    function renderDetail(app, id) {
        const comp = allCompetitions.find(c => c.id === id);
        if (!comp) {
            app.innerHTML = `<div class="empty-state"><div class="empty-state-text">竞赛未找到</div></div>`;
            return;
        }

        const tl = comp.timeline || {};
        const loc = comp.location || {};
        const favStar = isFavorited(comp.id) ? '⭐' : '☆';
        const favClass = isFavorited(comp.id) ? 'favorited' : '';

        const timelineHtml = renderTimeline(tl);
        const tags = [];
        if (comp.category) tags.push(`<span class="tag tag-category">${esc(comp.category)}</span>`);
        if (comp.difficulty) tags.push(`<span class="tag tag-difficulty-${comp.difficulty}">${esc(comp.difficulty)}</span>`);
        (comp.subcategory || []).forEach(s => tags.push(`<span class="tag tag-sub">${esc(s)}</span>`));

        app.innerHTML = `
            <div class="detail-page">
                <a href="#/" class="back-btn">← 返回</a>

                <div class="detail-title">${esc(comp.name || '未命名')}</div>
                <div class="detail-tags">${tags.join('')}</div>

                <div class="detail-actions">
                    ${comp.officialUrl ? `<a href="${esc(comp.officialUrl)}" target="_blank" class="btn btn-primary">🔗 官网</a>` : ''}
                    <button class="btn btn-outline ${favClass}" onclick="window._toggleFav(event,'${esc(comp.id)}')">${favStar} 收藏</button>
                </div>

                <div class="detail-grid">
                    <div class="detail-label">Organizer</div>
                    <div class="detail-value">${esc(comp.organizer || '未知')}</div>
                    <div class="detail-label">Location</div>
                    <div class="detail-value">${esc(loc.display || [loc.province, loc.city].filter(Boolean).join(' · ') || '未知')}</div>
                    <div class="detail-label">Source</div>
                    <div class="detail-value">${esc(comp.source || '未知')}${comp.sourceVerified ? ' ✓ 已验证' : ''}</div>
                    ${comp.prize ? `<div class="detail-label">Prize</div><div class="detail-value">${esc(comp.prize)}</div>` : ''}
                    ${comp.lastUpdated ? `<div class="detail-label">Updated</div><div class="detail-value">${esc(comp.lastUpdated)}</div>` : ''}
                </div>

                ${timelineHtml}

                ${comp.description ? `<div class="detail-description">${esc(comp.description)}</div>` : ''}
            </div>
        `;
    }

    function renderTimeline(tl) {
        const nodes = [];
        if (tl.registrationStart) nodes.push({ date: tl.registrationStart, label: '报名开始' });
        if (tl.registrationDeadline) nodes.push({ date: tl.registrationDeadline, label: '报名截止' });
        if (tl.competitionDate) nodes.push({ date: tl.competitionDate, label: '比赛日期' });
        if (tl.resultDate) nodes.push({ date: tl.resultDate, label: '结果公布' });

        if (nodes.length === 0) return '';

        const now = today();
        const dots = nodes.map(n => {
            const d = parseDate(n.date);
            let cls = '';
            if (d) {
                if (d < now) cls = 'past';
                else if (daysBetween(now, d) === 0) cls = 'current';
            }
            return `<div class="timeline-node">
                <div class="timeline-dot ${cls}"></div>
                <div class="timeline-date">${esc(n.date || '')}</div>
                <div class="timeline-label">${esc(n.label)}</div>
            </div>`;
        }).join('');

        return `<div class="timeline">
            <div class="timeline-title">Timeline</div>
            <div class="timeline-track">${dots}</div>
        </div>`;
    }

    // ── Global toggle favorite ──
    window._toggleFav = toggleFavorite;
})();
