BOT_NAME = 'quotes'

SPIDER_MODULES = ['quotes.spiders']
NEWSPIDER_MODULE = 'quotes.spiders'

ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 16
AUTOTHROTTLE_ENABLED = True