"""
教育部白名单竞赛 - 种子数据
来源：教育部公布的全国大学生学科竞赛白名单
作为基础数据补充，确保核心竞赛一定收录
"""
from datetime import datetime


def make_id(name):
    """从竞赛名称生成 slug ID"""
    import re
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\u4e00-\u9fff-]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    if not slug:
        slug = datetime.now().strftime("%Y%m%d%H%M%S")
    return slug


def get_seed_competitions():
    """获取种子竞赛数据"""
    now = datetime.now().strftime("%Y-%m-%d")
    seed = [
        {
            "id": make_id("中国国际大学生创新大赛"),
            "name": "中国国际大学生创新大赛",
            "category": "创新创业类",
            "subcategory": ["互联网+"],
            "organizer": "教育部",
            "location": {"province": "", "city": "", "display": "全国"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-06-30",
                "submissionDeadline": None,
                "competitionDate": "2026-10-15",
                "resultDate": None
            },
            "description": "教育部主办，国内规模最大、认可度最高的大学生创新创业大赛",
            "officialUrl": "https://cy.ncss.cn",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Advanced",
            "prize": "",
            "region": "national",
            "status": "已截止"
        },
        {
            "id": make_id("挑战杯课外学术科技作品竞赛"),
            "name": "挑战杯课外学术科技作品竞赛",
            "category": "创新创业类",
            "subcategory": ["挑战杯"],
            "organizer": "共青团中央",
            "location": {"province": "", "city": "", "display": "全国"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-05-15",
                "submissionDeadline": None,
                "competitionDate": "2026-11-01",
                "resultDate": None
            },
            "description": "共青团中央主办，大挑，两年一届，奇数年举办",
            "officialUrl": "http://www.tiaozhanbei.net",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Advanced",
            "prize": "",
            "region": "national",
            "status": "已截止"
        },
        {
            "id": make_id("ICPC亚洲区域赛"),
            "name": "ICPC亚洲区域赛",
            "category": "计算机类",
            "subcategory": ["ICPC", "XCPC"],
            "organizer": "ICPC北京总部",
            "location": {"province": "", "city": "", "display": "全国多赛站"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-09-30",
                "submissionDeadline": None,
                "competitionDate": "2026-11-15",
                "resultDate": None
            },
            "description": "国际顶级算法竞赛，ACM/ICPC亚洲区预选赛",
            "officialUrl": "https://icpc.pku.edu.cn",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Advanced",
            "prize": "",
            "region": "regional",
            "status": "报名中"
        },
        {
            "id": make_id("中国大学生计算机设计大赛"),
            "name": "中国大学生计算机设计大赛",
            "category": "计算机类",
            "subcategory": ["计算机"],
            "organizer": "教育部计算机教指委",
            "location": {"province": "", "city": "", "display": "全国"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-04-30",
                "submissionDeadline": None,
                "competitionDate": "2026-08-01",
                "resultDate": None
            },
            "description": "教育部高校计算机类专业教学指导委员会主办",
            "officialUrl": "https://jsjds.blcu.edu.cn/",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Intermediate",
            "prize": "",
            "region": "national",
            "status": "已截止"
        },
        {
            "id": make_id("蓝桥杯软件和信息技术专业人才大赛"),
            "name": "蓝桥杯软件和信息技术专业人才大赛",
            "category": "计算机类",
            "subcategory": ["蓝桥杯"],
            "organizer": "工信部人才交流中心",
            "location": {"province": "", "city": "", "display": "全国各赛区"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-03-31",
                "submissionDeadline": None,
                "competitionDate": "2026-06-13",
                "resultDate": None
            },
            "description": "工业和信息化部人才交流中心主办，参赛人数最多的IT类竞赛",
            "officialUrl": "https://dasai.lanqiao.cn",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Beginner",
            "prize": "",
            "region": "regional",
            "status": "已截止"
        },
        {
            "id": make_id("全国大学生信息安全竞赛"),
            "name": "全国大学生信息安全竞赛",
            "category": "计算机类",
            "subcategory": ["信息安全"],
            "organizer": "教育部",
            "location": {"province": "", "city": "", "display": "全国"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-05-31",
                "submissionDeadline": None,
                "competitionDate": "2026-08-15",
                "resultDate": None
            },
            "description": "国内信息安全领域顶级大学生竞赛",
            "officialUrl": "http://www.ciscn.cn",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Advanced",
            "prize": "",
            "region": "national",
            "status": "已截止"
        },
        {
            "id": make_id("全国大学生数学建模竞赛"),
            "name": "全国大学生数学建模竞赛",
            "category": "数学类",
            "subcategory": ["数学建模"],
            "organizer": "教育部",
            "location": {"province": "", "city": "", "display": "各高校"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-09-01",
                "submissionDeadline": None,
                "competitionDate": "2026-09-11",
                "resultDate": None
            },
            "description": "全国高校规模最大的基础性学科竞赛",
            "officialUrl": "http://www.mcm.edu.cn",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Intermediate",
            "prize": "",
            "region": "regional",
            "status": "报名中"
        },
        {
            "id": make_id("全国大学生数学竞赛"),
            "name": "全国大学生数学竞赛",
            "category": "数学类",
            "subcategory": ["数学"],
            "organizer": "中国数学会",
            "location": {"province": "", "city": "", "display": "各高校"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-10-15",
                "submissionDeadline": None,
                "competitionDate": "2026-10-31",
                "resultDate": None
            },
            "description": "中国数学会主办，分数学专业组和非数学专业组",
            "officialUrl": "http://www.cmathc.cn",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Advanced",
            "prize": "",
            "region": "regional",
            "status": "即将开始"
        },
        {
            "id": make_id("全国大学生电子设计竞赛"),
            "name": "全国大学生电子设计竞赛",
            "category": "电子信息类",
            "subcategory": ["电子设计"],
            "organizer": "教育部",
            "location": {"province": "", "city": "", "display": "全国各赛区"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": None,
                "submissionDeadline": None,
                "competitionDate": None,
                "resultDate": None
            },
            "description": "教育部高等教育司主办，两年一届，奇数年举办",
            "officialUrl": "http://www.nuedc.com.cn",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Advanced",
            "prize": "",
            "region": "regional",
            "status": "偶数年"
        },
        {
            "id": make_id("全国大学生光电设计竞赛"),
            "name": "全国大学生光电设计竞赛",
            "category": "电子信息类",
            "subcategory": ["光电"],
            "organizer": "中国光学学会",
            "location": {"province": "", "city": "", "display": "全国"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-05-31",
                "submissionDeadline": None,
                "competitionDate": "2026-07-20",
                "resultDate": None
            },
            "description": "中国光学学会主办，光电领域最高水平大学生竞赛",
            "officialUrl": "https://www.optics.sjtu.edu.cn/",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Intermediate",
            "prize": "",
            "region": "national",
            "status": "已截止"
        },
        {
            "id": make_id("西门子杯中国智能制造挑战赛"),
            "name": "西门子杯中国智能制造挑战赛",
            "category": "电子信息类",
            "subcategory": ["智能制造"],
            "organizer": "西门子+教育部",
            "location": {"province": "", "city": "", "display": "全国"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-05-15",
                "submissionDeadline": None,
                "competitionDate": "2026-08-10",
                "resultDate": None
            },
            "description": "西门子与教育部合作举办的工业自动化竞赛",
            "officialUrl": "https://www.siemens.com.cn/",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Intermediate",
            "prize": "",
            "region": "national",
            "status": "已截止"
        },
        {
            "id": make_id("全国大学生机械创新设计大赛"),
            "name": "全国大学生机械创新设计大赛",
            "category": "机械类",
            "subcategory": ["机械"],
            "organizer": "教育部机械教指委",
            "location": {"province": "", "city": "", "display": "全国"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": None,
                "submissionDeadline": None,
                "competitionDate": None,
                "resultDate": None
            },
            "description": "教育部机械基础课程教学指导委员会主办",
            "officialUrl": "https://www.mechinnovation.cn/",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Intermediate",
            "prize": "",
            "region": "national",
            "status": "偶数年"
        },
        {
            "id": make_id("全国大学生工程训练综合能力竞赛"),
            "name": "全国大学生工程训练综合能力竞赛",
            "category": "机械类",
            "subcategory": ["工程训练"],
            "organizer": "教育部",
            "location": {"province": "", "city": "", "display": "全国"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": None,
                "submissionDeadline": None,
                "competitionDate": None,
                "resultDate": None
            },
            "description": "教育部高等教育司主办，工程实践类竞赛",
            "officialUrl": "http://www.gcxl.edu.cn",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Intermediate",
            "prize": "",
            "region": "national",
            "status": "奇数年"
        },
        {
            "id": make_id("全国大学生英语竞赛"),
            "name": "全国大学生英语竞赛",
            "category": "外语类",
            "subcategory": ["英语"],
            "organizer": "中国外语教学研究会",
            "location": {"province": "", "city": "", "display": "各高校"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-03-15",
                "submissionDeadline": None,
                "competitionDate": "2026-04-12",
                "resultDate": None
            },
            "description": "全国规模最大的大学生英语学科竞赛，分A/B/C/D类",
            "officialUrl": "https://www.chinaneccs.cn",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Beginner",
            "prize": "",
            "region": "regional",
            "status": "已截止"
        },
        {
            "id": make_id("全国大学生化工设计竞赛"),
            "name": "全国大学生化工设计竞赛",
            "category": "化工类",
            "subcategory": ["化工"],
            "organizer": "中国化工学会",
            "location": {"province": "", "city": "", "display": "全国"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-05-31",
                "submissionDeadline": None,
                "competitionDate": "2026-08-01",
                "resultDate": None
            },
            "description": "中国化工学会化学工程专业委员会主办",
            "officialUrl": "https://chemyjs.com/",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Intermediate",
            "prize": "",
            "region": "national",
            "status": "已截止"
        },
        {
            "id": make_id("全国大学生市场调查与分析大赛"),
            "name": "全国大学生市场调查与分析大赛",
            "category": "商科类",
            "subcategory": ["市场调查"],
            "organizer": "中国商业统计学会",
            "location": {"province": "", "city": "", "display": "全国"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-03-31",
                "submissionDeadline": None,
                "competitionDate": "2026-05-25",
                "resultDate": None
            },
            "description": "中国商业统计学会主办",
            "officialUrl": "https://www.chinastatistics.org/",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Beginner",
            "prize": "",
            "region": "national",
            "status": "已截止"
        },
        {
            "id": make_id("全国大学生电子商务三创赛"),
            "name": "全国大学生电子商务三创赛",
            "category": "商科类",
            "subcategory": ["电子商务"],
            "organizer": "教育部电商教指委",
            "location": {"province": "", "city": "", "display": "全国"},
            "timeline": {
                "registrationStart": None,
                "registrationDeadline": "2026-03-31",
                "submissionDeadline": None,
                "competitionDate": "2026-07-15",
                "resultDate": None
            },
            "description": "教育部电子商务类专业教学指导委员会主办",
            "officialUrl": "http://www.3chuang.net",
            "source": "教育部白名单",
            "sourceVerified": True,
            "lastUpdated": now,
            "difficulty": "Beginner",
            "prize": "",
            "region": "national",
            "status": "已截止"
        },
    ]

    print(f"[种子数据] 加载 {len(seed)} 条教育部白名单竞赛")
    return seed


if __name__ == "__main__":
    data = get_seed_competitions()
    print(f"共 {len(data)} 条种子数据")
