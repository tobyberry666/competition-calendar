import requests

# Final round - search for working alternatives
urls = {
    "电子设计竞赛_nuedc": "http://www.nuedc.com.cn/",
    "信息安全_ciscn": "http://www.ciscn.cn/",
    "化工设计_chemyjs": "https://chemyjs.com/",
    "光电_百度百科": "https://baike.baidu.com/item/%E5%85%A8%E5%9B%BD%E5%A4%A7%E5%AD%A6%E7%94%9F%E5%85%89%E7%94%B5%E8%AE%BE%E8%AE%A1%E7%AB%9E%E8%B5%9B",
    "机械创新_百度百科": "https://baike.baidu.com/item/%E5%85%A8%E5%9B%BD%E5%A4%A7%E5%AD%A6%E7%94%9F%E6%9C%BA%E6%A2%B0%E5%88%9B%E6%96%B0%E8%AE%BE%E8%AE%A1%E5%A4%A7%E8%B5%9B",
    "市场调查_百度百科": "https://baike.baidu.com/item/%E5%85%A8%E5%9B%BD%E5%A4%A7%E5%AD%A6%E7%94%9F%E5%B8%82%E5%9C%BA%E8%B0%83%E6%9F%A5%E4%B8%8E%E5%88%86%E6%9E%90%E5%A4%A7%E8%B5%9B",
}

for name, url in urls.items():
    try:
        r = requests.get(url, timeout=8, allow_redirects=True)
        print(f"{name:20s} | {r.status_code} | {len(r.content)} bytes | {url}")
    except Exception as e:
        print(f"{name:20s} | ERR | {url}")
