"""
Hackalist API - 全球黑客松数据源
公开JSON API，无需爬虫
"""
import requests
from datetime import datetime

from retry import retry_get

API_URL = "https://hackalist.org/api/events"


def crawl_hackathons():
    """从 Hackalist 获取全球黑客松列表"""
    competitions = []

    try:
        resp = retry_get(API_URL, timeout=15)
        data = resp.json()

        for event in data:
            competitions.append({
                "title": event.get("title", ""),
                "url": event.get("url", ""),
                "category": "计算机类",
                "source": "Hackalist",
                "description": event.get("description", ""),
                "status": "报名中" if event.get("isAccepting", False) else "未开始",
                "raw_time": f"{event.get('startDate', '')} - {event.get('endDate', '')}",
                "registration_deadline": None,
                "contest_start": event.get("startDate", ""),
                "location": event.get("location", ""),
                "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        print(f"[Hackalist] 获取到 {len(competitions)} 条黑客松")

    except Exception as e:
        print(f"[Hackalist] 获取失败: {e}")

    return competitions


if __name__ == "__main__":
    data = crawl_hackathons()
    for item in data[:5]:
        print(item["title"], "-", item["location"])
