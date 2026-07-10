"""
Hackalist API - 全球黑客松数据源
公开JSON API，无需爬虫
"""
import requests
from datetime import datetime

from .retry import retry_get
from .seed_data import make_id
from .saikr import guess_difficulty

API_URL = "https://hackalist.org/api/events"


def crawl_hackathons():
    """从 Hackalist 获取全球黑客松列表"""
    competitions = []

    try:
        resp = retry_get(API_URL, timeout=15)
        data = resp.json()

        for event in data:
            title = event.get("title", "")
            comp_id = make_id(title)
            start_date = event.get("startDate", "")
            end_date = event.get("endDate", "")

            competitions.append({
                "id": comp_id,
                "name": title,
                "category": "计算机类",
                "subcategory": ["黑客松"],
                "organizer": "",
                "location": {"province": "", "city": "", "display": event.get("location", "")},
                "timeline": {
                    "registrationStart": None,
                    "registrationDeadline": None,
                    "submissionDeadline": None,
                    "competitionDate": start_date if start_date else None,
                    "resultDate": end_date if end_date else None
                },
                "description": event.get("description", ""),
                "officialUrl": event.get("url", ""),
                "source": "Hackalist",
                "sourceVerified": False,
                "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
                "difficulty": guess_difficulty(title),
                "prize": "",
                "region": "",
                "status": "报名中" if event.get("isAccepting", False) else "未开始"
            })

        print(f"[Hackalist] 获取到 {len(competitions)} 条黑客松")

    except Exception as e:
        print(f"[Hackalist] 获取失败: {e}")

    return competitions


if __name__ == "__main__":
    data = crawl_hackathons()
    for item in data[:5]:
        print(item["name"], "-", item["location"]["display"])
