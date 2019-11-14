import sys
import os
import json
from model import *

start_page = int(sys.argv[1])
end_page = int(sys.argv[2])


for i in range(start_page - 1, end_page):
    print('Crawling page %d' % (i + 1))
    movies = Movie.select().where(Movie.comment_pages >= i)
    start_urls = ['https://movie.douban.com/subject/%d/comments?start=%d' % (movie.id_, i * 20) for movie in movies]
    with open('tmp_urls', 'w') as file:
        file.write(json.dumps(start_urls))
    with open('tmp_comment.json', 'w') as file:
        pass
    os.system('scrapy crawl comment -o tmp_comment.json')
    print('Successfully crawled page %d, now importing' % (i + 1))
    comments = json.loads(open('tmp_comment.json').read())
    for comment in comments:
        movie_id = comment['movie_id']
        for c in comment['comments']:
            try:
                id_ = int(c['id_'])
                content = c['content']
                vote = c['usefulNumber']
                rank = c['starNumber']
                co, created = Comment.get_or_create(id_=id_, content=content, movie_id=movie_id, vote=vote, rank=rank)
            except:
                pass