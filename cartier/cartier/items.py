# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CartierItem(scrapy.Item):
    Site = scrapy.Field()
    Product_Id = scrapy.Field()
    Product_Title = scrapy.Field()
    Price_Currency = scrapy.Field()
    Product_Price = scrapy.Field()
    Availability = scrapy.Field()
    Description = scrapy.Field()
    Source = scrapy.Field()
    Context_Identifier = scrapy.Field()
    Type = scrapy.Field()
    Available_Colors_OR_Size = scrapy.Field()
    Available_Size = scrapy.Field()
    Execution_Id = scrapy.Field()
    Feed_Code = scrapy.Field()
    Record_Create_By = scrapy.Field()
    Record_Create_Date = scrapy.Field()
    Source_Country = scrapy.Field()
    pass
