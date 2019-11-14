# -*- coding: utf-8 -*-
import scrapy
import re
import urllib
import json
import time
import random
import logging
from douban.items import *

class Top250Spider2(scrapy.Spider):
    name = 'top2501'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250?start=%d' % (i * 25) for i in range(10)]
    handle_httpstatus_list = [200, 403, 301, 302, 404]

    def __init__(self, max_pages=100):
        self.max_pages = int(max_pages)

    def parse(self, response):
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
        item['moviePoster'] = []
        item['movieShower'] = []
        #print(movie_id, movie_name, movie_type)
        url_poster = 'https://movie.douban.com/subject/%s/photos?type=R' % movie_id
        url_trailer = 'https://movie.douban.com/subject/%s/trailer' % movie_id
        url_comment = 'https://movie.douban.com/subject/%s/comments' % movie_id
        url_review = 'https://movie.douban.com/subject/%s/reviews' % movie_id
        urls = {
            'poster': url_poster,
            'trailer': url_trailer,
            'comment': url_comment,
            'review': url_review
        }
        yield scrapy.Request(url_poster, meta={'urls': urls, 'item': item, 'page': 0}, callback=self.parse_poster, priority=10)
        yield scrapy.Request(url_comment, meta={'page': 0, 'movie_id': movie_id}, callback=self.parse_comment, priority=-1)
        yield scrapy.Request(url_review, meta={'page': 0, 'movie_id': movie_id}, callback=self.parse_review, priority=-1)

    def parse_poster(self, response):
        item = response.meta['item']
        urls = response.meta['urls']
        next_page = response.selector.xpath('//a[contains(text(), "后页>")]/@href').extract_first()
        posters = response.selector.re(r'https://movie.douban.com/photos/photo/\d+/')
        item['moviePoster'] += posters
        if next_page != None:
            yield scrapy.Request(response.urljoin(next_page), meta=response.meta, callback=self.parse_poster, priority=10)
        else:
            yield scrapy.Request(urls['trailer'], meta=response.meta, callback=self.parse_trailer, priority=10)

    def parse_trailer(self, response):
        item = response.meta['item']
        urls = response.meta['urls']
        next_page = response.selector.xpath('//a[contains(text(), "后页>")]/@href').extract_first()
        trailers = response.selector.re(r'https://movie.douban.com/trailer/\d+/')
        item['movieShower'] += trailers
        if next_page != None:
            yield scrapy.Request(response.urljoin(next_page), meta=response.meta, callback=self.parse_trailer, priority=10)
        else:
            self.state['basic_info_number'] = self.state.get('basic_info_number', 0) + 1
            logging.info('Crawled basic information of movie %s, %d/250' % (item['movieName'], self.state['basic_info_number']))
            yield item

    def parse_comment(self, response):
        page = response.meta['page']
        movie_id = response.meta['movie_id']
        next_page = response.xpath('//a[contains(text(), "后页 >")]/@href').extract_first()
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
            comment_item['movieId'] = response.meta['movie_id'] 
            comment_item['id_'] = id_
            comment_item['content'] = content
            comment_item['starNumber'] = star
            comment_item['usefulNumber'] = votes
            comments.append(comment_item)
        logging.info('Crawled comment page#%d of movie%s' % (page, movie_id))
        yield {'movie_id': movie_id, 'comments': comments}
        if next_page != None and page < self.max_pages:
            response.meta['page'] += 1
            yield scrapy.Request(response.urljoin(next_page), meta=response.meta, callback=self.parse_comment, priority=-page-1)

    def parse_review(self, response):
        page = response.meta['page']
        movie_id = response.meta['movie_id']
        next_page = response.xpath('.//a[contains(text(), "后页>")]/@href').extract_first()
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
            review_item['movieId'] = response.meta['movie_id'] 
            review_item['starNumber'] = star
            review_item['usefulNumber'] = votes
            url_content = 'https://movie.douban.com/j/review/%s/full' % id_
            yield scrapy.Request(url_content, meta={'item': review_item}, callback=self.parse_content)
        logging.info('Crawled review page#%d of movie%s' % (page, movie_id))
        if next_page != None and page < self.max_pages:
            response.meta['page'] += 1
            yield scrapy.Request(response.urljoin(next_page), meta=response.meta, callback=self.parse_review, priority=-page-1)

    def parse_content(self, response):
        item = response.meta['item']
        item['content'] = json.loads(response.body)['body']
        yield item

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