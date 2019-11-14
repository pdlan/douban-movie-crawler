from peewee import *

db = SqliteDatabase('top250.db')

class BaseModel(Model):
    class Meta:
        database = db

class Movie(BaseModel):
    id_ = IntegerField(unique=True)
    name = CharField()
    type_ = CharField()
    comment_pages = IntegerField()
    review_pages = IntegerField()

class Comment(BaseModel):
    id_ = IntegerField(unique=True)
    movie_id = IntegerField()
    content = CharField()
    rank = CharField()
    vote = CharField()

class Review(BaseModel):
    id_ = IntegerField(unique=True)
    movie_id = IntegerField()
    content = CharField()
    rank = CharField()
    vote = CharField()

class Poster(BaseModel):
    url = CharField(unique=True)
    movie_id = IntegerField()

class Trailer(BaseModel):
    url = CharField(unique=True)
    movie_id = IntegerField()