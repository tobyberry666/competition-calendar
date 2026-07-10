"""Devpost 黑客松爬虫 - 全球最大黑客松平台"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .categories import guess_category
from .retry import retry_get
from .saikr import parse_date_from_text

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def crawl_devpost():
    """爬取 Devpost 进行中的黑客松"""
    url = "https://devpost.com/hackathons"
    competitions = []
    try:
        resp = retry_get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".hackathon-tile")
        for item in items[:20]:
            try:
                title_elem = item.select_one(".tile-title")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                link_elem = item.select_one("a")
                link = link_elem.get("href", "") if link_elem else ""
                if link and not link.startswith("http"):
                    link = "https://devpost.com" + link

                # Extract prize info
                prize_elem = item.select_one(".prize")
                prize = prize_elem.get_text(strip=True) if prize_elem else ""

                # Extract dates
                date_elems = item.select(".date")
                deadline = None
                start = None
                for de in date_elems:
                    text = de.get_text(strip=True)
                    if "deadline" in text.lower() or "截止" in text:
                        deadline = parse_date_from_text(text)
                    else:
                        start = parse_date_from_text(text)

                competitions.append({
                    "title": title,
                    "url": link,
                    "category": guess_category(title),
                    "source": "Devpost",
                    "description": "",
                    "status": "报名中",
                    "raw_time": "",
                    "registration_deadline": deadline,
                    "contest_start": start,
                    "location": "线上",
                    "prize": prize,
                    "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception:
                continue
        print(f"[Devpost] 获取到 {len(competitions)} 条黑客松")
    except Exception as e:
        print(f"[Devpost] 获取失败: {e}")
    return competitions
