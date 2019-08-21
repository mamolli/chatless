from lxml import html
from urllib.parse import urljoin
import time
import logging
import json
import boto3
import asyncio
from datetime import datetime
from chatless.lunchero_utils import stem

# try:
#     from pyppeteer import launch

#     def get_html_p(url):
#         async def helper_(url):
#             browser = await launch()
#             page = await browser.newPage()
#             await page.goto(url)
#             content = await page.content()
#             await browser.close()
#             return content
#         return asyncio.run(helper_(url))
# except Exception:
#     pass

log = logging.getLogger()
# log.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
log.setLevel(logging.INFO)

SCRAPPER_ARN = "arn:aws:lambda:us-east-1:622177633957:function:ts-scrapper-dev-vanilla"

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


def get_html_l(url):
    client = boto3.client("lambda")
    response = client.invoke(
        FunctionName=SCRAPPER_ARN,
        InvocationType='Event',
        Payload=json.dumps({'queryStringParameters': {'url': url}})
    )
    data = response['Payload'].read()
    content = json.loads(data).get('body')
    return content

def get_url(url: str):
    if 'posts' not in url:
        posts_url = urljoin(url, 'posts')
    else:
        posts_url = url

    content = get_html_l(posts_url)
    log.info("getting browser for: %s", url)
    log.error("Content %s", content[:200])
    posts_data = parse_data(content, posts_url)
    log.info("Getting posts data %s", posts_data)
    return (url, posts_data)

def parse_data(html_content, posts_url):
    lhtml = html.fromstring(html_content)
    log.info(dir(lhtml))
    post_links = lhtml.cssselect('.timestampContent')
    posts_data = (extract_post_data(post_link, posts_url) for post_link in post_links)
    posts_data = filter_posts(posts_data)
    return posts_data

def run(urls: tuple):
    log.info("Starting async loop")
    # return asyncio.get_event_loop().run_until_complete(get_url(urls[0]))
    return asyncio.run(get_data_from_fb(urls))

async def get_data_from_fb(urls: tuple):
    # loop = asyncio.get_event_loop()
    log.info("getting fb data from: %s", urls)
    tasks = (get_url(url) for url in urls)
    data = await asyncio.gather(*tasks)
    log.info("finished waiting")
    return data

def filter_posts(posts_data):
    posts_data = list(posts_data)
    if len(posts_data) > 1: 
        posts_data = list(filter(lambda post: _is_date_between(post['post_utc_iso'], *_iso_bounds()), posts_data))
    if len(posts_data) > 1:
        posts_data = list(filter(lambda post: _is_lunch_post(post), posts_data))
    return posts_data

def _is_lunch_post(post):
    return any(keyword in stem(post.get('post_text', '')) for keyword in lunch_keywords)

def extract_post_data(post_link, fb_url):
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
    # sadly post_url can be null
    # log.info(dir(link))
    post_link_url = urljoin(fb_url, link.attrib.get('href')) if link else None
    post_text = post.text_content()

    return {"fb_url": fb_url, "post_utc_iso": post_utc_iso, "post_url": post_link_url, "post_text": post_text}

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
