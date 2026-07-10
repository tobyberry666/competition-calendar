"""
赛氪网爬虫 - 主数据源
覆盖各类大学生竞赛：计算机、创新创业、光电设计、外语等
"""
import re
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

from .categories import guess_category
from .retry import retry_get
from .seed_data import make_id

# 常见中国城市名（用于从标题/描述中提取地点）
COMMON_CITIES = [
    "北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都", "重庆", "天津",
    "苏州", "西安", "长沙", "沈阳", "青岛", "郑州", "大连", "厦门", "宁波", "济南",
    "哈尔滨", "长春", "福州", "昆明", "合肥", "南昌", "贵阳", "太原", "石家庄", "海口",
    "珠海", "东莞", "佛山", "无锡", "常州", "徐州", "温州", "南宁", "兰州", "银川",
    "乌鲁木齐", "呼和浩特", "拉萨", "西宁", "桂林", "三亚", "烟台", "威海", "扬州",
    "中山", "惠州", "嘉兴", "绍兴", "金华", "台州", "泉州", "漳州", "赣州", "九江",
    "芜湖", "洛阳", "开封", "咸阳", "宝鸡", "遵义", "桂林", "绵阳",
]

# 子分类映射：根据竞赛标题关键词确定 subcategory
CATEGORY_SUBCAT_MAP = {
    "ICPC": ["ICPC", "XCPC"],
    "CCPC": ["CCPC", "XCPC"],
    "蓝桥杯": ["蓝桥杯"],
    "天梯赛": ["天梯赛"],
    "数学建模": ["数学建模"],
    "信息安全": ["信息安全"],
    "电子设计": ["电子设计"],
    "光电": ["光电"],
    "机械": ["机械"],
    "机器人": ["机器人"],
    "互联网+": ["互联网+"],
    "挑战杯": ["挑战杯"],
    "创新创业": ["创新创业"],
    "计算机设计": ["计算机"],
    "英语": ["英语"],
    "翻译": ["翻译"],
    "化工": ["化工"],
    "市场调查": ["市场调查"],
    "电子商务": ["电子商务"],
    "CSP": ["CSP"],
    "数据挖掘": ["数据挖掘"],
    "人工智能": ["人工智能"],
    "智能制造": ["智能制造"],
    "商业": ["商业"],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9"
}


def guess_difficulty(title):
    """根据标题猜测竞赛难度"""
    if "ICPC" in title or "CCPC" in title:
        return "Advanced"
    if "蓝桥杯" in title or "天梯赛" in title:
        return "Beginner"
    return "Intermediate"


def guess_subcategory(title):
    """根据标题关键词确定 subcategory"""
    for kw, subcats in CATEGORY_SUBCAT_MAP.items():
        if kw in title:
            return subcats
    return []


