import scrapy
from scrapy import Request
import json
from os import environ
from datetime import datetime
from ..items import HandbagsItem


class ExampleSpider(scrapy.Spider):
    name = 'cartier_handbags_ES'

    start_urls = ['https://www.cartier.com/en-es/bags']
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/106.0.0.0 Safari/537.36"}
    site = 'https://www.cartier.com'
    execution_id = '621291'
    feed_code = 'aeid5482'
    record_create_by = 'aeid5482_cartier'
    record_create_date = datetime.now()
    source_country = 'Spain'

    def parse(self, response):  # Going to last page of the products
        k = response.css('.loadMoreProductsButton a::attr(href)').get()
        l = response.css('.product-slot__info a::attr(href)').getall()
        for link in l:
            yield Request(url=link, callback=self.parse_details, headers=self.headers)
        if k:
            request = Request(url=k, callback=self.parse, headers=self.headers)
            yield request

    def parse_details(self, response):
        items = HandbagsItem()
        items['Source'] = response.url
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


        brd = response.css('.breadcrumbs a span::text').extract()
        brdcrmb = ','.join(brd).replace(',', '/')
        try:
            items['Context_Identifier'] = brdcrmb
        except:
            items['Context_Identifier'] = ''
        try:
            items['Type'] = 'bags'
        except:
            items['Type'] = ''
        if response.css('.js-btn span::text').get():
            items['Availability'] = 'InStock'
        else:
            items['Availability'] = 'OutofStock'
        try:
            items['Product_Id'] = response.css('.small-paragraph .value::text').get().strip()
        except:
            items['Product_Id'] = ''
        items['Site'] = self.site
        items['Execution_Id'] = environ.get('SHUB_JOBKEY', None)
        items['Feed_Code'] = self.feed_code
        items['Record_Create_By'] = self.record_create_by
        items['Record_Create_Date'] = self.record_create_date
        items['Source_Country'] = self.source_country
        yield items

