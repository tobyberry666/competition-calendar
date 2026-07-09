# 🎯 大学生竞赛日历

全网大学生竞赛信息一站聚合，每天早上7点自动更新。
**让想打竞赛的同学不用再到处找！**

## ✨ 功能特性

- 🤖 **全自动采集**：GitHub Actions 每天定时爬取，无需人工维护
- 📊 **6大数据源**：赛氪网、我爱竞赛网、竞观、ICPC、Hackalist、教育部白名单
- 🏷️ **分类筛选**：计算机类、创新创业类、电子信息类、数学类等10+分类
- 📅 **双视图模式**：列表视图 + 日历视图，一目了然
- 🔍 **关键词搜索**：快速找到感兴趣的竞赛
- ⏰ **报名截止提醒**：按截止时间排序，不错过重要赛事
- 🆓 **零成本部署**：全靠 GitHub 免费额度，不需要服务器
- 📱 **响应式设计**：手机电脑都能看

## 📂 项目结构

```
competition-calendar/
├── crawlers/                  # 爬虫模块（6个数据源）
│   ├── __init__.py
│   ├── saikr.py              # 赛氪网（主数据源，最全）
│   ├── jingsai52.py          # 我爱竞赛网
│   ├── jingrace.py           # 竞观 Compass
│   ├── icpc.py               # ICPC 亚洲区域赛
│   ├── hackalist.py          # 全球黑客松 API
│   └── seed_data.py          # 教育部白名单种子数据
├── data/
│   └── competitions.json     # 爬取的原始数据
├── frontend/                  # 前端页面
│   ├── index.html            # 主页面（列表+日历双视图）
│   ├── style.css             # 渐变紫主题
│   ├── app.js                # 筛选/搜索/日历逻辑
│   └── data.json             # 前端使用的数据
├── .github/
│   └── workflows/
│       └── daily-update.yml  # GitHub Actions 每日自动更新
├── main.py                    # 爬虫调度主入口
├── requirements.txt           # Python 依赖
├── 启动预览.bat               # Windows 一键本地预览
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

之后**每天早上7点自动更新**，完全不用管。

## 📋 支持的数据源

| 数据源 | 覆盖范围 | 类型 | 优先级 |
|--------|---------|------|--------|
| 教育部白名单 | 84项官方权威竞赛 | 种子数据 | ⭐⭐⭐⭐⭐ |
| 赛氪网 | 国内各类大学生竞赛（最全） | 网页爬虫 | ⭐⭐⭐⭐⭐ |
| 我爱竞赛网 | 国内第二大竞赛聚合平台 | 网页爬虫 | ⭐⭐⭐⭐ |
| 竞观 Compass | 精选竞赛，有含金量评级 | 网页爬虫 | ⭐⭐⭐ |
| ICPC 北京总部 | ICPC/CCPC 算法竞赛 | 网页爬虫 | ⭐⭐⭐⭐ |
| Hackalist | 全球黑客松活动 | 公开 API | ⭐⭐⭐ |

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
        "category": "分类（计算机类/创新创业类/...）",
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

然后在 `main.py` 中导入并加入调度即可。

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
A: 大概率是网站改版了，改一下对应的 CSS 选择器就行，一般5分钟搞定。

**Q: 怎么知道爬虫挂了？**
A: GitHub Actions 跑失败了会发邮件通知你。

**Q: 爬虫挂了网站会崩吗？**
A: 不会，网站显示上一次成功的数据，只是不更新而已。

### 数据量少怎么办？

1. 增加爬虫的翻页数量（`max_pages` 参数）
2. 添加更多数据源
3. 检查是不是被反爬了，加个延时或换 headers

## ⚠️ 免责声明

- 本项目仅供学习交流使用
- 竞赛信息以官方发布为准，报名前请务必核实官方信息
- 爬虫请遵守目标网站的 robots.txt，合理控制请求频率
- 请勿用于商业用途

## 📄 License

MIT
