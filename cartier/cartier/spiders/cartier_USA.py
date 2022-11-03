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
    name = 'Cartier'
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/106.0.0.0 Safari/537.36"}

    start_urls = ['https://www.cartier.com/en-us/home']
    site = 'https://www.cartier.com'
    execution_id = '621291'
    feed_code = 'aeid5482'
    record_create_by = 'aeid5482_cartier'
    record_create_date = datetime.now()
    source_country = 'USA'

    def parse(self, response):  # fetching all the href present in the site
        attributes = response.css('.header-flyout__tab-viewall a::attr(href)').extract()
        a = ['/en-us/jewelry/all-collections/', '/en-us/jewelry/bracelets/', '/en-us/jewelry/rings/',
             '/en-us/jewelry/necklaces/', '/en-us/jewelry/earrings/',
             '/en-us/jewelry/engagement-rings/', '/en-us/jewelry/wedding-bands/',
             '/en-us/watches/collections/', '/en-us/art-of-living/bags/',
             '/en-us/art-of-living/personal-accessories/',
             '/en-us/art-of-living/home/', '/en-us/art-of-living/writing-%26-stationery/',
             '/en-us/art-of-living/eyewear/',
             '/en-us/art-of-living/fragrances/']
        for j in attributes:
            for k in a:
                if k in j:
                    attr = self.site + j
                    request = Request(url=attr, callback=self.pagination, headers=self.headers)
                    yield request

    def pagination(self, response):  # Going to last page of the products
        last_page = response.css('link[rel="next"]::attr(href)').get()
        if last_page:
            last_page1 = last_page.rsplit('=', 1)[0]
            last_page2 = last_page1 + '=100'
            request = Request(url=last_page2, callback=self.apps, headers=self.headers)
            print(last_page2)
            yield request
        else:
            pass

    def apps(self, response):  # fetching the script and links of individual products
        print(response)
        print(response.url)
        data = response.xpath('//script[@type="application/ld+json"]/text()').get()
        if data:
            data = json.loads(data)
            for i in data['itemListElement']:
                link = i['url']
                request = Request(url=link, callback=self.parse_details, headers=self.headers)
                yield request
        else:
            pass

    # ------Below script is for rendering next page but here we are fetching all page at once------------
    # if response.xpath("//link/@rel='next'").get() == 1 or response.xpath("//link/@rel='next'").get() == '1' :
    #     next_page =  response.follow(url =self.list_url.format(response.url,self.page,self.p),callback=self.parse)
    #     yield next_page
    # -----------------------------------------------------------------------------------------------------
    def parse_details(self, response):  # Getting all details of the products
        print(response)
        print(response.url)
        items = CartierItem()
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
            brd = response.css('a.breadcrumbs__anchor::text').extract()
            brdcrmb = ','.join(brd).replace(',', '/')

            try:
                items['Context_Identifier'] = brdcrmb
            except:
                items['Context_Identifier'] = ''
            try:
                items['Type'] = brd[2]
            except:
                items['Type'] = ''

            if response.css('.text-align-last--center option::text').extract():
                list1 = []
                strng = ','
                for size in response.css('.text-align-last--center option::text').extract()[1:]:
                    sizes = size.replace('\n', '')
                    list1.append(sizes)
                str_lst = strng.join(list1)
                try:
                    items['Available_Size'] = str_lst
                except:
                    items['Available_Size'] = ''
            else:
                items['Available_Size'] = ''

            items['Source'] = response.url

            if response.css('#main .set--hide-click-focus p.font-family--serif::text').extract():
                try:
                    colors = response.css('#main .set--hide-click-focus p.font-family--serif::text').extract()
                    container = []
                    str1 = ','
                    for color in colors:
                        color_s = color.replace('\n', '')
                        container.append(color_s)
                    lst_str = str1.join(container)
                    items['Available_Colors_OR_Size'] = lst_str
                except:
                    items['Available_Colors_OR_Size'] = ''
            else:
                items['Available_Colors_OR_Size'] = ''

            items['Site'] = self.site
            items['Execution_Id'] = environ.get('SHUB_JOBKEY', None)
            items['Feed_Code'] = self.feed_code
            items['Record_Create_By'] = self.record_create_by
            items['Record_Create_Date'] = self.record_create_date
            items['Source_Country'] = self.source_country
            yield items
        else:
            pass
