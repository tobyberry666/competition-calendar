// 竞赛日历前端逻辑
let allCompetitions = [];
let currentCategory = 'all';
let currentLocation = 'all';
let searchKeyword = '';
let currentView = 'list';
let currentCalendarDate = new Date();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    initEventListeners();
});

// 加载数据
async function loadData() {
    try {
        const response = await fetch('data.json?t=' + Date.now());
        const data = await response.json();

        allCompetitions = data.competitions || [];
        document.getElementById('updateTime').textContent = `最后更新：${data.updated_at}`;
        document.getElementById('totalCount').textContent = data.total;
        document.getElementById('categoryCount').textContent = Object.keys(data.categories || {}).length;

        renderCategoryButtons(data.categories || {});
        renderCurrentView();
    } catch (error) {
        console.error('加载数据失败:', error);
        document.getElementById('competitionList').innerHTML =
            '<div class="loading">数据加载失败，请确保已运行爬虫生成 data.json</div>';
    }
}

// 渲染分类按钮
function renderCategoryButtons(categories) {
    const container = document.getElementById('categoryButtons');
    container.innerHTML = '<button class="cat-btn active" data-category="all">全部</button>';

    for (const [cat, count] of Object.entries(categories)) {
        const btn = document.createElement('button');
        btn.className = 'cat-btn';
        btn.dataset.category = cat;
        btn.textContent = `${cat} (${count})`;
        container.appendChild(btn);
    }
}

// 初始化事件监听
function initEventListeners() {
    // 分类筛选
    document.getElementById('categoryButtons').addEventListener('click', (e) => {
        if (e.target.classList.contains('cat-btn')) {
            document.querySelectorAll('.cat-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            currentCategory = e.target.dataset.category;
            renderCurrentView();
        }
    });

    // 搜索
    document.getElementById('searchInput').addEventListener('input', (e) => {
        searchKeyword = e.target.value.trim().toLowerCase();
        renderCurrentView();
    });

    // 地区筛选
    document.getElementById('locationFilter').addEventListener('change', (e) => {
        currentLocation = e.target.value;
        renderCurrentView();
    });

    // 视图切换
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentView = btn.dataset.view;
            renderCurrentView();
        });
    });

    // 日历导航
    document.getElementById('prevMonth').addEventListener('click', () => {
        currentCalendarDate.setMonth(currentCalendarDate.getMonth() - 1);
        renderCalendar();
    });

    document.getElementById('nextMonth').addEventListener('click', () => {
        currentCalendarDate.setMonth(currentCalendarDate.getMonth() + 1);
        renderCalendar();
    });

    // ESC 关闭弹窗
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeDayPopup();
    });
}

// 过滤数据
function getFilteredList() {
    return allCompetitions.filter(comp => {
        // 分类过滤
        if (currentCategory !== 'all' && comp.category !== currentCategory) {
            return false;
        }
        // 关键词搜索
        if (searchKeyword && !comp.title.toLowerCase().includes(searchKeyword)) {
            return false;
        }
        // 地区过滤
        if (currentLocation !== 'all') {
            const loc = (comp.location || '').toLowerCase();
            if (currentLocation === '全国') {
                if (!loc.includes('全国') && loc !== '') return false;
            } else if (currentLocation === '线上') {
                if (!loc.includes('线上') && !loc.includes('远程') && !loc.includes('online')) return false;
            } else {
                if (!loc.includes(currentLocation.toLowerCase())) return false;
            }
        }
        return true;
    });
}

// 渲染当前视图
function renderCurrentView() {
    if (currentView === 'list') {
        document.getElementById('competitionList').style.display = 'flex';
        document.getElementById('calendarView').style.display = 'none';
        renderList();
    } else {
        document.getElementById('competitionList').style.display = 'none';
        document.getElementById('calendarView').style.display = 'block';
        renderCalendar();
    }
}

