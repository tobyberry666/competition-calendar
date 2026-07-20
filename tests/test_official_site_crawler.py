import sys
import types
import unittest

if "bs4" not in sys.modules:
    bs4 = types.ModuleType("bs4")
    bs4.BeautifulSoup = object
    sys.modules["bs4"] = bs4

from crawlers.official_site_crawler import extract_timeline


class OfficialSiteCrawlerTests(unittest.TestCase):
    def test_extract_timeline_returns_registration_and_competition_dates(self):
        text = "报名截止：2026年9月30日。比赛时间：2026年10月18日。"

        self.assertEqual(("2026-09-30", "2026-10-18"), extract_timeline(text))

    def test_extract_timeline_returns_none_for_text_without_dates(self):
        self.assertEqual((None, None), extract_timeline("报名信息待公布。"))


if __name__ == "__main__":
    unittest.main()
