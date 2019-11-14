# -*- coding: utf-8 -*-
import scrapy
import re
import urllib
import json
import time
import random
import logging
import math
from douban.items import *

class ReviewSpider(scrapy.Spider):
    name = 'review'
    allowed_domains = ['movie.douban.com']
    handle_httpstatus_list = [200, 403, 301, 302, 404, 429, 500]
    start_urls = json.loads(open('tmp_urls').read())

    def parse(self, response):
        movie_id = response.selector.re(r'https://movie.douban.com/subject/\d+/')[0][33:-1]
        for review in response.css('.review-item'):
            url = review.xpath('.//div[contains(@class, "main-bd")]/h2/a/@href').extract_first()
            id_ = url[32:-1]
            votes = '/'.join([x.strip() for x in review.xpath('.//a[contains(@class, "action-btn")]/span/text()').extract()])
            rank = review.xpath('.//span[contains(@class, "main-title-rating")]/@title').extract_first()
            rank_dict = {
                '力荐': '5',
                '推荐': '4',
                '还行': '3',
                '较差': '2',
                '很差': '1'
            }
            star = rank_dict.get(rank, '5')
            review_item = ReviewItem()
            review_item['id_'] = id_
            review_item['movieId'] = movie_id
            review_item['starNumber'] = star
            review_item['usefulNumber'] = votes
            url_content = 'https://movie.douban.com/j/review/%s/full' % id_
            yield scrapy.Request(url_content, meta={'item': review_item}, callback=self.parse_content, priority=100)

    def parse_content(self, response):
        item = response.meta['item']
        item['content'] = json.loads(response.body)['body']
        yield {'type': 'review', 'review': item}