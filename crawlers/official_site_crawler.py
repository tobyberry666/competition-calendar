"""
官网直采截止日期爬虫（"自动搜官网"的准确版）
- 输入：白名单竞赛列表（含 officialUrl，缺失则先尝试搜索发现）
- 对每个官网用 requests 抓取，结构化提取报名截止 / 比赛日期
- 日期合法性校验：仅接受 2026–2028 年且格式合法的日期
- 失败 / 无日期：保留白名单基础信息并标 status="待更新"，绝不丢弃条目
- 复用 saikr 的日期解析与 url_validator 的发现能力
"""
import re
import time
from datetime import datetime, date

from .retry import retry_get
from .saikr import parse_date, parse_date_from_text
from .url_validator import search_official_url, check_url

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 仅接受该范围内的年份，过滤掉过期/畸形日期
VALID_YEARS = {2026, 2027, 2028}


def _year_ok(d):
    if not d:
        return False
    m = re.match(r"(\d{4})-", d or "")
    if not m:
        return False
    return int(m.group(1)) in VALID_YEARS


def _derive_status(timeline):
    dates = [timeline.get(k) for k in ("registrationDeadline", "competitionDate") if timeline.get(k)]
    if not dates:
        return "待更新"
    earliest = min(dates)
    today = date.today()
    try:
        ed = datetime.strptime(earliest, "%Y-%m-%d").date()
    except ValueError:
        return "待更新"
    if ed < today:
        return "已截止"
    if (ed - today).days > 14:
        return "即将开始"
    return "报名中"


def extract_timeline(text):
    """从官网正文提取 (报名截止, 比赛日期)。优先标签邻近，其次正则。"""
    if not text:
        return None, None

    reg_deadline = None
    comp_date = None

    # 报名截止：标签邻近
    for label in ["报名截止", "报名截止日期", "截止报名", "投稿截止", "提交截止", "征稿截止"]:
        node = re.search(re.escape(label) + r"[:：\s]{0,6}([^\n;；]{0,40})", text)
        if node:
            d = parse_date(node.group(1).strip())
            if _year_ok(d):
                reg_deadline = d
                break

    # 报名截止：正则兜底
    if not reg_deadline:
        m = re.search(r"报名.{0,12}?截止.{0,4}?(\d{4}[.\-/年]\d{1,2}[.\-/月]\d{1,2}|(\d{1,2})月(\d{1,2})[日号]?)", text)
        if m:
            d = parse_date_from_text(m.group(0))
            if _year_ok(d):
                reg_deadline = d

    # 比赛 / 决赛日期
    for label in ["比赛时间", "竞赛时间", "决赛时间", "总决赛", "作品提交", "决赛日期"]:
        node = re.search(re.escape(label) + r"[:：\s]{0,6}([^\n;；]{0,40})", text)
        if node:
            d = parse_date(node.group(1).strip())
            if _year_ok(d):
                comp_date = d
                break

    if not comp_date:
        for kw in ["总决赛", "决赛", "竞赛时间", "比赛时间"]:
            m = re.search(kw + r".{0,30}?(\d{4}[.\-/年]\d{1,2}[.\-/月]\d{1,2}|(\d{1,2})月(\d{1,2})[日号]?)", text)
            if m:
                d = parse_date_from_text(m.group(0))
                if _year_ok(d):
                    comp_date = d
                    break

    if reg_deadline or comp_date:
        return reg_deadline, comp_date
    return None, None


def crawl_official_deadlines(competitions, max_items=None):
    """对白名单竞赛逐站直采截止日期。返回 enriched 列表（条目数不变）。"""
    items = competitions if max_items is None else competitions[:max_items]
    enriched = []
    discovered = 0
    filled = 0

    for comp in items:
        name = comp.get("name", "")
        url = comp.get("officialUrl", "")

        # 缺失官网则先尝试搜索发现
        if not url:
            try:
                found = search_official_url(name)
            except Exception:
                found = None
            if found:
                url = found
                comp["officialUrl"] = found
                comp["sourceVerified"] = True
                discovered += 1

        reg_deadline = None
        comp_date = None

        if url:
            try:
                resp = retry_get(url, headers=HEADERS, timeout=10)
                resp.encoding = resp.apparent_encoding or "utf-8"
                soup = __import__("bs4").BeautifulSoup(resp.text, "html.parser")
                full_text = soup.get_text(" ", strip=True)
                reg_deadline, comp_date = extract_timeline(full_text)
            except Exception as e:
                print(f"[官网直采] {name[:18]} 抓取失败: {e}")

        timeline = comp.setdefault("timeline", {})
        if reg_deadline:
            timeline["registrationDeadline"] = reg_deadline
        if comp_date:
            timeline["competitionDate"] = comp_date

        # 状态推导（有真实日期才覆盖默认的"待更新"）
        if reg_deadline or comp_date:
            comp["status"] = _derive_status(timeline)
            filled += 1
        else:
            comp["status"] = "待更新"

        enriched.append(comp)
        time.sleep(0.4)  # 礼貌延时

    print(f"[官网直采] 发现官网 {discovered} 条，成功提取日期 {filled} 条 / 共 {len(enriched)} 条")
    return enriched


if __name__ == "__main__":
    from .whitelist_84 import get_whitelist_competitions
    data = get_whitelist_competitions()
    out = crawl_official_deadlines(data, max_items=5)
    for c in out:
        print(c["name"][:22], "->", c["status"], c["timeline"])
