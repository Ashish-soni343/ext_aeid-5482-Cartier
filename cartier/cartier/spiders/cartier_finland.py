from scrapy import Request
import scrapy
import json
from ..items import CartierItem
from datetime import datetime
from os import environ

custom_settings = {
    'SCHEDULER_PRIORITY_QUEUE': 'scrapy.pqueues.DownloaderAwarePriorityQueue',
    'REACTOR_THREADPOOL_MAXSIZE': '20',
    'LOG_LEVEL': 'INFO',
    'RETRY_ENABLED': 'False',
    'DOWNLOAD_TIMEOUT': '99999999',
    'REDIRECT_ENABLED': 'False',
    'AJAXCRAWL_ENABLED': 'True',
    'CONCURRENT_REQUESTS_PER_DOMAIN': '2',
    'DNS_RESOLVER': 'scrapy.resolver.CachingThreadedResolver',
    'DUPEFILTER_CLASS': "scrapy.dupefilters.BaseDupeFilter",
    'AUTOTHROTTLE_ENABLED': 'False'
}


class ProSpider(scrapy.Spider):  # class to initiate spider with required values
    name = 'Cartier_Finland'
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/106.0.0.0 Safari/537.36", 'Accept-Language': 'en'}

    start_urls = ['https://www.cartier.com/en-fi/jewellery','https://www.cartier.com/en-fi/watches','https://www.cartier.com/en-fi/bags','https://www.cartier.com/en-fi/accessories',
            'https://www.cartier.com/en-fi/art-of-living-home','https://www.cartier.com/en-fi/writing-and-stationery',
            'https://www.cartier.com/en-fi/eyewear','https://www.cartier.com/en-fi/fragrances']
    site = 'https://www.cartier.com'
    execution_id = '621291'
    feed_code = 'aeid5482'
    record_create_by = 'aeid5482_cartier'
    record_create_date = datetime.now()
    source_country = 'Finland'

    def parse(self, response):  # fetching all the href present in the site
        a = response.css('.shelf-element__btn a::attr(href)').getall()
        if a:
            for links in a:
                request = Request(url=links, callback=self.pagination, headers=self.headers)
                yield request
        else:
            request = Request(url=response.url, callback=self.pagination, headers=self.headers)
            yield request

    def pagination(self, response):  # Going to last page of the products
        k = response.css('.loadMoreProductsButton a::attr(href)').get()
        l = response.css('.product-slot__info a::attr(href)').getall()
        for link in l:
            yield Request(url=link, callback=self.scrape, headers=self.headers)
        if k:
            request = Request(url=k, callback=self.pagination, headers=self.headers)
            yield request

    def scrape(self, response):
        items = CartierItem()
        try:
            items['Product_Title'] = response.css('.item-info__name.heading-1::text').get().strip()
        except:
            items['Product_Title'] = ''
        try:
            items['Description'] = response.css('.editorialdescription .value::text').get().strip()
        except:
            items['Description'] = ''
        try:
            items['Product_Price'] = response.css('.price .value::text').get().strip()
        except:
            items['Product_Price'] = ''
        try:
            items['Price_Currency'] = response.css('.currency::text').get().strip()
        except:
            items['Price_Currency'] = ''
        try:
            items['Context_Identifier'] = ''
        except:
            items['Context_Identifier'] = ''

        if response.css('select option::text').getall():
            size = response.css('select option::text').getall()
            list1 = []
            strng = ','
            for k in size:
                sizes = k.strip()
                list1.append(sizes)
            str_lst = strng.join(list1)
            try:
                items['Available_Size'] = str_lst
            except:
                items['Available_Size'] = ''
            else:
                items['Available_Size'] = ''
        items['Availability'] = response.css('.js-btn span::text').get()
        items['Product_Id'] = response.css('.small-paragraph .value::text').get().strip()

        yield items