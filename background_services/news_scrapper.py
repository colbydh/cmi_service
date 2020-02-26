import os
from datetime import time

import newspaper
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CMI_Service.settings")
import django

django.setup()
from newspaper import Article
from webarticles.models import Article as WebArticle

# Grabs the title from the html
from webarticles.models import Site, Url


def get_title(html):
    return ''


# Grabs the description from the html
def get_description(html):
    return ''


# Grabs the site name from the html
def get_site_name(html):
    return ''


def get_site_base_url(html):
    return ''


# Returns the main article data from the given url
def create_article_from_url(url):
    # Get and parse the article
    article = Article(url=url.expanded)

    # Create article
    if WebArticle.objects.filter(expanded_url__icontains=url.expanded).exists():
        rtn_article = WebArticle.objects.get(expanded_url__icontains=url.expanded)
        if not url.article:
            url.article = rtn_article
        url.scraped = True
        url.save()
        return

    rtn_article = get_article_from_article(article, url)

    # Now see if a site exists for this site if not then create one
    try:
        site = Site.objects.get(base_url__exact=article.source_url)
    except:
        if url.canonical != article.canonical_link:
            url.canonical = article.canonical_link
            article = Article(url=url.canonical)
            rtn_article = get_article_from_article(article, url)
            try:
                site = Site.objects.get(base_url__exact=article.source_url)
            except:
                site = Site.objects.create(name=article.meta_data['og']['site_name'], domain=article.source_url,
                                           base_url=article.source_url)
        else:
            site = Site.objects.create(name=article.meta_data['og']['site_name'], domain=article.source_url,
                                       base_url=article.source_url)

    # Add site to url
    rtn_article.save()
    url.site = site
    url.article = rtn_article
    url.scraped = True
    url.save()


# Returns the main article data from the given url
def get_article_from_article(article, url):

    keep_trying = True

    while keep_trying:
        try:
            article.download()
            keep_trying = False
        except Exception as e:
            print(e)
            time.sleep(1)

    article.parse()
    article.nlp()

    return WebArticle(
        expanded_url=url.expanded,
        authors=article.authors,
        keywords=article.keywords,
        lang=article.meta_lang,
        title=article.title,
        meta=article.meta_data,
        text=article.text,
        date_published=article.publish_date
    )


def crawl_sites_getting_news_articles():
    sites = Site.objects.all()

    for site in sites:
        print('Crawling through: ', site.name)

        # Build site
        paper = newspaper.build(site.base_url)

        for article in tqdm(paper.articles, total=paper.size()):

            # See if url already exists in db
            if Url.objects.filter(expanded__icontains=article.url):  # Exists
                url = Url.objects.get(expanded__icontains=article.url)
                if url.article and url.scraped:
                    continue
            else:  # Doesn't exist
                url = Url.objects.create(raw=article.url, expanded=article.url, site=site)

            # Now parse the url for the article and create one
            article = get_article_from_article(article, url)

            # Add the article and site to the url and mark it as scraped
            if article:
                url.article = article
                url.scraped = True
                url.save()


def crawl_unscraped_urls():
    unscraped_urls = Url.objects.filter(scraped=False)

    for url in tqdm(unscraped_urls, total=unscraped_urls.count()):
        create_article_from_url(url)


# Start
if __name__ == '__main__':
    # crawl_sites_getting_news_articles()
    crawl_unscraped_urls()
