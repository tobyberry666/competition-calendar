import requests

urls = {
    "光电设计竞赛": [
        "https://www.guangdiansheji.com/",
        "http://www.opticscompetition.cn/",
        "https://optics.sjtu.edu.cn/",
        "https://www.opencollege.net/",
    ],
    "西门子杯": [
        "https://www.siemenscup-cimc.com/",
        "https://siemenscup.com/",
        "https://www.siemens.com.cn/",
    ],
    "机械创新设计": [
        "https://www.mechinnovation.cn/",
        "https://www.mechdesign.org.cn/",
        "http://www.mi.ustb.edu.cn/",
    ],
    "化工设计竞赛": [
        "https://chemyjs.com/",
        "http://chemyjs.com/",
        "https://www.chemyjs.cn/",
    ],
    "信息安全竞赛": [
        "https://www.ciscn.cn/",
        "https://ciscn.sjtu.edu.cn/",
        "http://www.ciscn.cn/",
    ],
    "电子设计竞赛": [
        "https://nuedc.zju.edu.cn/",
        "https://www.nuedc.com.cn/",
        "https://nuedc.bjtu.edu.cn/",
    ],
    "市场调查大赛": [
        "http://www.china-stat.com/",
        "https://www.china-stat.org/",
        "http://www.chinastatistics.org/",
    ],
}

for name, url_list in urls.items():
    found = False
    for url in url_list:
        try:
            r = requests.head(url, timeout=5, allow_redirects=True)
            if r.status_code < 400:
                print(f"OK {name:20s} | {r.status_code} | {url}")
                found = True
                break
        except:
            pass
    if not found:
        print(f"FAIL {name:20s} | all failed")
