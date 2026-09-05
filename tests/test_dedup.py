import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_SPEC = spec_from_file_location(
    "dedup", Path(__file__).resolve().parents[1] / "crawlers" / "dedup.py"
)
dedup = module_from_spec(_SPEC)
_SPEC.loader.exec_module(dedup)
fuzzy_key = dedup.fuzzy_key
merge_and_dedupe = dedup.merge_and_dedupe


class DedupTests(unittest.TestCase):
    def test_fuzzy_key_matches_zhengda_cup_to_official_name(self):
        self.assertEqual(
            fuzzy_key("正大杯"),
            fuzzy_key("全国大学生市场调查与分析大赛"),
        )

    def test_higher_confidence_duplicate_supplies_official_url(self):
        alias_record = {
            "name": "正大杯",
            "officialUrl": "https://aggregator.example/item",
            "confidence": "medium",
            "sourceVerified": False,
        }
        verified_record = {
            "name": "全国大学生市场调查与分析大赛",
            "officialUrl": "https://official.example/",
            "confidence": "high",
            "sourceVerified": True,
        }

        merged = merge_and_dedupe([[alias_record], [verified_record]])

        self.assertEqual(1, len(merged))
        self.assertEqual("https://official.example/", merged[0]["officialUrl"])
        self.assertEqual("high", merged[0]["confidence"])


if __name__ == "__main__":
    unittest.main()
