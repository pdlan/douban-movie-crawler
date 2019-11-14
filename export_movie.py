import sys
import json
from model import *

filename = sys.argv[1]
movies = []

for movie in Movie.select():
    id_ = movie.id_
    url = 'https://movie.douban.com/subject/%d/' % id_
    name = movie.name
    type_ = movie.type_
    comment_pages = movie.comment_pages
    review_pages = movie.review_pages
    movie_json = {}
    movie_json['movieName'] = name
    movie_json['movieURL'] = url
    movie_json['movieType'] = type_
    posters = []
    trailers = []
    comments = []
    reviews = []
    for poster in Poster.select().where(Poster.movie_id == id_):
        #print(poster.url)
        posters.append(poster.url)
    for trailer in Trailer.select().where(Trailer.movie_id == id_):
        trailers.append(trailer.url)
    for comment in Comment.select().where(Comment.movie_id == id_):
        comment_json = {
            'id': comment.id_,
            'content': comment.content,
            'starNumber': comment.rank,
            'usefulNumber': comment.vote
        }
        comments.append(comment_json)
    for review in Review.select().where(Review.movie_id == id_):
        review_json = {
            'id': review.id_,
            'content': review.content,
            'starNumber': review.rank,
            'usefulNumber': review.vote
        }
        reviews.append(review_json)
        #print(review_json)
    movie_json['moviePoster'] = posters
    movie_json['movieShower'] = trailers
    movie_json['shortRemark'] = comments
    #movie_json['longRemark'] = reviews
    movies.append(movie_json)

with open(filename, 'w') as file:
    file.write(json.dumps(movies))