import json

from bson import json_util
from flask import Flask, request, jsonify
import pymongo
from flask_cors import CORS, cross_origin

from blog import Blog
from research import Research

app = Flask(__name__)
cors = CORS(app)

app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

app.config['MONGO_DBNAME'] = 'user_auth'

client = pymongo.MongoClient(
    "mongodb+srv://admin:NtXLrfmOBLhl00bm@capstoneauth.25mmcqj.mongodb.net/?retryWrites=true&w=majority", tls=True,
    tlsAllowInvalidCertificates=True)
db = client['user-auth']


@app.route("/")
@app.route("/blogs", methods=["GET", "POST"])
@cross_origin()
def blogs():
    if request.method == "GET":
        user_id = request.args.get('user_id')
        all_blogs = Blog.get_blogs(db, user_id)
    else:
        blog_filter = request.json['blog-filter']
        blog_tittle = request.json['blog-title']
        user_id = request.json['user_id']
        all_blogs = Blog.get_filtered_blogs(db, blog_filter, blog_tittle, user_id)
    return all_blogs


@app.route("/create_blog", methods=["GET", "POST"])
@cross_origin()
def create_blog():
    if request.method == "POST":
        title = request.json['title']
        information = request.json['information']
        link = request.json['link']
        user_id = request.json['user_id']
        tag = request.json['tag']
        Blog.create_blog(title, information, link, user_id, db, tag)
        return jsonify({'result': "Successfully created Blog"})

    all_blogs = db.db.blogs.find()
    return json.loads(json_util.dumps(all_blogs))


@app.route("/research", methods=["GET", "POST"])
@cross_origin()
def research():
    if request.method == "GET":
        user_id = request.args.get('user_id')
        all_research = Research.get_research(db, user_id)
    else:
        research_filter = request.json['research-filter']
        research_title = request.json['research-title']
        user_id = request.json['user_id']
        all_research = Research.get_filtered_research(db, research_filter, research_title, user_id)
    return all_research


@app.route("/create_research", methods=["POST"])
@cross_origin()
def create_research():
    if request.method == "POST":
        title = request.json['title']
        information = request.json['information']
        link = request.json['link']
        user_id = request.json['user_id']
        tag = request.json['tag']
        file = request.json['file']
        Research.create_research(title, information, link, user_id, db, tag, file)
        return jsonify({'result': "Successfully created Research entry"})

    all_research = db.db.research.find()
    return json.loads(json_util.dumps(all_research))


@app.route("/get_organization", methods=["GET"])
@cross_origin()
def get_orgs():
    if request.method == "GET":
        return json.loads(json_util.dumps(db.db.organization.find()))
