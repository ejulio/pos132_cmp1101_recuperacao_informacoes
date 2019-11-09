from datetime import datetime

import scrapy

from quotes.items import QuotesItem


class QuotesToscrapeComSpider(scrapy.Spider):
    name = 'quotes.toscrape.com'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    author = None

    def parse(self, response):
        for (i, quote) in enumerate(response.css('.quote')):
            text = quote.css('.text::text').get()
            author = quote.css('.author::text').get()
            if not self.author or author == self.author:
                yield QuotesItem(
                    text=text,
                    author=author,
                    url=response.url,
                    rank=i,
                    scrape_date=datetime.now().isoformat()
                )
        url = response.css(
            '.pager .next a::attr(href)'
        ).get()
        if url:
            yield response.follow(url)
