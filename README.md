# 依赖
```
python3, sqlite3, peewee, scrapy
```

# 使用方法
## 获取基本信息
基本信息包括影片的名字、URL等信息及海报和预告片的信息
```
scrapy crawl top250 -o movie.json
```

## 导入数据库

```
python3 import_movie.py movie.json
```

## 获取长短评论

```
python3 crawl_comment.py 1 100 #爬取从第1页到第100页的所有短评并导入数据库
python3 crawl_review.py 1 10 #爬取从第1页到第10页的所有影评并导入数据库
```

## 导出数据库

```
python3 export_movie.py result.json
```