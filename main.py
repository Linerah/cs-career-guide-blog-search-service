from flask import Flask, request
import pymongo
from blog import Blog

app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

app.config['MONGO_DBNAME'] = 'user_auth'

client = pymongo.MongoClient(
    "mongodb+srv://admin:NtXLrfmOBLhl00bm@capstoneauth.25mmcqj.mongodb.net/?retryWrites=true&w=majority", tls=True,
    tlsAllowInvalidCertificates=True)
db = client['user-auth']


@app.route("/")
@app.route("/blogs", methods=["GET", "POST"])
def blogs():
    if request.method == "GET":
        all_blogs = Blog.get_blogs(db)
    else:
        blog_filter = request.json['blog-filter']
        blog_tittle = request.json['blog-title']
        all_blogs = Blog.get_filtered_blogs(db, blog_filter, blog_tittle)
    return all_blogs


@app.route("/create_blog", methods=["GET", "POST"])
def create_blog():
    if request.method == "POST":
        title = request.json['title']
        information = request.json['information']
        link = request.json['link']
        user_id = request.json['user_id']
        Blog.create_blog(title, information, link, user_id, db)
        return "Successfully created Blog ;)"
    all_blogs = Blog.get_blogs(db)
    return all_blogs
