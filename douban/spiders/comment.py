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

class CommentSpider(scrapy.Spider):
    name = 'comment'
    allowed_domains = ['movie.douban.com']
    handle_httpstatus_list = [200, 403, 301, 302, 404, 429, 500]
    start_urls = json.loads(open('tmp_urls').read())

    def parse(self, response):
        movie_id = response.selector.re(r'https://movie.douban.com/subject/\d+/')[0][33:-1]
        comments = []
        for comment in response.css('.comment-item'):
            id_ = comment.xpath('@data-cid').extract_first()
            votes = comment.xpath('.//span[contains(@class, "votes")]/text()').extract_first()
            content = comment.xpath('.//span[contains(@class, "short")]/text()').extract_first()
            rank = comment.xpath('.//span[contains(@class, "rating")]/@title').extract_first()
            rank_dict = {
                '力荐': '5',
                '推荐': '4',
                '还行': '3',
                '较差': '2',
                '很差': '1'
            }
            star = rank_dict.get(rank, '5')
            comment_item = CommentItem()
            comment_item['movieId'] = movie_id
            comment_item['id_'] = id_
            comment_item['content'] = content
            comment_item['starNumber'] = star
            comment_item['usefulNumber'] = votes
            comments.append(comment_item)
        yield {'type': 'comments', 'movie_id': movie_id, 'comments': comments}