// 判断状态
function getStatusClass(status) {
    if (!status) return 'upcoming';
    if (status.includes('报名中') || status.includes('进行中') || status.includes('火热')) {
        return 'ongoing';
    }
    return 'upcoming';
}

// 渲染列表
function renderList() {
    const list = getFilteredList();
    const container = document.getElementById('competitionList');

    if (list.length === 0) {
        container.innerHTML = '<div class="loading">没有找到匹配的竞赛</div>';
        return;
    }

    container.innerHTML = list.map(comp => `
        <div class="competition-card">
            <div class="card-header">
                <a href="${comp.url}" target="_blank" class="card-title">${escapeHtml(comp.title)}</a>
                <span class="category-tag">${escapeHtml(comp.category || '其他')}</span>
            </div>
            <div class="card-meta">
                ${comp.registration_deadline ? `
                    <span class="meta-item deadline">
                        ⏰ 报名截止：${escapeHtml(comp.registration_deadline)}
                    </span>
                ` : ''}
                ${comp.contest_start ? `
                    <span class="meta-item">
                        📅 比赛时间：${escapeHtml(comp.contest_start)}
                    </span>
                ` : ''}
                ${comp.raw_time && !comp.contest_start ? `
                    <span class="meta-item">
                        📅 ${escapeHtml(comp.raw_time)}
                    </span>
                ` : ''}
                ${comp.location ? `
                    <span class="meta-item">
                        📍 ${escapeHtml(comp.location)}
                    </span>
                ` : ''}
            </div>
            ${comp.description ? `<p class="card-desc">${escapeHtml(comp.description)}</p>` : ''}
            <div class="card-footer">
                <span class="source-tag">来源：${escapeHtml(comp.source || '未知')}</span>
                <span class="status-tag ${getStatusClass(comp.status)}">${escapeHtml(comp.status || '敬请关注')}</span>
            </div>
        </div>
    `).join('');
}

// HTML转义
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========== 日历视图 ==========

// 解析日期字符串为Date对象
function parseDateStr(dateStr) {
    if (!dateStr) return null;
    try {
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return null;
        return d;
    } catch {
        return null;
    }
}

// 获取某天的所有竞赛
function getCompetitionsByDate(year, month, day) {
    const targetDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const list = getFilteredList();
    return list.filter(comp => {
        const d1 = parseDateStr(comp.registration_deadline);
        const d2 = parseDateStr(comp.contest_start);
        if (d1 && formatDate(d1) === targetDate) return true;
        if (d2 && formatDate(d2) === targetDate) return true;
        return false;
    });
}

function formatDate(d) {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

// 渲染日历
function renderCalendar() {
    const year = currentCalendarDate.getFullYear();
    const month = currentCalendarDate.getMonth();

    // 更新标题
    document.getElementById('currentMonthTitle').textContent = `${year}年${month + 1}月`;

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startWeekday = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1; // 周一为0
    const daysInMonth = lastDay.getDate();

    const today = new Date();
    const todayStr = formatDate(today);

    const grid = document.getElementById('calendarGrid');
    grid.innerHTML = '';

    // 上个月的填充天数
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = startWeekday - 1; i >= 0; i--) {
        const day = prevMonthLastDay - i;
        grid.appendChild(createDayCell(day, true, year, month - 1));
    }

    // 当月天数
    for (let day = 1; day <= daysInMonth; day++) {
        const isToday = formatDate(new Date(year, month, day)) === todayStr;
        grid.appendChild(createDayCell(day, false, year, month, isToday));
    }

    // 下个月填充
    const totalCells = startWeekday + daysInMonth;
    const remaining = (7 - (totalCells % 7)) % 7;
    for (let day = 1; day <= remaining; day++) {
        grid.appendChild(createDayCell(day, true, year, month + 1));
    }
}

