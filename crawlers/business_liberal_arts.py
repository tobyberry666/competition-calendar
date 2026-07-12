"""
商科 / 文科竞赛专项爬虫
=================================================
专门保证「工行杯」「正大杯」这类面向商科、文科、设计、外语类专业学生的
竞赛稳定进入数据库。

设计思路（双保险）：
  1. GUARANTEED_COMPETITIONS —— 手工维护的「保底清单」，全部 sourceVerified=True，
     即使网络完全不可用，这些竞赛也一定进库（这是“稳定进库”的核心保障）。
  2. crawl_business_liberal_live() —— 在赛氪网实时抓取商科/设计/外语/文体类
     竞赛，补充当季最新动态。抓取失败时不影响保底清单。

模块对外暴露:
  - get_guaranteed_business_liberal()  -> 保底清单（list[dict]）
  - crawl_business_liberal(max_pages)  -> 保底 + 实时 合并去重后的完整列表
"""
from datetime import datetime

from .retry import retry_get
from .categories import guess_category
from .seed_data import make_id
from .saikr import crawl_saikr_hot

# 这些分类视为「商科 / 文科」范畴，实时抓取时只保留命中这些分类的竞赛
LIBERAL_ARTS_CATEGORIES = {
    "商科类", "设计类", "外语类", "文体类", "学科类",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 保底清单：手工维护，全部为 sourceVerified=True
# 日期说明：带「[预计]」字样的是根据往届赛程推算的下一届时间，以官网为准。
GUARANTEED_COMPETITIONS = [
    {
        "id": make_id("工行杯全国大学生金融科技创新大赛"),
        "name": "工行杯（全国大学生金融科技创新大赛）",
        "category": "商科类",
        "subcategory": ["金融科技", "工行杯"],
        "organizer": "中国工商银行",
        "location": {"province": "", "city": "", "display": "全国"},
        "timeline": {
            "registrationStart": "2026-05-27",
            "registrationDeadline": "2026-09-30",
            "submissionDeadline": None,
            "competitionDate": "2026-12-26",
            "resultDate": None,
        },
        "description": (
            "中国工商银行主办的第17届全国大学生金融科技创新大赛，主题「数智银行·创见未来」，"
            "设科技金融、绿色金融、普惠金融等十大方向。报名2026年5月—9月，官网报名截止9月30日"
            "（部分校赛渠道提示9月1日，以官网 gonghangbei.com 为准）；省赛10月、全国总决赛12月。"
            "特等奖2万元/组并提供工行实习机会。"
        ),
        "officialUrl": "https://www.gonghangbei.com",
        "source": "商科文科爬虫·保底清单",
        "sourceVerified": True,
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "difficulty": "Intermediate",
        "prize": "特等奖2万元/组 + 工行实习",
        "region": "national",
        "status": "报名中",
    },
    {
        "id": make_id("正大杯全国大学生市场调查与分析大赛"),
        "name": "正大杯（全国大学生市场调查与分析大赛）",
        "category": "商科类",
        "subcategory": ["市场调查", "正大杯"],
        "organizer": "中国商业统计学会（正大集团冠名）",
        "location": {"province": "", "city": "", "display": "全国"},
        "timeline": {
            "registrationStart": "2026-10-25",
            "registrationDeadline": "2026-11-20",
            "submissionDeadline": None,
            "competitionDate": "2027-05-25",
            "resultDate": None,
        },
        "description": (
            "中国商业统计学会主办、正大集团冠名的全国性大学生市场调查类赛事，文科/商科生热门选择。"
            "[预计] 第17届（2026-2027学年）预计2026年10月启动报名，省赛次年4月、全国总决赛次年5月；"
            "具体日期以官网 china-cssc.org 通知为准。第16届已于2026年5月结束。"
        ),
        "officialUrl": "https://www.china-cssc.org/list-550-1.html",
        "source": "商科文科爬虫·保底清单",
        "sourceVerified": True,
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "difficulty": "Beginner",
        "prize": "",
        "region": "national",
        "status": "未开始",
    },
    {
        "id": make_id("全国大学生广告艺术大赛"),
        "name": "全国大学生广告艺术大赛（大广赛）",
        "category": "设计类",
        "subcategory": ["广告", "大广赛"],
        "organizer": "教育部高等教育司",
        "location": {"province": "", "city": "", "display": "全国"},
        "timeline": {
            "registrationStart": None,
            "registrationDeadline": "2026-06-30",
            "submissionDeadline": None,
            "competitionDate": "2026-08-15",
            "resultDate": None,
        },
        "description": (
            "教育部认可的全国大学生广告艺术大赛，覆盖平面、视频、动画、文案、营销策划等赛道，"
            "设计/传媒/文科生核心赛事。[预计] 2026年第16届全国总评审预计7-8月，报名通常6月底前截止。"
        ),
        "officialUrl": "http://www.sun-ada.net",
        "source": "商科文科爬虫·保底清单",
        "sourceVerified": True,
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "difficulty": "Intermediate",
        "prize": "",
        "region": "national",
        "status": "进行中",
    },
    {
        "id": make_id("外研社国才杯全国英语演讲大赛"),
        "name": "外研社·国才杯 全国英语演讲大赛",
        "category": "外语类",
        "subcategory": ["英语", "演讲"],
        "organizer": "外语教学与研究出版社",
        "location": {"province": "", "city": "", "display": "全国"},
        "timeline": {
            "registrationStart": None,
            "registrationDeadline": "2026-10-15",
            "submissionDeadline": None,
            "competitionDate": "2026-12-15",
            "resultDate": None,
        },
        "description": (
            "外语教学与研究出版社主办的「外研社·国才杯·合智杯」系列赛事中的英语演讲赛道，"
            "外语类最热门竞赛之一。[预计] 校赛/省赛秋季进行，全国总决赛12月。"
        ),
        "officialUrl": "https://uchallenge.unipus.cn",
        "source": "商科文科爬虫·保底清单",
        "sourceVerified": True,
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "difficulty": "Intermediate",
        "prize": "",
        "region": "national",
        "status": "未开始",
    },
    {
        "id": make_id("中国大学生服务外包创新创业大赛"),
        "name": "中国大学生服务外包创新创业大赛",
        "category": "商科类",
        "subcategory": ["服务外包", "创新创业"],
        "organizer": "教育部 + 商务部",
        "location": {"province": "", "city": "", "display": "全国"},
        "timeline": {
            "registrationStart": None,
            "registrationDeadline": "2026-12-31",
            "submissionDeadline": None,
            "competitionDate": "2027-05-15",
            "resultDate": None,
        },
        "description": (
            "教育部、商务部联合主办的服创类赛事，企业命题赛道对商科、管理、计算机交叉背景友好。"
            "[预计] 报名通常年底截止，全国总决赛次年5月。"
        ),
        "officialUrl": "http://www.fwwb.org.cn",
        "source": "商科文科爬虫·保底清单",
        "sourceVerified": True,
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "difficulty": "Intermediate",
        "prize": "",
        "region": "national",
        "status": "报名中",
    },
]


def get_guaranteed_business_liberal():
    """返回保底清单（每次返回新副本，避免被外部修改污染）"""
    return [dict(comp) for comp in GUARANTEED_COMPETITIONS]


def crawl_business_liberal_live(max_pages=2):
    """实时抓取赛氪网上的商科/设计/外语/文体类竞赛，作为保底清单的补充。

    抓取失败时返回空列表，不影响保底清单。
    """
    live = []
    try:
        for page in range(1, max_pages + 1):
            items = crawl_saikr_hot(page)
            if not items:
                break
            for comp in items:
                # 只保留商科/文科范畴的竞赛，避免与通用赛氪爬虫重复收录理工类
                if comp.get("category") in LIBERAL_ARTS_CATEGORIES:
                    live.append(comp)
        print(f"[商科文科·实时] 抓取到 {len(live)} 条商科/文科类竞赛")
    except Exception as e:
        print(f"[商科文科·实时] 抓取异常（不影响保底清单）: {e}")
        return []
    return live


def crawl_business_liberal(max_pages=2):
    """主入口：保底清单 + 实时抓取，合并去重后返回。

    保底清单永远优先（sourceVerified=True），保证『工行杯』『正大杯』等稳定进库。
    """
    guaranteed = get_guaranteed_business_liberal()
    live = crawl_business_liberal_live(max_pages=max_pages)

    merged = []
    seen = set()
    # 先放保底清单，确保它们一定保留
    for comp in guaranteed:
        key = comp["name"].strip()
        if key and key not in seen:
            seen.add(key)
            merged.append(comp)
    # 再放实时抓取（同名则跳过，保底优先）
    for comp in live:
        key = comp["name"].strip()
        if key and key not in seen:
            seen.add(key)
            merged.append(comp)

    print(f"[商科文科] 共 {len(merged)} 条（保底 {len(guaranteed)} + 实时 {len(live)}）")
    return merged


if __name__ == "__main__":
    import json
    data = crawl_business_liberal(2)
    print(json.dumps(data[:3], ensure_ascii=False, indent=2))
