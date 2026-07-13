# 🎯 竞赛日历 · 大学生竞赛信息收集

全网大学生竞赛信息一站聚合，**按最近截止日期排序**，每天早上 7 点自动更新。
**不管是计算机、算法竞赛，还是商科、外语、数学、设计类比赛，想打竞赛的同学都不用再到处找！**

> 受众面向所有专业：计算机 / 算法（ICPC、蓝桥杯）、创新创业（互联网+、挑战杯）、
> 商科金融（工行杯、正大杯·市场调查大赛）、外语（全国大学生英语竞赛）、
> 数学建模、广告设计（大广赛）、电子设计……通通能在这里找到。

## ✨ 功能特性

- 🤖 **全自动采集**：GitHub Actions 每天定时爬取，无需人工维护
- 📊 **权威母表 + 多源补充**：以**教育部 84 项白名单**为权威锚点（名称/主办天然准确），再叠加赛氪网、我爱竞赛网、竞观 Compass、ICPC、Hackalist、DoraHacks、Devpost、商科/文科专项等来源
- 🎯 **官网直采截止日期**：对白名单每个官网自动抓取报名截止 / 比赛日期（仅接受 2026–2028 年合法日期），失败则保留基础信息并标「待更新」，绝不丢条目
- 🧹 **智能去重 + 置信度**：模糊归一化合并同竞赛不同表述（正大杯↔市场调查等），并为每条标注置信度（官方认证 / 聚合匹配 / 待核实）
- 🏷️ **分类筛选**：计算机类、创新创业类、商科/金融、外语类、数学类、设计类、电子信息类等（与 crawlers 分类对齐）
- 🔍 **关键词搜索**：快速找到感兴趣的竞赛
- ⏰ **按截止日期排序**：首页与全部列表默认按报名截止时间升序，最近截止的排最前，不错过任何一场
- 🔥 **临近提醒**：单独标出「7 天内截止」「30 天内开始」的赛事
- ⭐ **收藏功能**：浏览器本地收藏，打造自己的赛季清单（localStorage，无需登录）
- 🆓 **零成本部署**：全靠 GitHub 免费额度，不需要服务器
- 📱 **响应式设计**：手机电脑都能看

## 📂 项目结构

```
competition-calendar/
├── crawlers/                  # 爬虫模块（9 个数据源 + 分类/重试/URL 校验 helper）
│   ├── __init__.py
│   ├── whitelist_84.py        # 教育部 84 项白名单（权威母表，sourceVerified + confidence=high）
│   ├── official_site_crawler.py  # 官网直采截止日期（requests 抓取 + 日期校验 + 优雅降级）
│   ├── dedup.py               # 模糊归一化去重 + 别名合并 + 置信度优先合并
│   ├── saikr.py              # 赛氪网（主数据源，最全，覆盖各学科）
│   ├── jingsai52.py          # 我爱竞赛网
│   ├── jingrace.py           # 竞观 Compass
│   ├── icpc.py               # ICPC 亚洲区域赛
│   ├── hackalist.py          # 全球黑客松 API
│   ├── dorahacks.py          # DoraHacks 黑客松
│   ├── devpost.py            # Devpost 黑客松
│   ├── business_liberal_arts.py  # 商科/文科专项爬虫（保底工行杯、正大杯等稳定进库）
│   ├── young_ai_conference.py  # 年轻AI线下大会（官网直采：Google Vibe-a-thon/小米黑客松/TRAE/CODING LADY/TapNow）
│   ├── seed_data.py          # 教育部白名单手写补充种子
│   ├── categories.py         # 统一竞赛分类映射（计算机/商科/外语/数学/设计…）
│   ├── retry.py              # 请求重试
│   └── url_validator.py      # 每日校验官网链接，失效自动搜索恢复
├── data/
│   └── competitions.json     # 爬取的原始数据（每日备份带日期）
├── frontend/                  # 前端页面（原生 HTML/CSS/JS，无框架）
│   ├── index.html            # 主页面
│   ├── style.css             # 暗色主题样式
│   ├── app.js                # 筛选/搜索/排序/收藏/详情逻辑
│   └── data.json             # 前端使用的数据（由 main.py 生成）
├── .github/
│   └── workflows/
│       └── daily-update.yml  # GitHub Actions 每日自动更新 + 部署 Pages
├── main.py                    # 爬虫调度主入口（合并、去重、按截止排序、备份）
├── requirements.txt           # Python 依赖
├── 启动预览.bat               # Windows 一键本地预览
├── LICENSE                    # MIT 许可证
└── README.md
```

## 🚀 快速开始

### 本地预览

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行爬虫（可选，已有示例数据）
python main.py

# 3. 启动本地服务器
cd frontend
python -m http.server 8000

