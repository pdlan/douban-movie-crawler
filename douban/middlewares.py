# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy import signals
import json
import urllib
import time
import _thread
import random

#def get_new_proxies():
#    l1 = urllib.request.urlopen('https://proxy.horocn.com/api/proxies?order_id=FGWP1650112907265526&num=10&format=text&line_separator=win').read().decode('utf-8').split('\n')
#    l2 = urllib.request.urlopen('https://proxy.horocn.com/api/proxies?order_id=4DIJ1650115412051583&num=10&format=text&line_separator=win').read().decode('utf-8').split('\n')
#    l = l1 + l2
#    return l
#
user_agents = open('user_agent.txt').readline()
#proxies = {x: time.time() for x in get_new_proxies()}
#last_update = time.time()

#def maintain_proxies():
#    global proxies
#    while True:
#        time.sleep(12)
#        l = get_new_proxies()
#        for p in l:
#            proxies[p] = time.time()
#        for p, t in list(proxies.items()):
#            if time.time() - t > 120:
#                del proxies[p]
#
#_thread.start_new_thread(maintain_proxies, ())
#
class DoubanSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class DoubanDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class UAProxyMiddleware(RetryMiddleware):
    def process_request(self, request, spider):
        global proxies
        global last_update
        request.headers['User-Agent'] = random.choice(user_agents)
        request.meta['proxy'] = 'http://PZK61650181434253173:pRgPvk9JKw56@dyn.horocn.com:50000'

    def process_response(self, request, response, spider):
        if response.status in [301, 302, 403, 404, 429, 500]:
            #input('change ip')
            return self._retry(request, '', spider) or response
        return response