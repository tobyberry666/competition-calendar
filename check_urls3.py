import requests

# More attempts with different URL patterns
urls = {
    "光电设计竞赛": [
        "https://www.opticscompetition.cn/",
        "http://www.opticscompetition.cn/",
        "https://opticscompetition.cn/",
    ],
    "机械创新设计": [
        "http://www.mi.ustb.edu.cn/",
        "https://www.mi.ustb.edu.cn/",
        "https://mi.ustb.edu.cn/",
        "http://mi.ustb.edu.cn/",
    ],
    "化工设计竞赛": [
        "http://www.cacic.cn/",
        "https://www.cacic.cn/",
        "http://cacic.cn/",
        "https://chemyjs.cn/",
    ],
    "电子设计竞赛": [
        "https://nuedc.zju.edu.cn/",
        "http://nuedc.zju.edu.cn/",
        "https://www.nuedc.com.cn/",
        "http://www.nuedc.com.cn/",
    ],
    "市场调查大赛": [
        "http://www.china-stat.com/",
        "https://www.china-stat.com/",
        "http://china-stat.com/",
        "https://china-stat.org/",
    ],
}

for name, url_list in urls.items():
    found = False
    for url in url_list:
        try:
            r = requests.get(url, timeout=8, allow_redirects=True)
            print(f"{name:20s} | {r.status_code} | {len(r.content)} bytes | {url}")
            if r.status_code < 400:
                found = True
                break
        except Exception as e:
            print(f"{name:20s} | ERR | {url} | {e}")
    if not found:
        print(f"--- {name}: all failed ---")
