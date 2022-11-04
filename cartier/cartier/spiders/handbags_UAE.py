import scrapy
from scrapy import Request
import json
from os import environ
from datetime import datetime
from ..items import HandbagsItem
class ExampleSpider(scrapy.Spider):
    name = 'cartier_handbags_UAE'

    start_urls = ['https://www.cartier.com/en-ae/art-of-living/bags/?page=100']
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/106.0.0.0 Safari/537.36"}
    site = 'https://www.cartier.com'
    execution_id = '621291'
    feed_code = 'aeid5482'
    record_create_by = 'aeid5482_cartier'
    record_create_date = datetime.now()
    source_country = 'UAE'
    def parse(self, response):
        data = response.xpath('//script[@type="application/ld+json"]/text()').get()
        data = json.loads(data)
        for i in data['itemListElement']:
            link = i['url']
            request = Request(url=link, callback=self.parse_details, headers=self.headers)
            yield request

    def parse_details(self,response):
        items = HandbagsItem()
        items['Source'] = response.url
        details = response.xpath('//script[@type="application/ld+json"]/text()').get()
        if details:
            details = json.loads(details)
            try:
                items['Product_Id'] = details['sku']
            except:
                items['Product_Id'] = ''
            items['Product_Title'] = details['name']
            try:
                items['Price_Currency'] = details['offers']['priceCurrency']
            except:
                items['Price_Currency'] = ''
            try:
                items['Product_Price'] = details['offers']['price']
            except:
                try:
                    low_price = str(details['offers']['lowprice']['sales']['value'])
                    high_price = str(details['offers']['highprice']['sales']['value'])
                    all_price = low_price + ' & ' + high_price
                    items['Product_Price'] = all_price
                except:
                    items['Product_Price'] = ''
            items['Availability'] = details['offers']['availability'].strip('https://schema.org/')

            check_desc = response.css('span.pdp-main__description-full::text').get()
            if check_desc:
                check_desc.strip()
                try:
                    items['Description'] = response.css('.pdp-main__description-full::text').extract()[-3].strip()
                except:
                    items['Description'] = response.css('span.pdp-main__description-full::text').get().strip()
            else:
                try:
                    items['Description'] = response.css('.pdp-main__description::text').get()
                except:
                    items['Description'] = ''
            brd = response.css('.breadcrumbs a span::text').extract()
            brdcrmb = ','.join(brd).replace(',', '/')

            try:
                items['Context_Identifier'] = brdcrmb
            except:
                items['Context_Identifier'] = ''
            try:
                items['Product_Id'] = response.css('.small-paragraph .value::text').get().strip()
            except:
                items['Product_Id'] = ''
            if response.css('p.short-description::text').getall():
                colors = response.css('p.short-description::text').getall()
                list1 = []
                strng = ','
                for k in colors:
                    color = k.strip()
                    list1.append(color)
                str_lst = strng.join(list1)
                items['Colors'] = str_lst
            else:
                items['Colors'] = ''
            items['Type'] = 'bags'
            items['Source'] = response.url
            items['Site'] = self.site
            items['Execution_Id'] = environ.get('SHUB_JOBKEY', None)
            items['Feed_Code'] = self.feed_code
            items['Record_Create_By'] = self.record_create_by
            items['Record_Create_Date'] = self.record_create_date
            items['Source_Country'] = self.source_country
            yield items
 

