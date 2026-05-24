"""
本地执行脚本: 从 Wikipedia REST API 抓 99 国地标主图 URL, 写入 countries.db

用法:
    python fetch_wiki_images.py

依赖: 只用 Python 标准库, 无需 pip install.

流程:
    1) 读 data/country_wiki_targets.py 的 99 条 (国名 -> Wikipedia 词条)
    2) 对每条调用 https://en.wikipedia.org/api/rest_v1/page/summary/{词条}
    3) 从返回 JSON 里读 thumbnail.source (主图 URL, 通常 320px)
    4) 把 URL 里的 /320px- 替换为 /1280px-, 拿到更大尺寸的图
    5) UPDATE countries SET image_url = ? WHERE name = ?

输出: 每条形如:
    [ 1/99] ✓ 法国    -> Eiffel_Tower     https://upload.wikimedia.org/...
    [ 2/99] ✗ 意大利  -> Colosseum        (词条无主图)

失败的国家不写 image_url, 前端会自动 fallback 到 SVG.
"""
import sqlite3
import sys
import os
import time
import json
import re
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data.country_wiki_targets import COUNTRY_WIKI_TARGETS

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'countries.db')
API_TEMPLATE = 'https://en.wikipedia.org/api/rest_v1/page/summary/{title}'
HEADERS = {
    'User-Agent': 'AtlasMundi/1.0 (educational world map; local dev)',
    'Accept': 'application/json',
}
TIMEOUT = 15


def upscale_url(url: str, target_width: int = 1280) -> str:
    """
    Wikimedia thumbnail URL 通常形如:
      https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Tour_Eiffel.JPG/320px-Tour_Eiffel.JPG
    把其中的 /320px- (或 /NNNpx-) 改成 /1280px- 即可拿大图.
    若 URL 无 /NNpx- 段则原样返回.
    """
    return re.sub(r'/\d+px-', f'/{target_width}px-', url)


def fetch_one(title: str):
    """返回 (image_url, error_msg). 成功时 error_msg=None."""
    url = API_TEMPLATE.format(title=title)
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        return None, f'HTTP {e.code}'
    except URLError as e:
        return None, f'网络 {e.reason}'
    except Exception as e:
        return None, f'其他 {e!r}'
    
    thumb = (data.get('thumbnail') or {}).get('source')
    orig = (data.get('originalimage') or {}).get('source')
    img = thumb or orig
    if not img:
        return None, '词条无主图'
    return upscale_url(img, 1280), None


def main():
    print('=' * 70)
    print('Atlas Mundi · 99 国 Wikipedia 地标图片抓取')
    print('=' * 70)
    print(f'目标: {len(COUNTRY_WIKI_TARGETS)} 国')
    print(f'数据库: {DB_PATH}')
    print('-' * 70)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # 先清空旧的 image_url, 防止上轮残留
    cur.execute('UPDATE countries SET image_url = NULL')
    conn.commit()

    ok, fail = [], []
    items = list(COUNTRY_WIKI_TARGETS.items())

    for idx, (cn_name, (title, desc)) in enumerate(items, 1):
        # 确认国家存在数据库
        cur.execute('SELECT id FROM countries WHERE name = ?', (cn_name,))
        if not cur.fetchone():
            print(f'[{idx:2d}/{len(items)}] ⚠ {cn_name} 不在数据库, 跳过')
            continue

        img_url, err = fetch_one(title)
        if img_url:
            cur.execute('UPDATE countries SET image_url = ? WHERE name = ?',
                        (img_url, cn_name))
            conn.commit()
            ok.append((cn_name, title, desc))
            short = img_url if len(img_url) <= 85 else img_url[:82] + '...'
            print(f'[{idx:2d}/{len(items)}] ✓ {cn_name:8s} -> {title:38s} {short}')
        else:
            fail.append((cn_name, title, desc, err))
            print(f'[{idx:2d}/{len(items)}] ✗ {cn_name:8s} -> {title:38s} ({err})')

        time.sleep(0.1)  # 礼貌延迟

    conn.close()

    print('-' * 70)
    print(f'成功 {len(ok)} 国 / 失败 {len(fail)} 国')

    if fail:
        print('\n失败清单 (前端会走 SVG fallback):')
        for cn_name, title, desc, err in fail:
            print(f'  ✗ {cn_name} ({desc}) -> {title}: {err}')
        print('\n若要重试, 编辑 data/country_wiki_targets.py 修改词条名后再次运行.')

    print('\n[完成] 重启 uvicorn 并强制刷新浏览器即可查看效果.')


if __name__ == '__main__':
    main()
