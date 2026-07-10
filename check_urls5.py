import requests

urls = {
    "化工设计_新的": [
        "https://chemyjs.cn/",
        "http://chemyjs.cn/",
        "https://www.chemyjs.org/",
    ],
    "机械创新_北科大新": [
        "https://www.mechinnovation.cn/",
        "http://www.mechinnovation.cn/",
        "https://mechinnovation.cn/",
    ],
    "光电_上海交大": [
        "https://www.optics.sjtu.edu.cn/",
        "http://www.optics.sjtu.edu.cn/",
        "https://optics.sjtu.edu.cn/",
    ],
    "市场调查_中国商业统计学会": [
        "http://www.chinastatistics.org/",
        "https://www.chinastatistics.org/",
        "http://chinastatistics.org/",
    ],
}

for name, url_list in urls.items():
    for url in url_list:
        try:
            r = requests.get(url, timeout=8, allow_redirects=True)
            print(f"{name:20s} | {r.status_code} | {len(r.content)} bytes | {url}")
            if r.status_code < 400:
                break
        except Exception as e:
            print(f"{name:20s} | ERR | {url}")
