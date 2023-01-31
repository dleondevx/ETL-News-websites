import argparse
import logging
logging.basicConfig(level=logging.INFO)
import re
import datetime
import csv

from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

from common import config
import news_page_objects as news

logger = logging.getLogger(__name__)
is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$') # some Text

def _fetch_article_though_pages(*args,**kwargs):
    print(*args)
    articles = []
    news_site_uid, host, = args[0], args[1]
    for link in args[2].article_links:
        article = _fetch_article(news_site_uid, host, link)
        logger.info('Article fetched!!')
        articles.append(article)
        print(article.title)
    return articles

def _news_scraper(news_site_uid, pagination = None):
    if pagination:
        host = config()['news_sites'][news_site_uid]['url']+str(pagination) 
    else:
        host = config()['news_sites'][news_site_uid]['url']
    logging.info('Beginning scraper for {}'.format(host))
    logging.info('Finding links in homepage...')
    homepage = news.HomePage(news_site_uid, host)  
    articles = _fetch_article_though_pages(news_site_uid,host,homepage)
    _save_articles(news_site_uid, articles)



def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return '{}{}'.format(host, link)
    elif 'sharer/sharer.php' in link:
        real_host = re.search('u=(.*)', link).group(1)
        return real_host
    else:
        return '{host}/{url}'.format(host=host, url=link)



def _fetch_article(news_site_uid, host, link):
    logger.info('Start fetching article at {}'.format(_build_link(host, link)))

    article = None
    try:
        article = news.ArticlePage(news_site_uid, _build_link(host,link))
        print(article.link)
    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while fechting the article', exc_info=False)
        print(e)

    if article and not article.body:
        logger.warning('Invalid article, There is no body')
        return None
    
    return article


def _save_articles(news_site_uid, articles):
    now = datetime.datetime.now()
    out_file_name = '{news_site_uid}_articles.csv'.format(
            news_site_uid=news_site_uid,
            datetime=now)

    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(articles[0])))

    with open(out_file_name, mode='a+') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for article in articles:
            row = [str(getattr(article,prop)) for prop in csv_headers]
            writer.writerow(row)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    news_site_choices = list(config()['news_sites'].keys())
    parser.add_argument('news_site',
                        help='The news site that you want to scrape',
                        type=str,
                        choices=news_site_choices)

    
    args = parser.parse_args()
    host = args.news_site 

    if True:
        pagination = 'page/'
        for i in range(1,150):
            if i != 1:
                _news_scraper(host, pagination+str(i)+'/')
            else:
                _news_scraper(host)

    else:
        _news_scraper(args.news_site)