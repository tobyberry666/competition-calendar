"""
年轻AI线下大会 - 官网直采爬虫
针对 5 个面向青年的 AI 线下 / 创作大赛，逐个抓取官网，复用 official_site_crawler.extract_timeline
结构化提取「报名截止 / 比赛日期」。
设计原则（与项目一致）：
- 官网能抓到日期 → 用实时的；
- 官网是 SPA / 需登录 / 抓取失败 → 用下方已核实的种子日期兜底，绝不丢弃条目。
"""
import time
from datetime import datetime, date

from .retry import retry_get
from .seed_data import make_id
from .official_site_crawler import extract_timeline, HEADERS

CATEGORY = "年轻AI线下大会"

# 每个比赛的静态配置（name / officialUrl / 组织者 / 地点 / 子类 / 难度 / 奖项 / 简介）
# timeline 为「已核实的种子日期」（来源：各官网 / 主办方公告，2026 年），作为兜底。
COMPETITIONS = [
    {
        "name": "Google AI Vibe-a-thon出海创意赛",
        "officialUrl": "https://bj.huodongxing.com/event/1866445168100",
        "organizer": "杭州谷歌开发者社区（杭州GDG）",
        "location": {"province": "", "city": "", "display": "线上"},
        "subcategory": ["AI创意", "出海", "小红书创作"],
        "difficulty": "Beginner",
        "prize": "奖金 + 官方证书 + 导师点评 + 社区曝光；Top6 进入 Google I/O Connect 上海路演",
        "region": "online",
        "description": (
            "Google AI 出海创想赛 Vibe-a-thon，面向开发者、产品设计师、出海创业者与跨界创作者的 AI 创作挑战。"
            "鼓励从海外用户真实需求出发，用 Google AI 及相关工具链把创意做成产品或工具，并在小红书发布作品内容；"
            "优秀作品可获奖金、官方证书、导师点评与社区曝光，Top6 进入 Google I/O Connect 上海现场路演。"
        ),
        "timeline": {
            "registrationStart": "2026-06-23",
            "registrationDeadline": "2026-07-15",
            "submissionDeadline": None,
            "competitionDate": None,
            "resultDate": None,
        },
    },
    {
        "name": "小米集团黑客马拉松",
        "officialUrl": "https://hackathon-uni.tech.xiaomi.com/2026/#/",
        "organizer": "小米集团",
        "location": {"province": "北京", "city": "北京", "display": "小米总部（北京）"},
        "subcategory": ["黑客松", "48小时coding"],
        "difficulty": "Intermediate",
        "prize": "高额现金奖励 + 小米实习绿色通道 + 优质项目孵化通道；入围线下战队差旅食宿由小米承担",
        "region": "offline",
        "description": (
            "小米集团黑客马拉松，48 小时线下封闭 coding。赛道开放创新 / 技术探索，唯一标准是构思的独特性与实现潜力；"
            "赛程含线上组队报名、作品预审、小米总部 48 小时开发、初评（现场路演）与终评（现场答辩）。"
            "评审团由小米集团资深技术专家组成。"
        ),
        "timeline": {
            "registrationStart": "2026-06-22",
            "registrationDeadline": "2026-07-14",
            "submissionDeadline": None,
            "competitionDate": "2026-07-26",
            "resultDate": None,
        },
    },
    {
        "name": "TRAE AI创造力大赛",
        "officialUrl": "https://www.trae.cn/ai-creativity",
        "organizer": "字节跳动 TRAE",
        "location": {"province": "", "city": "", "display": "线上 + 决赛现场"},
        "subcategory": ["AI创作", "创造力", "TRAE"],
        "difficulty": "Beginner",
        "prize": "113 万现金奖池，单作品最高 35 万现金；报名成功即送 TRAE 中国版速通 Pro 月卡",
        "region": "online",
        "description": (
            "TRAE AI 创造力大赛，借助 TRAE IDE / TRAE Work 把创意做成可运行 Demo 并完善为完整产品。"
            "设报名 + 初赛（提交创意、创作 Demo）、复赛（创作完整产品）、决赛；报名成功即可获得 TRAE 速通月卡与决赛现场门票，"
            "主打「人人都可以创造」。"
        ),
        "timeline": {
            "registrationStart": "2026-06-16",
            "registrationDeadline": "2026-07-15",
            "submissionDeadline": None,
            "competitionDate": None,
            "resultDate": None,
        },
    },
    {
        "name": "CODING LADY女性黑客松",
        "officialUrl": "https://weibo.com/1029207511/R64BEeqGV",
        "organizer": "趁早 × 出门问问 × 真格基金 等",
        "location": {"province": "北京", "city": "北京", "display": "北京·海淀区（线下）"},
        "subcategory": ["女性黑客松", "公益", "AI Coding"],
        "difficulty": "Beginner",
        "prize": "主办方提供奖励 + 趁早 / 出门问问免费在线辅导（公益、开放、非商业化）",
        "region": "offline",
        "description": (
            "「她来创造 · CODING LADY 2026」女性 AI 创造者公益黑客松，由趁早与出门问问、真格基金等联合发起，"
            "获 Google GDG、WaytoAGI 等支持。面向所有女性（AI Coding 零基础亦可），借助 AI 工具完成从发现问题到落地成品的创作；"
            "线上比赛 7/18–20，线下比赛 7/25–26 于北京海淀。主打公益、开放、非商业化。"
        ),
        "timeline": {
            "registrationStart": "2026-06-27",
            "registrationDeadline": "2026-07-17",
            "submissionDeadline": None,
            "competitionDate": "2026-07-26",
            "resultDate": None,
        },
    },
    {
        "name": "一万个平行宇宙TapNow全球AI影视创作大赛",
        "officialUrl": "https://app.tapnow.ai/event/26",
        "organizer": "TapNow / TapTV Arena",
        "location": {"province": "", "city": "", "display": "线上 + 北京/厦门/北美/日本线下黑客松"},
        "subcategory": ["AI影视", "AIGC", "预告片"],
        "difficulty": "Intermediate",
        "prize": "总奖池 ¥3,000,000（动画 / 真人影视冠军各 30 万现金等），联合专业厂牌孵化高潜力 IP",
        "region": "global",
        "description": (
            "TapNow「一万个平行宇宙」全球 AI 影视创作大赛，面向全球征集 10,000 部 AI Trailer。"
            "分动画宇宙 / 真人影视宇宙 / MV 宇宙 / 宇宙联盟四赛道，联合多家专业制作厂牌对高潜力作品开启深度 IP 开发与孵化。"
            "口号：每一颗故事种子，都值得成为一个宇宙。"
        ),
        "timeline": {
            "registrationStart": "2026-04-02",
            "registrationDeadline": "2026-07-15",
            "submissionDeadline": "2026-07-15",
            "competitionDate": "2026-07-15",
            "resultDate": None,
        },
    },
]


