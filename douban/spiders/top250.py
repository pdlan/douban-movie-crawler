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

class Top250Spider(scrapy.Spider):
    name = 'top250'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250?start=%d' % (i * 25) for i in range(10)]
    handle_httpstatus_list = [200, 403, 301, 302, 404, 429, 500]

    def parse(self, response):
        for url in response.selector.re(r'https://movie.douban.com/subject/\d+/'):
            yield scrapy.Request(url, callback=self.parse_movie_subject)

    def parse_movie_subject(self, response):
        url = response.url
        movie_id = url[33:-1]
        movie_name = response.selector.xpath('//span[contains(@property, "v:itemreviewed")]/text()').extract_first()
        movie_type = ' / '.join(response.selector.xpath('//span[contains(@property, "v:genre")]/text()').extract())
        url_poster = 'https://movie.douban.com/subject/%s/photos?type=R' % movie_id
        url_trailer = 'https://movie.douban.com/subject/%s/trailer' % movie_id
        num_comments = int(response.selector.xpath('//div[contains(@id, "comments-section")]//span[contains(@class, "pl")]/a/text()').extract_first()[3:-2])
        pages_comments = num_comments // 20
        num_reviews = int(response.selector.xpath('//section[contains(@class, "reviews")]//span[contains(@class, "pl")]/a/text()').extract_first()[3:-2])
        pages_reviews = num_reviews // 20
        item = DoubanItem()
        item['movieName'] = movie_name
        item['movieURL'] = url
        item['movieType'] = movie_type
        item['pagesComments'] = pages_comments
        item['pagesReviews'] = pages_reviews
        yield {'type': 'movie', 'item': item}
        yield scrapy.Request(url_poster, meta={'movie_id': movie_id, 'page': 0}, callback=self.parse_poster, priority=10)
        yield scrapy.Request(url_trailer, meta={'movie_id': movie_id}, callback=self.parse_trailer, priority=10)

    def parse_poster(self, response):
        movie_id = response.meta['movie_id']
        page = response.meta['page']
        posters = response.selector.re(r'https://movie.douban.com/photos/photo/\d+/')
        yield {'type': 'posters', 'movie_id': movie_id, 'posters': posters}
        if page == 0:
            n = response.selector.xpath('//span[contains(@class, "count")]/text()').extract_first()
            if n == None:
                n = 1
            else:
                n = int(n[2:-2])
            pages = n // 30
            for i in range(1, pages):
                url = 'https://movie.douban.com/subject/%s/photos?type=R&start=%d' % (movie_id, i * 30)
                yield scrapy.Request(url, meta={'page': i, 'movie_id': movie_id}, callback=self.parse_poster, priority=10)

    def parse_trailer(self, response):
        movie_id = response.meta['movie_id']
        trailers = response.selector.re(r'https://movie.douban.com/trailer/\d+/')
        yield {'type': 'trailers', 'movie_id': movie_id, 'trailers': trailers}