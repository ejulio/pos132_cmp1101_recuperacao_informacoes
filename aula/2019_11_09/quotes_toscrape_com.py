import scrapy


class QuotesToscrapeComSpider(scrapy.Spider):
    name = 'quotes.toscrape.com'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        for quote in response.css('.quote'):
            text = quote.css('span.text::text').get()
            author = quote.css('.author::text').get()
            yield {
                'text': text,
                'author': author
            }
        url = response.css(
            '.pager .next a::attr(href)'
        ).get()
        #if url is not None:
        if url:
            yield response.follow(url)