function createDayCell(day, isOtherMonth, year, month, isToday = false) {
    const cell = document.createElement('div');
    cell.className = 'calendar-day';
    if (isOtherMonth) cell.classList.add('other-month');
    if (isToday) cell.classList.add('today');

    const dayNum = document.createElement('div');
    dayNum.className = 'cal-day-number';
    dayNum.textContent = day;
    cell.appendChild(dayNum);

    // 获取当天竞赛
    const events = getCompetitionsByDate(year, month, day);
    const displayEvents = events.slice(0, 2);
    const extraCount = events.length - 2;

    displayEvents.forEach(comp => {
        const eventEl = document.createElement('div');
        eventEl.className = 'cal-event';
        // 报名截止标红
        const deadlineDate = parseDateStr(comp.registration_deadline);
        if (deadlineDate && formatDate(deadlineDate) === formatDate(new Date(year, month, day))) {
            eventEl.classList.add('deadline');
        }
        eventEl.textContent = comp.title.length > 10 ? comp.title.substring(0, 10) + '...' : comp.title;
        eventEl.title = comp.title;
        cell.appendChild(eventEl);
    });

    if (extraCount > 0) {
        const moreEl = document.createElement('div');
        moreEl.className = 'cal-event more';
        moreEl.textContent = `+${extraCount} 更多`;
        cell.appendChild(moreEl);
    }

    // 点击日历格子弹出当日竞赛详情
    cell.addEventListener('click', () => {
        renderDayPopup(year, month, day);
    });

    return cell;
}

// 渲染当日竞赛弹窗
function renderDayPopup(year, month, day) {
    closeDayPopup();
    const events = getCompetitionsByDate(year, month, day);
    const dateStr = `${year}年${month + 1}月${day}日`;

    const overlay = document.createElement('div');
    overlay.className = 'day-popup-overlay';
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeDayPopup();
    });

    const popup = document.createElement('div');
    popup.className = 'day-popup';

    const header = document.createElement('div');
    header.className = 'day-popup-header';
    const title = document.createElement('span');
    title.textContent = dateStr;
    const closeBtn = document.createElement('button');
    closeBtn.className = 'day-close-btn';
    closeBtn.textContent = '✕';
    closeBtn.addEventListener('click', closeDayPopup);
    header.appendChild(title);
    header.appendChild(closeBtn);
    popup.appendChild(header);

    if (events.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'day-popup-item';
        empty.style.color = '#999';
        empty.textContent = '当天无竞赛';
        popup.appendChild(empty);
    } else {
        events.forEach(comp => {
            const item = document.createElement('div');
            item.className = 'day-popup-item';

            const tag = document.createElement('span');
            tag.className = 'category-tag';
            tag.textContent = comp.category || '其他';

            const link = document.createElement('a');
            link.href = comp.url;
            link.target = '_blank';
            link.textContent = comp.title;

            const status = document.createElement('span');
            status.className = `status-tag ${getStatusClass(comp.status)}`;
            status.textContent = comp.status || '敬请关注';

            const meta = document.createElement('div');
            meta.className = 'day-popup-item-meta';
            if (comp.registration_deadline) {
                const dl = document.createElement('span');
                dl.textContent = `报名截止：${comp.registration_deadline}`;
                meta.appendChild(dl);
            }
            if (comp.contest_start) {
                const cs = document.createElement('span');
                cs.textContent = `比赛时间：${comp.contest_start}`;
                meta.appendChild(cs);
            }
            if (comp.raw_time && !comp.contest_start) {
                const rt = document.createElement('span');
                rt.textContent = comp.raw_time;
                meta.appendChild(rt);
            }

            item.appendChild(tag);
            item.appendChild(link);
            item.appendChild(status);
            item.appendChild(meta);
            popup.appendChild(item);
        });
    }

    overlay.appendChild(popup);
    document.body.appendChild(overlay);
}

// 关闭当日竞赛弹窗
function closeDayPopup() {
    const existing = document.querySelector('.day-popup-overlay');
    if (existing) existing.remove();
}