def parse_date(date_str):
    """解析日期字符串，统一格式为 YYYY-MM-DD。支持日期范围，提取起始日期。"""
    if not date_str:
        return None
    date_str = date_str.strip()

    # 处理日期范围：取第一个日期
    # 支持分隔符: -, ~, ～, 至, 到
    range_separators = re.split(r'[-~～至到]', date_str)
    if len(range_separators) > 1:
        date_str = range_separators[0].strip()

    # 处理常见格式
    for fmt in ["%Y.%m.%d", "%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # 尝试匹配 M月D日 格式
    m = re.match(r'(\d{1,2})月(\d{1,2})日?', date_str)
    if m:
        month, day = int(m.group(1)), int(m.group(2))
        now = datetime.now()
        try:
            return datetime(now.year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            return date_str

    return date_str  # 解析失败返回原字符串


def parse_date_from_text(text):
    """从任意文本中用正则提取日期，返回第一个找到的日期（YYYY-MM-DD）"""
    if not text:
        return None
    text = text.strip()

    # 匹配 YYYY.MM.DD 或 YYYY-MM-DD 或 YYYY/MM/DD
    m = re.search(r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})', text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime(y, mo, d).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # 匹配 YYYY年M月D日
    m = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日?', text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime(y, mo, d).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # 匹配 M月D日（无年份，用当前年）
    m = re.search(r'(\d{1,2})月(\d{1,2})日?', text)
    if m:
        mo, d = int(m.group(1)), int(m.group(2))
        now = datetime.now()
        try:
            return datetime(now.year, mo, d).strftime("%Y-%m-%d")
        except ValueError:
            pass

    return None


def crawl_saikr_hot(page=1):
    """爬取赛氪热门竞赛列表"""
    url = f"https://www.saikr.com/vs?page={page}"
    competitions = []

    try:
        resp = retry_get(url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        items = soup.select(".item-list .item")
        for item in items:
            try:
                title_elem = item.select_one(".title a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = title_elem.get("href", "")
                if link and not link.startswith("http"):
                    link = "https://www.saikr.com" + link

                # 提取时间信息
                time_elem = item.select_one(".time")
                time_text = time_elem.get_text(strip=True) if time_elem else ""

                # 提取报名状态
                status_elem = item.select_one(".status")
                status = status_elem.get_text(strip=True) if status_elem else ""

                # 提取简介
                desc_elem = item.select_one(".desc")
                desc = desc_elem.get_text(strip=True) if desc_elem else ""

                # 从 raw_time 和 desc 中提取日期
                reg_deadline = None
                comp_date = None
                for field in [time_text, desc]:
                    date_found = parse_date_from_text(field)
                    if date_found:
                        if not reg_deadline:
                            reg_deadline = date_found
                        else:
                            comp_date = date_found
                            break

                subcats = guess_subcategory(title)
                comp_id = make_id(title)

                competition = {
                    "id": comp_id,
                    "name": title,
                    "category": guess_category(title),
                    "subcategory": subcats,
                    "organizer": "",
                    "location": {"province": "", "city": "", "display": ""},
                    "timeline": {
                        "registrationStart": None,
                        "registrationDeadline": reg_deadline,
                        "submissionDeadline": None,
                        "competitionDate": comp_date,
                        "resultDate": None
                    },
                    "description": desc,
                    "officialUrl": link,
                    "source": "赛氪",
                    "sourceVerified": False,
                    "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
                    "difficulty": guess_difficulty(title),
                    "prize": "",
                    "region": "",
                    "status": status
                }

                competitions.append(competition)
            except Exception as e:
                print(f"解析单个竞赛项失败: {e}")
                continue

        print(f"[赛氪] 第{page}页爬取到 {len(competitions)} 条竞赛")
        time.sleep(1)  # 礼貌延时

    except Exception as e:
        print(f"[赛氪] 爬取失败: {e}")

    return competitions


def crawl_saikr_detail(competition_url):
    """爬取竞赛详情页，获取更精确的报名截止时间、地点等"""
    try:
        resp = retry_get(competition_url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        detail = {}
        full_text = soup.get_text()

        # --- 提取报名截止时间 ---
        # 方式1：在标签附近找日期
        deadline_elem = soup.find(string=lambda t: t and "报名截止" in t)
        if deadline_elem:
            parent = deadline_elem.find_parent()
            if parent:
                detail["registrationDeadline"] = parse_date(parent.get_text(strip=True))

        # 方式2：用正则在全文中找"截止"附近的日期
        if not detail.get("registrationDeadline"):
            m = re.search(r'报名.{0,10}截止.{0,30}', full_text)
            if m:
                detail["registrationDeadline"] = parse_date_from_text(m.group(0))

        # --- 提取比赛时间 ---
        # 方式1：在标签附近找日期
        contest_time_elem = soup.find(string=lambda t: t and "比赛时间" in t)
        if contest_time_elem:
            parent = contest_time_elem.find_parent()
            if parent:
                detail["competitionDate"] = parse_date(parent.get_text(strip=True))

        # 方式2：用正则在全文中找"开始"/"比赛"附近的日期
        if not detail.get("competitionDate"):
            for keyword in ["开始", "比赛", "竞赛", "开赛"]:
                m = re.search(rf'{keyword}.{{0,30}}', full_text)
                if m:
                    date_found = parse_date_from_text(m.group(0))
                    if date_found:
                        detail["competitionDate"] = date_found
                        break

        # --- 提取举办地点 ---
        # 方式1：在标签附近找地点关键词
        for label in ["举办地点", "举办地址", "比赛地点", "活动地点", "竞赛地点"]:
            location_elem = soup.find(string=lambda t: t and label in t)
            if location_elem:
                parent = location_elem.find_parent()
                if parent:
                    loc_text = parent.get_text(strip=True)
                    for prefix in [label, "地点", "地址"]:
                        loc_text = loc_text.replace(prefix, "")
                    detail["location"] = loc_text.strip("：: ")
                    break

        # 方式2：在全文中找地点关键词附近的地址
        if not detail.get("location"):
            for keyword in ["地点", "地址", "举办地"]:
                m = re.search(rf'{keyword}[：:\s]{{0,5}}(.{{2,40}})', full_text)
                if m:
                    loc_text = m.group(1).strip()
                    # 截断到下一个标点或换行
                    loc_text = re.split(r'[。，；\n\r]', loc_text)[0].strip()
                    if loc_text and len(loc_text) >= 2:
                        detail["location"] = loc_text
                        break

        # 方式3：从标题或描述中提取城市名
        if not detail.get("location"):
            title_elem = soup.select_one("h1, .title, .competition-title")
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                for city in COMMON_CITIES:
                    if city in title_text:
                        detail["location"] = city
                        break

        time.sleep(0.5)
        return detail

    except Exception as e:
        print(f"[赛氪详情] 爬取失败 {competition_url}: {e}")
        return {}


def crawl_all(max_pages=3):
    """爬取多页竞赛，返回完整列表"""
    all_competitions = []
    for page in range(1, max_pages + 1):
        items = crawl_saikr_hot(page)
        all_competitions.extend(items)
        if not items:
            break

    # 去重
    seen = set()
    unique = []
    for comp in all_competitions:
        if comp["name"] not in seen:
            seen.add(comp["name"])
            unique.append(comp)

    print(f"[赛氪] 共爬取 {len(unique)} 条唯一竞赛")

    # 抓取详情页（限制前30条）
    detail_limit = min(30, len(unique))
    for i in range(detail_limit):
        comp = unique[i]
        url = comp.get("officialUrl")
        if not url:
            continue
        print(f"[赛氪] 正在获取详情 ({i+1}/{detail_limit})...")
        detail = crawl_saikr_detail(url)
        if detail:
            if detail.get("registrationDeadline"):
                comp["timeline"]["registrationDeadline"] = detail["registrationDeadline"]
            if detail.get("competitionDate"):
                comp["timeline"]["competitionDate"] = detail["competitionDate"]
            if detail.get("location"):
                comp["location"]["display"] = detail["location"]

    return unique


if __name__ == "__main__":
    data = crawl_all(2)
    print(json.dumps(data[:3], ensure_ascii=False, indent=2))
