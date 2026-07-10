import sys; sys.path.insert(0,'.')
from crawlers.seed_data import get_seed_competitions
import requests

for s in get_seed_competitions():
    url = s.get('officialUrl', '')
    name = s.get('name', '')[:25]
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        status = r.status_code
    except Exception as e:
        status = f'FAIL: {type(e).__name__}'
    print(f'{name:25s} | {status} | {url}')
