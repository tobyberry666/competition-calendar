"""DoraHacks 黑客松爬虫 - 全球Web3/AI黑客松"""
import requests
from datetime import datetime
from .categories import guess_category
from .retry import retry_get

def crawl_dorahacks():
    """从 DoraHacks GraphQL API 获取进行中的黑客松"""
    url = "https://api.dorahacks.com/graphql"
    query = {
        "query": """{ hackathons(orderBy:"created_at", orderDirection:"desc", first:20, where:{status:"active"}) { id title description url startDate endDate registrationDeadline status prizes { amount token } } }"""
    }
    competitions = []
    try:
        resp = requests.post(url, json=query, timeout=15)
        data = resp.json()
        for h in data.get("data", {}).get("hackathons", []):
            prize_str = ""
            if h.get("prizes"):
                amounts = [f"{p.get('amount',0)} {p.get('token','USD')}" for p in h["prizes"] if p.get("amount")]
                prize_str = ", ".join(amounts[:3]) if amounts else ""
            competitions.append({
                "title": h.get("title", ""),
                "url": f"https://dorahacks.io/hackathon/{h.get('url', '')}/buidl" if h.get("url") else "",
                "category": guess_category(h.get("title", "")),
                "source": "DoraHacks",
                "description": (h.get("description", "") or "")[:200],
                "status": "报名中" if h.get("status") == "active" else "未开始",
                "raw_time": f"{h.get('startDate', '')} - {h.get('endDate', '')}",
                "registration_deadline": None,
                "contest_start": None,
                "location": "线上",
                "prize": prize_str,
                "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        print(f"[DoraHacks] 获取到 {len(competitions)} 条黑客松")
    except Exception as e:
        print(f"[DoraHacks] 获取失败: {e}")
    return competitions
