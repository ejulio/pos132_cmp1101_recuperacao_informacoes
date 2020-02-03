import scrapy


class BooksSpider(scrapy.Spider):

    name = 'books.toscrape.com'
    start_urls = ['http://books.toscrape.com']

    def parse(self, response):
        for book in response.css('.product_pod'):
            href = book.css('h3 a::attr(href)').get()
            yield response.follow(
                href,
                callback=self.parse_book
            )

        href = response.css('.next a::attr(href)').get()
        if href:
            yield response.follow(
                href,
                callback=self.parse
            )

    def parse_book(self, response):
        titulo = response.css(
            '.product_main h1::text'
        ).get()
        desc = response.css(
            '#product_description + p::text'
        ).get()
        return {
            'url': response.url,
            'titulo': titulo,
            'descricao': desc
        }