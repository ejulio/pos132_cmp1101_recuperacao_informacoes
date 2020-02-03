import scrapy


class QuotesSpider(scrapy.Spider):
    name = 'quotes.toscrape.com'
    start_urls = ['http://quotes.toscrape.com/']

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield scrapy.Request(url)

    def parse(self, response):
        for quote in response.css('.quote'):
            frase = quote.css('.text::text').get()
            autor = quote.css('.author::text').get()
            href = quote.css('.author + a::attr(href)').get()
            href = response.urljoin(href)
            yield scrapy.Request(
                href,
                dont_filter=True,
                callback=self.parse_autor,
                meta={
                    'dados': {
                        'frase': frase,
                        'autor': autor
                    }
                }
            )
        
        href = response.css('.next a::attr(href)').get()
        if href:
            yield response.follow(
                href,
                callback=self.parse
            )

    def parse_autor(self, response):
        data = response.css(
            '.author-born-date::text'
        ).get()
        dados = response.meta['dados']
        dados['data'] = data
        return dados
