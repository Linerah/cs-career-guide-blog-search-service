import hashlib
import json
import time
from bson import json_util


def generate_blog_id():
    """ Generates a unique blog's id
    """
    cur_time = str(time.time())
    hashed_time = hashlib.sha1()
    hashed_time.update(cur_time.encode("utf8"))
    return hashed_time.hexdigest()


class Blog:

    def __init__(self, title, information, link, user_id, tag):
        self.tag = tag
        self.blog_id = generate_blog_id()
        self.title = title
        self.information = information
        self.link = link
        self.date_published = time.time()
        self.upvote_count = 0
        self.read_count = 0
        self.user_id = user_id


    @staticmethod
    def create_blog(title, information, link, user_id, database, tag):
        """ A static method, that creates a blog object and adds it to the database
        """
        blog = Blog(title, information, link, user_id, tag)
        blog_document = blog.to_json()
        collection = database.db.blogs
        print(blog_document)
        collection.insert_one(blog_document)
        return blog

    @staticmethod
    def get_blogs(database, user_id):
        """ A static method, that gets all of the blogs in the database
        """
        collection = database.db.blogs  # TODO: try to see if Atlas search has an AI that orders by relevance
        pipeline = [
            {
                '$lookup': {
                    'from': "users",
                    'localField': "user_id",
                    'foreignField': "_id",
                    'as': "user_info"
                }
            },
            {
                '$lookup': {
                    "from": "upvote",
                    "let": {"user_id": user_id,
                            "blog_id": "$blog_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$user_id", user_id]},
                                        {"$eq": ["$blog_id", "$$blog_id"]}
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "matchedDocuments"
                }
            },
            {
                '$project': {
                    "_id": 0,
                    "blog_id": 1,
                    "title": 1,
                    "information": 1,
                    "link": 1,
                    "read_count": 1,
                    "upvote_count": 1,
                    "upvote": {
                        '$ne': ["$matchedDocuments", []]
                    },
                    "tag":1,
                    "date_published": 1,
                    "user_info._id": 1,
                    "user_info.email": 1,
                    "user_info.name": 1
                }
            }
        ]
        return json.loads(json_util.dumps(collection.aggregate(pipeline)))

    @staticmethod
    def get_filtered_blogs(database, blog_filter, blog_title, user_id):
        """ A static method, that filters blogs by the given input from the user
        """
        tagList = ['Programming Languages', 'Data Structures', 'Computer Architecture', 'Computer Networks', 'Cybersecurity', 'Databases', 'Software Engineering', 'Human/Computer Interaction', 'Artificial Intelligence']
        collection = database.db.blogs
        query = {'query': blog_title, 'path': ['title']}
        pipeline = [
            {
                '$search': {
                    'index': 'blogs',
                    'text': query
                }
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "user_id",
                    'foreignField': "_id",
                    'as': "user_info"
                }
            },
            {
                '$lookup': {
                    "from": "upvote",
                    "let": {"user_id": user_id,
                            "blog_id": "$blog_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$user_id", user_id]},
                                        {"$eq": ["$blog_id", "$$blog_id"]}
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "matchedDocuments"
                }
            },
            {
                '$project': {
                    "_id": 0,
                    "blog_id": 1,
                    "title": 1,
                    "information": 1,
                    "link": 1,
                    "read_count": 1,
                    "upvote_count": 1,
                    "upvote": {
                        '$ne': ["$matchedDocuments", []]
                    },
                    "tag": 1,
                    "date_published": 1,
                    "user_info._id": 1,
                    "user_info.email": 1,
                    "user_info.name": 1
                }
            }
        ]
        if not blog_filter and not blog_title:
            return json.loads(json_util.dumps(collection.aggregate([{
                '$lookup': {
                    'from': "users",
                    'localField': "user_id",
                    'foreignField': "_id",
                    'as': "user_info"
                }
            },
                {
                    '$lookup': {
                        "from": "upvote",
                        "let": {"user_id": user_id,
                                "blog_id": "$blog_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$user_id", user_id]},
                                            {"$eq": ["$blog_id", "$$blog_id"]}
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "matchedDocuments"
                    }
                },
                {
                    '$project': {
                        "_id": 0,
                        "blog_id": 1,
                        "title": 1,
                        "information": 1,
                        "link": 1,
                        "read_count": 1,
                        "upvote_count": 1,
                        "upvote": {
                            '$ne': ["$matchedDocuments", []]
                        },
                        "tag": 1,
                        "date_published": 1,
                        "user_info._id": 1,
                        "user_info.email": 1,
                        "user_info.name": 1
                    }
                }
            ])))
        elif not blog_filter:
            return json.loads(json_util.dumps(collection.aggregate(pipeline)))
        elif not blog_title:
            pipeline = [
                {
                    '$lookup': {
                        'from': "users",
                        'localField': "user_id",
                        'foreignField': "_id",
                        'as': "user_info"
                    }
                },
                {
                    '$lookup': {
                        "from": "upvote",
                        "let": {"user_id": user_id,
                                "blog_id": "$blog_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$user_id", user_id]},
                                            {"$eq": ["$blog_id", "$$blog_id"]}
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "matchedDocuments"
                    }
                },
                {
                    '$project': {
                        "_id": 0,
                        "blog_id": 1,
                        "title": 1,
                        "information": 1,
                        "link": 1,
                        "read_count": 1,
                        "upvote_count": 1,
                        "upvote": {
                            '$ne': ["$matchedDocuments", []]
                        },
                        "tag": 1,
                        "date_published": 1,
                        "user_info._id": 1,
                        "user_info.email": 1,
                        "user_info.name": 1
                    }
                }
            ]
            if blog_filter == "Newest":
                sort_criteria = {"date_published": -1}
                pipeline.append({"$sort": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
            elif blog_filter == "Most upvote":
                sort_criteria = {"upvote_count": -1}
                pipeline.append({"$sort": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
            elif blog_filter in tagList:
                sort_criteria = {"tag": blog_filter}
                pipeline.append({"$match": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
            else:
                # this returns the blogs ordered "Oldest"
                sort_criteria = {"date_published": 1}
                pipeline.append({"$sort": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
        else:
            if blog_filter == "Newest":
                sort_criteria = {"date_published": -1}
                pipeline.append({"$sort": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
            elif blog_filter == "Most upvote":
                sort_criteria = {"upvote_count": -1}
                pipeline.append({"$sort": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
            elif blog_filter in tagList:
                sort_criteria = {"tag": blog_filter}
                pipeline.append({"$match": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
            else:
                sort_criteria = {"date_published": 1}
                pipeline.append({"$sort": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))

    def to_json(self):
        """ Converts a blog object to json format
        """
        return {'blog_id': self.blog_id, 'title': self.title, 'information': self.information, 'link': self.link,
                'date_published': self.date_published, 'upvote_count': self.upvote_count, 'read_count': self.read_count,
                'user_id': self.user_id, 'tag': self.tag}