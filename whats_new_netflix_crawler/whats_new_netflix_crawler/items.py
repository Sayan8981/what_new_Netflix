# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WhatsNewNetflixCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    netflix_id=scrapy.Field()
    title=scrapy.Field()
    image=scrapy.Field()
    imdb_rating=scrapy.Field()
    url=scrapy.Field()
    content_type=scrapy.Field()
    show_type=scrapy.Field()
    season_number=scrapy.Field()
    year=scrapy.Field()
    tv_rating=scrapy.Field()
    description=scrapy.Field()
    genre=scrapy.Field()
    cast=scrapy.Field()
    director=scrapy.Field()
    runtime=scrapy.Field()
    language=scrapy.Field()
    updated_db=scrapy.Field()
    item_category=scrapy.Field()


