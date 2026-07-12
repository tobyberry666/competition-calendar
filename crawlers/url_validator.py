"""
URL 验证与自动发现模块
每天自动检查所有竞赛官网链接，挂了的自动搜新的
"""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from .retry import retry_get

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9"
}

# 已知的可靠域名映射（当搜索找不到时的备选）
KNOWN_DOMAINS = {
    "ICPC": ["icpc.pku.edu.cn", "icpc.global"],
    "CCPC": ["ccpc.edu.cn"],
    "蓝桥杯": ["dasai.lanqiao.cn"],
    "数学建模": ["mcm.edu.cn", "mcm.mcm.edu.cn"],
    "数学竞赛": ["cmathc.cn"],
    "英语竞赛": ["chinaneccs.cn"],
    "电子设计": ["nuedc.com.cn"],
    "信息安全": ["ciscn.cn"],
    "计算机设计": ["jsjds.blcu.edu.cn"],
    "创新大赛": ["cy.ncss.cn"],
    "挑战杯": ["tiaozhanbei.net"],
    "工程训练": ["gcxl.edu.cn"],
    "电子商务": ["3chuang.net"],
    "化工设计": ["chemyjs.com"],
    "西门子杯": ["siemens.com.cn"],
    "正大杯": ["china-cssc.org"],
    "市场调查": ["china-cssc.org"],
    "工行杯": ["gonghangbei.com"],
    "广告": ["sun-ada.net"],
    "大广赛": ["sun-ada.net"],
}


def check_url(url, timeout=8):
    """检查 URL 是否可访问，返回 (ok, status_code)"""
    if not url:
        return False, 0
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return resp.status_code < 400, resp.status_code
    except requests.exceptions.SSLError:
        # SSL 错误时尝试 HTTP
        if url.startswith("https://"):
            try:
                resp = requests.get(url.replace("https://", "http://"), headers=HEADERS, timeout=timeout, allow_redirects=True)
                return resp.status_code < 400, resp.status_code
            except:
                pass
        return False, 0
    except:
        return False, 0


def search_official_url(competition_name):
    """通过搜索引擎搜索竞赛官网"""
    # 方法1: DuckDuckGo HTML 搜索
    try:
        query = quote_plus(f"{competition_name} 官网")
        url = f"https://html.duckduckgo.com/html/?q={query}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 提取搜索结果链接
        results = soup.select(".result__a")
        for result in results[:5]:
            href = result.get("href", "")
            # DuckDuckGo 的链接格式可能是重定向 URL
            if "uddg=" in href:
                import urllib.parse
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                actual_url = parsed.get("uddg", [""])[0]
                if actual_url and _is_relevant_url(actual_url, competition_name):
                    return actual_url
            elif href.startswith("http") and _is_relevant_url(href, competition_name):
                return href
    except Exception as e:
        print(f"[URL搜索] DuckDuckGo 搜索失败: {e}")
    
    # 方法2: Bing 搜索
    try:
        query = quote_plus(f"{competition_name} 官网")
        url = f"https://www.bing.com/search?q={query}&setlang=zh-CN"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        results = soup.select("li.b_algo h2 a")
        for result in results[:5]:
            href = result.get("href", "")
            if href.startswith("http") and _is_relevant_url(href, competition_name):
                return href
    except Exception as e:
        print(f"[URL搜索] Bing 搜索失败: {e}")
    
    return None


def _is_relevant_url(url, competition_name):
    """判断 URL 是否与竞赛相关"""
    # 排除搜索引擎、社交媒体、广告链接
    exclude_domains = [
        "google.com", "bing.com", "baidu.com", "sogou.com",
        "facebook.com", "twitter.com", "weibo.com", "zhihu.com",
        "bilibili.com", "youtube.com", "github.com",
        "ad.doubleclick.net", "doubleclick.net",
    ]
    url_lower = url.lower()
    for domain in exclude_domains:
        if domain in url_lower:
            return False
    
    # 检查 URL 长度（太短的可能是首页）
    if len(url) < 15:
        return False
    
    return True


def validate_and_discover_urls(competitions):
    """验证所有竞赛的官网链接，挂了的自动搜索新链接
    
    Args:
        competitions: 竞赛列表（每个竞赛需有 name 和 officialUrl 字段）
    
    Returns:
        更新后的竞赛列表 + 统计信息
    """
    stats = {"total": len(competitions), "ok": 0, "fixed": 0, "failed": 0}
    
    for comp in competitions:
        name = comp.get("name", "")
        url = comp.get("officialUrl", "")
        
        # 检查现有 URL
        if url:
            ok, code = check_url(url)
            if ok:
                stats["ok"] += 1
                continue
        
        # URL 失效或不存在，尝试搜索
        print(f"[URL验证] {name[:20]} 的链接失效(code={code if url else 'N/A'})，正在搜索...")
        new_url = search_official_url(name)
        
        if new_url:
            # 验证搜索到的 URL
            ok, code = check_url(new_url)
            if ok:
                comp["officialUrl"] = new_url
                comp["sourceVerified"] = True
                stats["fixed"] += 1
                print(f"[URL验证] ✓ 找到新链接: {new_url}")
            else:
                stats["failed"] += 1
        else:
            # 搜索也没找到，尝试已知域名
            new_url = _try_known_domains(name)
            if new_url:
                ok, code = check_url(new_url)
                if ok:
                    comp["officialUrl"] = new_url
                    comp["sourceVerified"] = True
                    stats["fixed"] += 1
                    print(f"[URL验证] ✓ 从已知域名恢复: {new_url}")
                else:
                    stats["failed"] += 1
            else:
                stats["failed"] += 1
    
    return competitions, stats


def _try_known_domains(competition_name):
    """尝试已知的可靠域名"""
    for keyword, domains in KNOWN_DOMAINS.items():
        if keyword in competition_name:
            for domain in domains:
                url = f"https://{domain}"
                ok, _ = check_url(url)
                if ok:
                    return url
                url = f"http://{domain}"
                ok, _ = check_url(url)
                if ok:
                    return url
    return None


if __name__ == "__main__":
    # 测试
    test_comps = [
        {"name": "ICPC亚洲区域赛", "officialUrl": "https://icpc.pku.edu.cn"},
        {"name": "蓝桥杯软件和信息技术专业人才大赛", "officialUrl": "https://dasai.lanqiao.cn"},
        {"name": "全国大学生数学建模竞赛", "officialUrl": "http://www.mcm.edu.cn"},
    ]
    result, stats = validate_and_discover_urls(test_comps)
    print(f"\n统计: {stats}")
    for comp in result:
        print(f"  {comp['name'][:20]} → {comp['officialUrl']}")
