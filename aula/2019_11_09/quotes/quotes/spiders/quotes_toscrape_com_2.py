from datetime import datetime

import scrapy

from quotes.items import QuotesItem


class QuotesToscrapeComSpider(scrapy.Spider):
    name = 'quotes.toscrape.com_2'
    allowed_domains = ['quotes.toscrape.com']
    
    author = None

    def start_requests(self):
        yield scrapy.Request(
            'http://quotes.toscrape.com/',
            callback=self.parse_quotes
        )

    def parse_quotes(self, response):
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
            yield response.follow(
                url,
                callback=self.parse_quotes
            )
