"""
我爱竞赛网爬虫 - 第二大聚合平台
官网：https://www.52jingsai.com
"""
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

from categories import guess_category
from retry import retry_get

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9"
}


def parse_date(date_str):
    """解析日期字符串"""
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ["%Y.%m.%d", "%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str


def crawl_52jingsai(page=1):
    """爬取我爱竞赛网竞赛列表"""
    url = f"https://www.52jingsai.com/portal.php?page={page}"
    competitions = []

    try:
        resp = retry_get(url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        items = soup.select(".xld .bbda")
        for item in items:
            try:
                title_elem = item.select_one(".xs3 a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = title_elem.get("href", "")
                if link and not link.startswith("http"):
                    link = "https://www.52jingsai.com/" + link

                # 提取分类
                cat_elem = item.select_one(".xg1 a")
                cat_text = cat_elem.get_text(strip=True) if cat_elem else ""

                # 提取时间
                time_elem = item.select_one(".time")
                time_text = time_elem.get_text(strip=True) if time_elem else ""

                # 提取简介
                desc_elem = item.select_one(".summery")
                desc = desc_elem.get_text(strip=True) if desc_elem else ""

                competition = {
                    "title": title,
                    "url": link,
                    "category": guess_category(title, [cat_text]),
                    "source": "我爱竞赛网",
                    "description": desc,
                    "status": "报名中" if "报名" in title or "报名" in desc else "敬请关注",
                    "raw_time": time_text,
                    "registration_deadline": None,
                    "contest_start": None,
                    "location": None,
                    "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                competitions.append(competition)
            except Exception as e:
                continue

        print(f"[我爱竞赛网] 第{page}页爬取到 {len(competitions)} 条")
        time.sleep(1)

    except Exception as e:
        print(f"[我爱竞赛网] 爬取失败: {e}")

    return competitions


def crawl_all(max_pages=3):
    """爬取多页"""
    all_competitions = []
    for page in range(1, max_pages + 1):
        items = crawl_52jingsai(page)
        all_competitions.extend(items)
        if not items:
            break
    return all_competitions


if __name__ == "__main__":
    data = crawl_all(2)
    print(f"共爬取 {len(data)} 条")
    for item in data[:3]:
        print(item["title"])
