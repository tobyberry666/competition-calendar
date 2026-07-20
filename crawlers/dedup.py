"""
去重与置信度模型（P1）
- 模糊归一化：去掉"全国大学生/大赛/杯/届/年份"等结构词后匹配，合并同竞赛不同表述
- 别名表：把昵称（正大杯、工行杯、大广赛、互联网+、ICPC…）归一到白名单官方名
- 置信度：high=白名单+官网直采，medium=聚合站匹配，low=搜索发现
- 合并时优先保留：置信度高 > sourceVerified > 有日期 > 有官网 的记录
"""
import re

# 昵称 / 旧名 -> 白名单官方名（保证正大杯↔市场调查 等被合并）
ALIASES = {
    "正大杯": "全国大学生市场调查与分析大赛",
    "工行杯": "“工行杯”全国大学生金融科技创新大赛",
    "大广赛": "全国大学生广告艺术大赛",
    "广告艺术大赛": "全国大学生广告艺术大赛",
    "互联网+": "中国国际“互联网+”大学生创新创业大赛",
    "大挑": "“挑战杯”全国大学生课外学术科技作品竞赛",
    "小挑": "“挑战杯”中国大学生创业计划大赛",
    "三创赛": "全国大学生电子商务“创新、创意及创业”挑战赛",
    "电子商务三创赛": "全国大学生电子商务“创新、创意及创业”挑战赛",
    "外研社杯": "外研社全国大学生英语系列赛",
    "蓝桥杯": "蓝桥杯全国软件和信息技术专业人才大赛",
    "数学建模": "全国大学生数学建模竞赛",
    "ICPC": "ACM-ICPC国际大学生程序设计竞赛",
    "ICPC亚洲区域赛": "ACM-ICPC国际大学生程序设计竞赛",
    "工程训练综合能力竞赛": "中国大学生工程实践与创新能力大赛",
    " RoboMaster": "全国大学生机器人大赛",
    "RoboCon": "全国大学生机器人大赛",
}

# 归一化时移除的结构词（保守，避免误并）
_REMOVE_TOKENS = [
    "全国大学生", "全国", "大学生", "国际", "中国", "系列赛", "挑战赛",
    "竞赛", "大赛", "杯", "赛", "届",
]
_REMOVE_RE = re.compile(
    r"第\d+届|[" + "".join(_REMOVE_TOKENS) + r"]|\d{4}|\d{1,2}月\d{1,2}[日号]?|“|”|\"|'|\s"
)
_DIGIT_RE = re.compile(r"\d+")


def normalize_name(name):
    """去掉结构词/年份/标点，得到可比较的归一名"""
    s = name.lower()
    s = _REMOVE_RE.sub("", s)
    s = _DIGIT_RE.sub("", s)
    return s.strip()


def fuzzy_key(name):
    """计算去重键：先查别名，再归一化（避免别名键是规范名子串导致递归）"""
    for alias_key, canonical in ALIASES.items():
        if alias_key in name and alias_key != canonical:
            return normalize_name(canonical)
    return normalize_name(name)


CONF_RANK = {"high": 3, "medium": 2, "low": 1}


def _score(comp):
    c = comp.get("confidence") or ("high" if comp.get("sourceVerified") else "medium")
    tl = comp.get("timeline", {}) or {}
    has_date = any(tl.get(k) for k in ("registrationDeadline", "competitionDate"))
    return (
        CONF_RANK.get(c, 2) * 10
        + (3 if comp.get("sourceVerified") else 0)
        + (2 if has_date else 0)
        + (1 if comp.get("officialUrl") else 0)
    )


def _overlay(base, patch):
    """以 base 为主，用 patch 的非空字段补全"""
    for k in ("officialUrl", "organizer", "category"):
        if not base.get(k) and patch.get(k):
            base[k] = patch[k]
    tl_b, tl_p = base.setdefault("timeline", {}), patch.get("timeline", {}) or {}
    for k in ("registrationStart", "registrationDeadline", "submissionDeadline", "competitionDate", "resultDate"):
        if not tl_b.get(k) and tl_p.get(k):
            tl_b[k] = tl_p[k]
    if len(patch.get("description", "")) > len(base.get("description", "")):
        base["description"] = patch["description"]
    base["sourceVerified"] = bool(base.get("sourceVerified")) or bool(patch.get("sourceVerified"))
    bc = base.get("confidence") or ("high" if base.get("sourceVerified") else "medium")
    pc = patch.get("confidence") or ("high" if patch.get("sourceVerified") else "medium")
    base["confidence"] = bc if CONF_RANK.get(bc, 2) >= CONF_RANK.get(pc, 2) else pc
    # 合并来源标记
    src = base.get("source", "")
    if patch.get("source") and patch["source"] not in src:
        base["source"] = (src + " + " + patch["source"]).strip(" +")
    return base


def merge_and_dedupe(all_lists):
    """合并多数据源并按模糊键去重。返回去重后的列表（保留首个出现顺序）。"""
    buckets = {}
    order = []
    for comp_list in all_lists:
        for comp in comp_list:
            comp.setdefault("confidence", "high" if comp.get("sourceVerified") else "medium")
            key = fuzzy_key(comp.get("name", ""))
            if not key:
                key = "___" + comp.get("name", str(id(comp)))
            if key in buckets:
                current = buckets[key]
                if _score(comp) > _score(current):
                    buckets[key] = _overlay(comp, current)
                else:
                    buckets[key] = _overlay(current, comp)
            else:
                buckets[key] = comp
                order.append(key)
    return [buckets[k] for k in order]
