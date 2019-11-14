import sys
import json
from model import *

db.connect()
db.create_tables([Movie, Comment, Review, Poster, Trailer])

filename = sys.argv[1]
data = json.loads(open(filename).read())

for d in data:
    if d['type'] == 'movie':
        movie_json = d['item']
        name = movie_json['movieName']
        url = movie_json['movieURL']
        type_ = movie_json['movieType']
        id_ = int(url[33:-1])
        comment_pages = movie_json['pagesComments']
        review_pages = movie_json['pagesReviews']
        movie = Movie(id_=id_, type_=type_, name=name, comment_pages=comment_pages, review_pages=review_pages)
        movie.save()
    elif d['type'] == 'posters':
        posters = d['posters']
        movie_id = int(d['movie_id'])
        for poster in posters:
            p, created = Poster.get_or_create(url=poster, movie_id=movie_id)
    elif d['type'] == 'trailers':
        trailers = d['trailers']
        movie_id = int(d['movie_id'])
        for trailer in trailers:
            t, created = Trailer.get_or_create(url=trailer, movie_id=movie_id)