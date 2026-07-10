"""
赛氪网爬虫 - 主数据源
覆盖各类大学生竞赛：计算机、创新创业、光电设计、外语等
"""
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

from categories import guess_category
from retry import retry_get

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9"
}


def parse_date(date_str):
    """解析日期字符串，统一格式为 YYYY-MM-DD"""
    if not date_str:
        return None
    date_str = date_str.strip()
    # 处理常见格式
    for fmt in ["%Y.%m.%d", "%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str  # 解析失败返回原字符串


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

                competition = {
                    "title": title,
                    "url": link,
                    "category": guess_category(title),
                    "source": "赛氪",
                    "description": desc,
                    "status": status,
                    "raw_time": time_text,
                    "registration_deadline": None,
                    "contest_start": None,
                    "location": None,
                    "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

        # 尝试提取报名截止时间
        deadline_elem = soup.find(string=lambda t: t and "报名截止" in t)
        if deadline_elem:
            parent = deadline_elem.find_parent()
            if parent:
                detail["registration_deadline"] = parse_date(parent.get_text(strip=True))

        # 尝试提取比赛时间
        contest_time_elem = soup.find(string=lambda t: t and "比赛时间" in t)
        if contest_time_elem:
            parent = contest_time_elem.find_parent()
            if parent:
                detail["contest_start"] = parse_date(parent.get_text(strip=True))

        # 尝试提取举办地点
        location_elem = soup.find(string=lambda t: t and "举办地点" in t)
        if location_elem:
            parent = location_elem.find_parent()
            if parent:
                detail["location"] = parent.get_text(strip=True).replace("举办地点", "").strip("：: ")

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
        if comp["title"] not in seen:
            seen.add(comp["title"])
            unique.append(comp)

    print(f"[赛氪] 共爬取 {len(unique)} 条唯一竞赛")
    return unique


if __name__ == "__main__":
    data = crawl_all(2)
    print(json.dumps(data[:3], ensure_ascii=False, indent=2))