def _derive_status(timeline):
    """根据 timeline 推导状态（与 official_site_crawler 逻辑一致）。"""
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


def crawl_young_ai_conference():
    """抓取「年轻AI线下大会」5 个比赛的官网，返回竞赛列表（条目数固定为 5）。"""
    competitions = []

    for cfg in COMPETITIONS:
        name = cfg["name"]
        url = cfg.get("officialUrl", "")
        # 兜底：已核实的种子时间
        timeline = {k: cfg["timeline"].get(k) for k in
                    ("registrationStart", "registrationDeadline", "submissionDeadline", "competitionDate", "resultDate")}

        # 尝试官网实时直采
        if url:
            try:
                resp = retry_get(url, headers=HEADERS, timeout=10)
                resp.encoding = resp.apparent_encoding or "utf-8"
                soup = __import__("bs4").BeautifulSoup(resp.text, "html.parser")
                text = soup.get_text(" ", strip=True)
                crawled_reg, crawled_comp = extract_timeline(text)
                if crawled_reg:
                    timeline["registrationDeadline"] = crawled_reg
                if crawled_comp:
                    timeline["competitionDate"] = crawled_comp
            except Exception as e:
                print(f"[年轻AI线下大会] {name[:16]} 官网抓取失败，使用已核实种子日期: {e}")

        comp = {
            "id": make_id(name),
            "name": name,
            "category": CATEGORY,
            "subcategory": cfg.get("subcategory", []),
            "organizer": cfg.get("organizer", ""),
            "location": cfg.get("location", {"province": "", "city": "", "display": ""}),
            "timeline": timeline,
            "description": cfg.get("description", ""),
            "officialUrl": url,
            "source": "年轻AI线下大会·官网爬虫",
            "sourceVerified": True,
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "difficulty": cfg.get("difficulty", "Beginner"),
            "prize": cfg.get("prize", ""),
            "region": cfg.get("region", ""),
            "status": _derive_status(timeline),
            "confidence": "high",
        }
        competitions.append(comp)
        time.sleep(0.4)  # 礼貌延时

    print(f"[年轻AI线下大会] 采集 {len(competitions)} 条比赛")
    return competitions


if __name__ == "__main__":
    data = crawl_young_ai_conference()
    for c in data:
        print(f"{c['name'][:24]:24} | {c['status']:6} | {c['timeline']}")
