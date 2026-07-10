"""
竞观 Compass 爬虫
官网：https://www.jingrace.com/
竞赛信息质量高，有含金量评级
"""
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

from .categories import guess_category
from .retry import retry_get

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9"
}


def parse_date(date_str):
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ["%Y.%m.%d", "%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str


def crawl_jingrace():
    """爬取竞观Compass竞赛列表"""
    url = "https://www.jingrace.com/"
    competitions = []

    try:
        resp = retry_get(url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        # 尝试多种选择器匹配竞赛卡片
        items = soup.select(".competition-card, .race-item, .contest-item, .card-item")

        # 如果没找到，尝试通用列表项
        if not items:
            items = soup.select("[class*=card]")

        for item in items[:30]:  # 限制数量避免抓到无关的
            try:
                title_elem = item.select_one("h2, h3, .title, a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                if len(title) < 4 or len(title) > 50:
                    continue

                link_elem = item.select_one("a")
                link = link_elem.get("href", "") if link_elem else ""
                if link and not link.startswith("http"):
                    link = "https://www.jingrace.com" + link

                # 提取所有文本
                all_text = item.get_text(" ", strip=True)

                competition = {
                    "title": title,
                    "url": link if link else "https://www.jingrace.com/",
                    "category": guess_category(title),
                    "source": "竞观Compass",
                    "description": all_text[:200] if all_text else "",
                    "status": "敬请关注",
                    "raw_time": "",
                    "registration_deadline": None,
                    "contest_start": None,
                    "location": None,
                    "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                competitions.append(competition)
            except Exception:
                continue

        print(f"[竞观Compass] 爬取到 {len(competitions)} 条")
        time.sleep(1)

    except Exception as e:
        print(f"[竞观Compass] 爬取失败: {e}")

    return competitions


if __name__ == "__main__":
    data = crawl_jingrace()
    for item in data[:5]:
        print(item["title"])
