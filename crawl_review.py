import sys
import os
import json
from model import *

start_page = int(sys.argv[1])
end_page = int(sys.argv[2])


for i in range(start_page - 1, end_page):
    print('Crawling page %d' % (i + 1))
    movies = Movie.select().where(Movie.comment_pages >= i)
    start_urls = ['https://movie.douban.com/subject/%d/reviews?start=%d' % (movie.id_, i * 20) for movie in movies]
    with open('tmp_urls', 'w') as file:
        file.write(json.dumps(start_urls))
    with open('tmp_comment.json', 'w') as file:
        pass
    os.system('scrapy crawl review -o tmp_review.json')
    print('Successfully crawled page %d, now importing' % (i + 1))
    reviews = json.loads(open('tmp_review.json').read())
    for review in reviews:
        r = review['review']
        try:
            id_ = int(r['id_'])
            movie_id = r['movieId']
            content = r['content']
            vote = r['usefulNumber']
            rank = r['starNumber']
            co, created = Review.get_or_create(id_=id_, content=content, movie_id=movie_id, vote=vote, rank=rank)
        except:
            pass