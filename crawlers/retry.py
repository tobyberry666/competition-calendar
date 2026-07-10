"""
HTTP请求重试机制
处理网络异常：ConnectionError、Timeout、HTTPError(5xx)
"""
import requests
import time
from requests.exceptions import ConnectionError, Timeout, HTTPError


def retry_get(url, headers=None, timeout=10, max_retries=3, backoff=1):
    """
    带重试的HTTP GET请求
    
    Args:
        url: 请求URL
        headers: 请求头
        timeout: 超时时间(秒)
        max_retries: 最大重试次数
        backoff: 退避基数(秒)
    
    Returns:
        requests.Response: 成功响应
    
    Raises:
        最后一次重试的异常
    """
    last_exception = None
    
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()  # 检查HTTP错误状态码
            return resp
        except (ConnectionError, Timeout, HTTPError) as e:
            last_exception = e
            if attempt < max_retries:
                wait_time = backoff * attempt
                print(f'[重试] 第{attempt}次尝试 {url}')
                time.sleep(wait_time)
            else:
                print(f'[重试] 第{attempt}次尝试失败 {url}: {e}')
    
    raise last_exception
