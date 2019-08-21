from urllib.parse import urljoin
import time
import logging
import json
import boto3
import re
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
    log.error("Starting call for url %s", url)
    response = client.invoke(
        FunctionName=SCRAPPER_ARN,
        InvocationType='RequestResponse',
        Payload=json.dumps({'queryStringParameters': {'url': url}})
    )
    data = response['Payload'].read()
    content = json.loads(data).get('body')
    return content

async def get_url(url: str):
    loop = asyncio.get_event_loop()
    if 'posts' not in url:
        posts_url = urljoin(url, 'posts')
    else:
        posts_url = url

    content = await loop.run_in_executor(None, get_html_l, posts_url)
    log.info("getting browser for: %s", url)
    posts = filter_posts(content)
    # shit we have to do::::::
    for p in posts:
        if p.get('link'):
            p['link'] = re.sub(r"\?.*", "", p['link'])
    return (url, posts)


def run(urls: tuple):
    log.info("Starting async loop")
    return asyncio.run(get_data_from_fb(urls)) 
    # return asyncio.get_event_loop().run_until_complete(get_data_from_fb(urls))
    # return asyncio.run(get_data_from_fb(urls))

async def get_data_from_fb(urls: tuple):
    # loop = asyncio.get_event_loop()
    log.info("getting fb data from: %s", urls)
    tasks = (get_url(url) for url in urls)
    data = await asyncio.gather(*tasks)
    return data

def filter_posts(posts):
    if len(posts) > 1:
        posts = list(filter(lambda post: _is_date_between(post['utcEpoch'], *_iso_bounds()), posts))
    if len(posts) > 1:
        posts = list(filter(lambda post: _is_lunch_post(post), posts))
    log.info("All 3posts: %s", list(posts))
    return posts

def _is_lunch_post(post):
    return any(keyword in stem(post.get('post_text', '')) for keyword in lunch_keywords)

def _iso_bounds():
    now = datetime.now()
    lower = now.replace(hour=5, minute=0, second=0)
    higher = now.replace(hour=13, minute=30, second=0)
    return lower.isoformat(), higher.isoformat()

def _is_date_between(utcepoch, iso_dt_compare_low=None, iso_dt_compare_high=None):
    dt = datetime.fromtimestamp(utcepoch)
    assert iso_dt_compare_low or iso_dt_compare_high
    dt_low = datetime.fromisoformat(iso_dt_compare_low) if iso_dt_compare_low else datetime.min
    dt_high = datetime.fromisoformat(iso_dt_compare_high) if iso_dt_compare_high else datetime.max
    between = dt_low < dt < dt_high
    return between
    

def phrase_text(text, phrases):
    naive_check = any(phrase in text for phrase in phrases)
    return naive_check
