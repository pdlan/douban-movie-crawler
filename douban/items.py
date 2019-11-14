# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class CommentItem(scrapy.Item):
    id_ = scrapy.Field()
    movieId = scrapy.Field()
    content = scrapy.Field()
    starNumber = scrapy.Field()
    usefulNumber = scrapy.Field()

class ReviewItem(scrapy.Item):
    id_ = scrapy.Field()
    movieId = scrapy.Field()
    content = scrapy.Field()
    starNumber = scrapy.Field()
    usefulNumber = scrapy.Field()

class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    movieName = scrapy.Field()
    movieURL = scrapy.Field()
    movieType = scrapy.Field()
    pagesComments = scrapy.Field()
    pagesReviews = scrapy.Field()
    #moviePoster = scrapy.Field()
    #movieShower = scrapy.Field()
    #shortRemark = scrapy.Field()
    #longRemark = scrapy.Field()
