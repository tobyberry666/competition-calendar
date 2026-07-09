"""
ICPC 亚洲区域赛爬虫
数据源：ICPC北京总部官网
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def crawl_icpc_regional():
    """爬取ICPC亚洲区域赛信息"""
    url = "https://icpc.pku.edu.cn/ssxx/index.htm"
    competitions = []

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        # 提取赛事列表
        rows = soup.select("table tr")
        for row in rows[1:]:  # 跳过表头
            cols = row.select("td")
            if len(cols) >= 3:
                location = cols[0].get_text(strip=True)
                date_text = cols[1].get_text(strip=True)
                link_elem = cols[0].select_one("a")
                link = link_elem.get("href", "") if link_elem else ""

                if location and date_text:
                    competitions.append({
                        "title": f"ICPC国际大学生程序设计竞赛亚洲区域赛（{location}站）",
                        "url": link if link.startswith("http") else f"https://icpc.pku.edu.cn{link}" if link else "https://icpc.pku.edu.cn",
                        "category": "计算机类",
                        "source": "ICPC北京总部",
                        "description": "ICPC亚洲区域赛，国际顶级大学生算法竞赛",
                        "status": "敬请关注",
                        "raw_time": date_text,
                        "registration_deadline": None,
                        "contest_start": date_text,
                        "location": location,
                        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

        print(f"[ICPC] 爬取到 {len(competitions)} 条区域赛信息")

    except Exception as e:
        print(f"[ICPC] 爬取失败: {e}")

    return competitions


if __name__ == "__main__":
    data = crawl_icpc_regional()
    for item in data:
        print(item["title"], "-", item["contest_start"])
