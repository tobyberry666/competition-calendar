"""dedup.py 单元测试（去重与置信度模型）。

同时兼容两种运行方式：
  - pytest tests/test_dedup.py
  - python tests/test_dedup.py   （无 pytest 环境时的独立运行）

直接按文件路径加载 dedup 模块，避免触发 crawlers/__init__.py 拉起全部爬虫依赖。
"""
import importlib.util
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("dedup", os.path.join(_ROOT, "crawlers", "dedup.py"))
dedup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dedup)


# ---------- normalize_name ----------

def test_normalize_strips_year_and_whitespace():
    assert dedup.normalize_name("RoboMaster 2026") == "robomaster"

def test_normalize_lowercases_ascii():
    assert dedup.normalize_name("ICPC") == "icpc"

def test_normalize_strips_session_prefix_and_cup():
    # "第3届" 整体移除（第\d+届），"杯" 是结构词
    assert dedup.normalize_name("第3届蓝桥杯") == "蓝桥"

def test_normalize_is_idempotent():
    once = dedup.normalize_name("2026年全国大学生数学建模竞赛")
    assert dedup.normalize_name(once) == once


# ---------- fuzzy_key（别名归一） ----------

def test_fuzzy_key_alias_maps_to_official_name():
    # "正大杯" 是官方名 "全国大学生市场调查与分析大赛" 的别名，二者必须同键
    assert (dedup.fuzzy_key("正大杯·第十四届市场调查大赛")
            == dedup.fuzzy_key("全国大学生市场调查与分析大赛"))

def test_fuzzy_key_icpc_variants_unify():
    assert (dedup.fuzzy_key("ICPC亚洲区域赛2026")
            == dedup.fuzzy_key("ACM-ICPC国际大学生程序设计竞赛"))

def test_fuzzy_key_robomaster_alias_matches_without_leading_space():
    # 回归：ALIASES 曾把 "RoboMaster" 写成 " RoboMaster"（前导空格），
    # 导致不含空格的名称永远匹配不上别名
    assert (dedup.fuzzy_key("RoboMaster机甲大师赛")
            == dedup.fuzzy_key("全国大学生机器人大赛")
            == "机器人")

def test_fuzzy_key_distinct_competitions_differ():
    assert dedup.fuzzy_key("蓝桥杯") != dedup.fuzzy_key("外研社杯")


# ---------- _score（合并优先级） ----------

def test_score_prefers_high_confidence_and_verified():
    strong = {"confidence": "high", "sourceVerified": True}
    weak = {"confidence": "low"}
    assert dedup._score(strong) > dedup._score(weak)

def test_score_rewards_dates_and_official_url():
    base = {"confidence": "medium"}
    rich = {"confidence": "medium",
            "timeline": {"registrationDeadline": "2026-09-01"},
            "officialUrl": "https://example.com"}
    assert dedup._score(rich) > dedup._score(base)

def test_score_source_verified_implies_high():
    # 无 confidence 字段时，sourceVerified=True 默认按 high 计
    assert (dedup._score({"sourceVerified": True})
            > dedup._score({"confidence": "medium"}))


# ---------- _overlay（字段补全） ----------

def test_overlay_fills_only_missing_fields():
    base = {"officialUrl": None, "category": "计算机类"}
    patch = {"officialUrl": "https://example.com", "category": "错误类"}
    merged = dedup._overlay(base, patch)
    assert merged["officialUrl"] == "https://example.com"
    assert merged["category"] == "计算机类"   # 已有字段不被覆盖

def test_overlay_upgrades_confidence_and_verified():
    base = {"confidence": "low", "sourceVerified": False}
    patch = {"confidence": "high", "sourceVerified": True}
    merged = dedup._overlay(base, patch)
    assert merged["confidence"] == "high"
    assert merged["sourceVerified"] is True

def test_overlay_keeps_base_confidence_when_equal_or_higher():
    base = {"confidence": "high"}
    patch = {"confidence": "low"}
    assert dedup._overlay(base, patch)["confidence"] == "high"

def test_overlay_longer_description_wins():
    base = {"description": "短"}
    patch = {"description": "这是一段更长的比赛介绍"}
    assert dedup._overlay(base, patch)["description"] == patch["description"]

def test_overlay_merges_source_labels():
    merged = dedup._overlay({"source": "saikr"}, {"source": "icpc"})
    assert merged["source"] == "saikr + icpc"

def test_overlay_does_not_lose_base_timeline():
    base = {"timeline": {"registrationDeadline": "2026-09-01"}}
    patch = {"timeline": {"competitionDate": "2026-10-01"}}
    merged = dedup._overlay(base, patch)
    assert merged["timeline"]["registrationDeadline"] == "2026-09-01"
    assert merged["timeline"]["competitionDate"] == "2026-10-01"


# ---------- merge_and_dedupe（端到端） ----------

def test_merge_unifies_alias_and_official_names():
    src_a = [{"name": "正大杯市场调查大赛", "confidence": "medium",
              "source": "saikr", "timeline": {"registrationDeadline": "2026-09-01"}}]
    src_b = [{"name": "全国大学生市场调查与分析大赛", "confidence": "high",
              "sourceVerified": True, "officialUrl": "https://example.com",
              "source": "whitelist"}]
    merged = dedup.merge_and_dedupe([src_a, src_b])
    assert len(merged) == 1
    item = merged[0]
    assert item["name"] == "正大杯市场调查大赛"          # 保留先出现者
    assert item["confidence"] == "high"                   # 置信度被升级
    assert item["sourceVerified"] is True
    assert item["officialUrl"] == "https://example.com"   # 空字段被补全
    assert item["timeline"]["registrationDeadline"] == "2026-09-01"
    assert "saikr" in item["source"] and "whitelist" in item["source"]

def test_merge_keeps_distinct_competitions_in_order():
    lists = [[{"name": "蓝桥杯", "source": "a"},
              {"name": "外研社杯", "source": "b"}]]
    merged = dedup.merge_and_dedupe(lists)
    assert [c["name"] for c in merged] == ["蓝桥杯", "外研社杯"]

def test_merge_defaults_confidence_from_source_verified():
    lists = [[{"name": "蓝桥杯", "sourceVerified": True}]]
    merged = dedup.merge_and_dedupe(lists)
    assert merged[0]["confidence"] == "high"

def test_merge_handles_empty_name_without_crash():
    merged = dedup.merge_and_dedupe([[{"name": "", "source": "x"}]])
    assert len(merged) == 1


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL {fn.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"  ERROR {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
