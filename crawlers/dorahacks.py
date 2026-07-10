"""DoraHacks 黑客松爬虫 - 全球Web3/AI黑客松"""
import requests
from datetime import datetime
from .categories import guess_category
from .retry import retry_get
from .seed_data import make_id
from .saikr import guess_difficulty, guess_subcategory

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

            title = h.get("title", "")
            comp_id = make_id(title)
            subcats = guess_subcategory(title)

            competitions.append({
                "id": comp_id,
                "name": title,
                "category": guess_category(title),
                "subcategory": subcats if subcats else ["黑客松"],
                "organizer": "",
                "location": {"province": "", "city": "", "display": "线上"},
                "timeline": {
                    "registrationStart": None,
                    "registrationDeadline": None,
                    "submissionDeadline": None,
                    "competitionDate": None,
                    "resultDate": None
                },
                "description": (h.get("description", "") or "")[:200],
                "officialUrl": f"https://dorahacks.io/hackathon/{h.get('url', '')}/buidl" if h.get("url") else "",
                "source": "DoraHacks",
                "sourceVerified": False,
                "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
                "difficulty": guess_difficulty(title),
                "prize": prize_str,
                "region": "",
                "status": "报名中" if h.get("status") == "active" else "未开始"
            })
        print(f"[DoraHacks] 获取到 {len(competitions)} 条黑客松")
    except Exception as e:
        print(f"[DoraHacks] 获取失败: {e}")
    return competitions