# 4. 浏览器打开 http://localhost:8000
```

Windows 用户直接双击 `启动预览.bat` 即可。

### 部署到 GitHub Pages（公开网站）

1. **创建 GitHub 仓库**，把本项目代码 push 上去
2. **开启 GitHub Pages**：
   - 仓库 Settings → Pages
   - Source 选择 **GitHub Actions**
3. **手动触发一次**：
   - 仓库 Actions → 每日竞赛数据更新 → Run workflow
4. **等待部署完成**，访问地址：`https://你的用户名.github.io/仓库名/`

之后**每天早上 7 点（北京时间）自动更新**，完全不用管。

## 📋 支持的数据源

| 数据源 | 覆盖范围 | 类型 | 优先级 |
|--------|---------|------|--------|
| 教育部白名单 | 84 项官方权威竞赛 | 种子数据 | ⭐⭐⭐⭐⭐ |
| 赛氪网 | 国内各类大学生竞赛（最全，含商科/文科） | 网页爬虫 | ⭐⭐⭐⭐⭐ |
| 我爱竞赛网 | 国内第二大竞赛聚合平台 | 网页爬虫 | ⭐⭐⭐⭐ |
| 竞观 Compass | 精选竞赛，有含金量评级 | 网页爬虫 | ⭐⭐⭐ |
| ICPC 北京总部 | ICPC/CCPC 算法竞赛 | 网页爬虫 | ⭐⭐⭐⭐ |
| Hackalist | 全球黑客松活动 | 公开 API | ⭐⭐⭐ |
| DoraHacks | 全球黑客松活动 | 公开 API | ⭐⭐⭐ |
| Devpost | 全球黑客松活动 | 公开 API | ⭐⭐⭐ |
| 商科/文科专项 | 工行杯、正大杯·市调、大广赛、外研社杯等（保底清单 + 实时补充） | 保底清单 + 网页爬虫 | ⭐⭐⭐⭐⭐ |
| 年轻AI线下大会 | Google Vibe-a-thon / 小米黑客松 / TRAE AI创造力 / CODING LADY女性黑客松 / TapNow全球AI影视 / 抖音AI创变者计划黑客松联赛（官网直采 + 核实日期兜底） | 官网直采爬虫 | ⭐⭐⭐⭐ |

## 🔧 添加新的数据源

在 `crawlers/` 目录下新建一个 Python 文件，实现一个返回列表的函数：

```python
from datetime import datetime

def crawl_xxx():
    competitions = []
    # ... 爬取逻辑 ...
    competitions.append({
        "title": "竞赛名称",
        "url": "官方链接",
        "category": "分类（计算机类/创新创业类/商科类/外语类/...）",
        "source": "数据源名称",
        "description": "简介",
        "status": "报名状态",
        "registration_deadline": "报名截止日期 YYYY-MM-DD",
        "contest_start": "比赛开始日期 YYYY-MM-DD",
        "location": "举办地点",
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return competitions
```

然后在 `main.py` 中导入并加入调度即可。若竞赛分类无法自动识别，可在 `crawlers/categories.py` 的 `MASTER_CATEGORY_MAP` 中补充关键词。

## ⚙️ 自定义更新时间

修改 `.github/workflows/daily-update.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: "0 23 * * *"  # UTC 时间，北京时间 +8 小时
```

常用时间对照：
- 北京时间 7:00 = UTC 23:00 → `0 23 * * *`
- 北京时间 9:00 = UTC 1:00 → `0 1 * * *`
- 北京时间 8:30 = UTC 0:30 → `30 0 * * *`

## 🛠️ 爬虫维护指南

### 常见问题

**Q: 某个数据源爬不到了怎么办？**
A: 大概率是网站改版了，改一下对应的 CSS 选择器就行，一般 5 分钟搞定。

**Q: 怎么知道爬虫挂了？**
A: GitHub Actions 跑失败了会发邮件通知你。

**Q: 爬虫挂了网站会崩吗？**
A: 不会，网站显示上一次成功的数据，只是不更新而已。

### 数据量少怎么办？

1. **白名单已兜底**：教育部 84 项白名单是权威母表，即使所有聚合站都爬不到，也能保证 84 条核心竞赛稳定在线。
2. 增加爬虫的翻页数量（`max_pages` 参数）
3. 添加更多数据源
4. 检查是不是被反爬了，加个延时或换 headers

## ⚠️ 免责声明

- 本项目仅供学习交流使用
- 竞赛信息以官方发布为准，报名前请务必核实官方信息
- 爬虫请遵守目标网站的 robots.txt，合理控制请求频率
- 请勿用于商业用途

## 📄 License

[MIT](LICENSE) —— 详见仓库根目录 `LICENSE` 文件。
