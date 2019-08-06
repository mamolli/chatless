import asyncio
from pyppeteer import launch
from lxml import html
from urllib.parse import urljoin
import time
from datetime import datetime
from lunchero_utils import stem

# more or less, 
lunch_keywords = (
    'lunch',
    'dzis',
    'poniedzial',
    'wtor',
    'srod',
    'czwart',
    'piat'
)

urls = (
    'https://www.facebook.com/Restauracja-Krowa-i-Kurczak-757603270918750/',
    "https://www.facebook.com/Pizza-pasta-basta-278942949312857/"
)

async def get_url(url: str):
    # browser = await launch(executablePath='chrome-mac/Chromium.app/Contents/MacOS/Chromium')
    if 'posts' not in url:
        posts_url = urljoin(url, 'posts')
    else:
        posts_url = url
    browser = await launch()
    # browser = await launch(executablePath='~/Library/Application Support/pyppeteer/local-chromium/588429/')
    # browser = await launch(executablePath='~/Library/Application\ Support/pyppeteer/local-chromium/588429/chrome-mac/Chromium.app/Contents/MacOS/Chromium')
    page = await browser.newPage()
    await page.goto(posts_url)
    content = await page.content()
    await browser.close()
    posts_data = parse_data(content, posts_url)
    return (url, posts_data)

def parse_data(html_content, html_url):
    lhtml = html.fromstring(html_content)
    post_links = lhtml.cssselect('.timestampContent')
    # extracting some information from html
    posts_data = (extract_post_data(post_link, html_url) for post_link in post_links)
    posts_data = filter_posts(posts_data)
    return posts_data

def run_get_url(url: str):
    return asyncio.get_event_loop().run_until_complete(get_url(url))


async def get_data_from_fb(urls: tuple):
    # loop = asyncio.get_event_loop()
    tasks = (get_url(url) for url in urls)
    data = await asyncio.gather(*tasks)
    return data

def main():
    # url = "https://www.facebook.com/Pizza-pasta-basta-278942949312857/"
    # posts_url = urljoin(url, 'posts')
    # page_html = run_get_url(posts_url)
    # lhtml = html.fromstring(page_html)
    # post_links = lhtml.cssselect('.timestampContent')
    # # extracting some information from html
    # posts_data = (extract_post_data(post_link, posts_url) for post_link in post_links)
    # # posts_data = filter_posts(posts_data)
    # return posts_data
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(get_data_from_fb(urls))
    return data

def filter_posts(posts_data):
    posts_data = tuple(filter(lambda post: _is_date_between(post['post_utc_iso'], *_iso_bounds()), posts_data))
    # do not filter if only one result left, most likely its correct :)
    if len(posts_data) > 1:
        posts_data = filter(lambda post: _is_lunch_post(post), posts_data)
    return posts_data

def _is_lunch_post(post):
    return any(keyword in stem(post.get('post_text', '')) for keyword in lunch_keywords)

def extract_post_data(post_link, posts_url):
    post, link = None, None
    for el in post_link.iterancestors():
        if "userContentWrapper" in el.classes:
            post = el
        if ("rel", "theater") in el.attrib.items():
            link = el
        if post and link:
            break
    post_epoch = post_link.getparent().attrib.get('data-utime')
    post_epoch = time.mktime(time.gmtime(int(post_epoch))) if post_epoch else None
    post_utc_iso = datetime.fromtimestamp(post_epoch).isoformat()
    post_link_url = urljoin(posts_url, link.attrib['href'])
    post_text = post.text_content()
    return {"post_utc_iso": post_utc_iso, "post_url": post_link_url, "post_text": post_text}

def _iso_bounds():
    now = datetime.now()
    lower = now.replace(hour=5, minute=0, second=0)
    higher = now.replace(hour=13, minute=30, second=0)
    return lower.isoformat(), higher.isoformat()

def _is_date_between(iso_dt, iso_dt_compare_low=None, iso_dt_compare_high=None):
    dt = datetime.fromisoformat(iso_dt)
    assert iso_dt_compare_low or iso_dt_compare_high
    dt_low = datetime.fromisoformat(iso_dt_compare_low) if iso_dt_compare_low else datetime.min
    dt_high = datetime.fromisoformat(iso_dt_compare_high) if iso_dt_compare_high else datetime.max
    between = dt_low < dt < dt_high
    return between
    

def phrase_text(text, phrases):
    naive_check = any(phrase in text for phrase in phrases)
    return naive_check
