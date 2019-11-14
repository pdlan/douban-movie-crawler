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

class Top2502Spider(scrapy.Spider):
    name = 'top2502'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250?start=%d' % (i * 25) for i in range(10)]
    handle_httpstatus_list = [200, 403, 301, 302, 404]

    def __init__(self, max_pages=100):
        self.max_pages = int(max_pages)

    def parse(self, response):
        if not self.state.get('state_init', False):
            self.state['state_init'] = True
            self.state['movie_name'] = {}
            self.state['movie_finished'] = []
            self.state['num_posters_need'] = {}
            self.state['num_posters_finished'] = {}
            self.state['posters_finished'] = {}
            self.state['trailers_finished'] = {}
        for url in response.selector.re(r'https://movie.douban.com/subject/\d+/'):
            yield scrapy.Request(url, callback=self.parse_movie_subject)

    def parse_movie_subject(self, response):
        url = response.url
        movie_id = url[33:-1]
        movie_name = response.selector.xpath('//span[contains(@property, "v:itemreviewed")]/text()').extract_first()
        movie_type = ' / '.join(response.selector.xpath('//span[contains(@property, "v:genre")]/text()').extract())
        item = DoubanItem()
        item['movieName'] = movie_name
        item['movieURL'] = url
        item['movieType'] = movie_type
        url_poster = 'https://movie.douban.com/subject/%s/photos?type=R' % movie_id
        url_trailer = 'https://movie.douban.com/subject/%s/trailer' % movie_id
        num_comments = int(response.selector.xpath('//div[contains(@id, "comments-section")]//span[contains(@class, "pl")]/a/text()').extract_first()[3:-2])
        pages_comments = min(num_comments // 20, self.max_pages)
        num_reviews = int(response.selector.xpath('//section[contains(@class, "reviews")]//span[contains(@class, "pl")]/a/text()').extract_first()[3:-2])
        pages_reviews = min(num_reviews // 20, self.max_pages)
        self.state['movie_name'][movie_id] = movie_name
        self.state['posters_finished'][movie_id] = False
        self.state['trailers_finished'][movie_id] = False
        yield {'type': 'movie', 'item': item}
        yield scrapy.Request(url_poster, meta={'movie_id': movie_id, 'page': 0}, callback=self.parse_poster, priority=10)
        yield scrapy.Request(url_trailer, meta={'movie_id': movie_id}, callback=self.parse_trailer, priority=10)
        for i in range(pages_comments):
            url_comment = 'https://movie.douban.com/subject/%s/comments?start=%d' % (movie_id, i * 20)
            yield scrapy.Request(url_comment, meta={'movie_id': movie_id}, callback=self.parse_comment, priority=-i-1)
        for i in range(pages_reviews):
            url_review = 'https://movie.douban.com/subject/%s/reviews?start=%d' % (movie_id, i * 20)
            yield scrapy.Request(url_review, meta={'movie_id': movie_id}, callback=self.parse_review, priority=-i-1)

    def parse_poster(self, response):
        movie_id = response.meta['movie_id']
        page = response.meta['page']
        posters = response.selector.re(r'https://movie.douban.com/photos/photo/\d+/')
        yield {'type': 'posters', 'movie_id': movie_id, 'posters': posters}
        #self.state['num_posters_finished'][movie_id] = self.state['num_posters_finished'].get(movie_id, 0) + 1
        #if page == 0:
        #    n = int(response.selector.xpath('//span[contains(@class, "count")]/text()').extract_first()[2:-2])
        #    pages = n // 30
        #    self.state['num_posters_need'][movie_id] = pages
        #    if self.state['num_posters_finished'][movie_id] == pages:
        #        self.state['posters_finished'][movie_id] = True
        #    if self.state['posters_finished'][movie_id] and self.state['trailers_finished'][movie_id]:
        #        self.state['movie_finished'].append(movie_id)
        #        logging.info('Crawled basic information of movie %s, %d/250' % (self.state['movie_name'][movie_id], len(self.state['movie_finished']) + 1))
        #    for i in range(1, n):
        #        url = 'https://movie.douban.com/subject/%s/photos?type=R&start=%d' % (movie_id, i * 30)
        #        yield scrapy.Request(url, meta={'page': i, 'movie_id': movie_id}, callback=self.parse_poster, priority=10)
        #else:
        #    if self.state['num_posters_finished'][movie_id] == self.state['num_posters_need'][movie_id]:
        #        self.state['posters_finished'][movie_id] = True
        #    if self.state['posters_finished'][movie_id] and self.state['trailers_finished'][movie_id]:
        #        self.state['movie_finished'].append(movie_id)
        #        logging.info('Crawled basic information of movie %s, %d/250' % (self.state['movie_name'][movie_id], len(self.state['movie_finished']) + 1))

    def parse_trailer(self, response):
        movie_id = response.meta['movie_id']
        trailers = response.selector.re(r'https://movie.douban.com/trailer/\d+/')
        self.state['trailers_finished'][movie_id] = True
        if self.state['posters_finished'][movie_id]:
            self.state['movie_finished'].append(movie_id)
            logging.info('Crawled basic information of movie %s, %d/250' % (self.state['movie_name'][movie_id], len(self.state['movie_finished']) + 1))
        yield {'type': 'trailers', 'movie_id': movie_id, 'trailers': trailers}

    def parse_comment(self, response):
        page = response.meta['page']
        movie_id = response.meta['movie_id']
        comments = []
        for comment in response.css('.comment-item'):
            id_ = comment.xpath('.//div[contains(@class, "comment-item")]/@data-cid').extract_first()
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
        logging.info('Crawling review page#%d of movie#%s' % (page, movie_id))
        yield {'type': 'comments', 'movie_id': movie_id, 'comments': comments}

    def parse_review(self, response):
        page = response.meta['page']
        movie_id = response.meta['movie_id']
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
        logging.info('Crawling review page#%d of movie#%s' % (page, movie_id))

    def parse_content(self, response):
        item = response.meta['item']
        item['content'] = json.loads(response.body)['body']
        yield {'type': 'review', 'review': item}

#class MovieSpider(scrapy.Spider):
#    name = 'movie'
#    allowed_domains = ['movie.douban.com']
#    start_urls = ['https://movie.douban.com/top250']
#
#    def parse(self, response):
#        urls = response.selector.re(r'https://movie.douban.com/subject/\d+/')
#        yield {'urls': urls}
#        for url in urls:
#            yield scrapy.Request(url, callback=self.parse_movie)
#
#    def parse_movie(self, response):
#        users = response.selector.css('.review-item').re(r'https://www.douban.com/people/[a-zA-Z0-9_-]+/')
#        for user in users:
#            url_user = 'https://movie.douban.com/people/%s/collect' % user[30:-1]
#            yield scrapy.Request(url_user, callback=self.parse_user)
#
#    def parse_user(self, response):
#        next_page = response.xpath('//a[contains(text(), "后页 >")]/@href').extract_first()
#        if next_page == None:
#            next_page = response.xpath('//a[contains(text(), "后页>")]/@href').extract_first()
#        urls = response.selector.re(r'https://movie.douban.com/subject/\d+/')
#        yield {'urls': urls}
#        if next_page != None:
#            yield scrapy.Request(response.urljoin(next_page), callback=self.parse_user)

#class CommentSpider(scrapy.Spider):
#    name = 'comment'
#    allowed_domains = ['movie.douban.com']
#    def __init__(self, mid):
#        self.start_urls = ['https://movie.douban.com/subject/%s/comments' % x for x in mid.split(',')]
#        self.movie_id = mid
#
#    def parse(self, response):
#        item = response.meta['item']
#        urls = response.meta['urls']
#        next_page = response.xpath('//a[contains(text(), "后页 >")]/@href').extract_first()
#        if next_page == None:
#            next_page = response.xpath('//a[contains(text(), "后页>")]/@href').extract_first()
#        for comment in response.css('.comment-item'):
#            id_ = comment.xpath('//div[contains(@class, "comment-item")]/@data-cid').extract_first()
#            votes = comment.css('.votes').extract_first()
#            content = comment.css('.short').extract_first()
#            rank = comment.xpath('//span[contains(@class, "rating")]/@title').extract_first()
#            rank_dict = {
#                '力荐': '5',
#                '推荐': '4',
#                '还行': '3',
#                '较差': '2',
#                '很差': '1'
#            }
#            star = rank_dict.get(rank, '5')
#            comment_item = CommentItem()
#            comment_item['id_'] = id_
#            comment_item['content'] = content
#            comment_item['starNumber'] = star
#            comment_item['usefulNumber'] = votes
#            item['shortRemark'].append(comment_item)
#        if next_page != None:
#            yield scrapy.Request(response.urljoin(next_page), meta=response.meta, callback=self.parse_comment)#