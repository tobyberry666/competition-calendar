import requests

# Check corrected URLs
urls_to_check = {
    "计算机设计大赛新": "https://jsjds.blcu.edu.cn/",
    "光电设计竞赛": "https://optics.sjtu.edu.cn/",
    "西门子杯": "https://www.siemenscup-cimc.cn/",
    "机械创新设计": "https://www.mechinnovation.com/",
    "化工设计竞赛": "https://chemyjs.com/",
    "市场调查大赛": "https://www.stats.gov.cn/",
    "信息安全竞赛": "https://ciscn.sjtu.edu.cn/",
    "电子设计竞赛": "https://nuedc.zju.edu.cn/",
}

for name, url in urls_to_check.items():
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        print(f"{name:20s} | {r.status_code} | {url}")
    except Exception as e:
        print(f"{name:20s} | FAIL: {type(e).__name__} | {url}")
