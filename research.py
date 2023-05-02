import hashlib
import json
import time
from bson import json_util


def generate_research_id():
    """ Generates a unique research's id
    """
    cur_time = str(time.time())
    hashed_time = hashlib.sha1()
    hashed_time.update(cur_time.encode("utf8"))
    return hashed_time.hexdigest()


class Research:
    def __init__(self, title, information, link, user_id, tag, file):
        self.tag = tag
        self.research_id = generate_research_id()
        self.title = title
        self.information = information
        self.link = link
        self.date_published = time.time()
        self.user_id = user_id
        self.file = file

    @staticmethod
    def create_research(title, information, link, user_id, database, tag, file):
        """ A static method, that creates a research object and adds it to the database
        """
        research = Research(title, information, link, user_id, tag, file)
        research_document = research.to_json()
        collection = database.db.research
        collection.insert_one(research_document)
        return research

    @staticmethod
    def get_research(database, user_id):
        """ A static method, that gets all the
        s in the database
        """
        collection = database.db.research
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
                '$project': {
                    "_id": 0,
                    "research_id": 1,
                    "title": 1,
                    "information": 1,
                    "link": 1,
                    "tag": 1,
                    "file": 1,
                    "date_published": 1,
                    "user_info._id": 1,
                    "user_info.email": 1,
                    "user_info.name": 1
                }
            }
        ]
        return json.loads(json_util.dumps(collection.aggregate(pipeline)))

    @staticmethod
    def get_filtered_research(database, research_filter, research_title, user_id):
        """ A static method, that filters research by the given input from the user
        """
        tagList = ['Programming Languages', 'Data Structures', 'Computer Architecture', 'Computer Networks',
                   'Cybersecurity', 'Databases', 'Software Engineering', 'Human/Computer Interaction',
                   'Artificial Intelligence']
        collection = database.db.research
        query = {'query': research_title, 'path': ['title']}
        pipeline = [
            {
                '$search': {
                    'index': 'research',
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
                            "research_id": "$research_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$user_id", user_id]},
                                        {"$eq": ["$research_id", "$$research_id"]}
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
                    "research_id": 1,
                    "title": 1,
                    "information": 1,
                    "link": 1,
                    "tag": 1,
                    "file": 1,
                    "date_published": 1,
                    "user_info._id": 1,
                    "user_info.email": 1,
                    "user_info.name": 1
                }
            }
        ]
        if not research_filter and not research_title:
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
                                "research_id": "$research_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$user_id", user_id]},
                                            {"$eq": ["$research_id", "$$research_id"]}
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
                        "research_id": 1,
                        "title": 1,
                        "information": 1,
                        "link": 1,
                        "tag": 1,
                        "file": 1,
                        "date_published": 1,
                        "user_info._id": 1,
                        "user_info.email": 1,
                        "user_info.name": 1
                    }
                }
            ])))
        elif not research_filter:
            return json.loads(json_util.dumps(collection.aggregate(pipeline)))
        elif not research_title:
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
                                "research_id": "$research_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$user_id", user_id]},
                                            {"$eq": ["$research_id", "$$research_id"]}
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
                        "research_id": 1,
                        "title": 1,
                        "information": 1,
                        "link": 1,
                        "tag": 1,
                        "file":1,
                        "date_published": 1,
                        "user_info._id": 1,
                        "user_info.email": 1,
                        "user_info.name": 1
                    }
                }
            ]
            if research_filter == "Newest":
                sort_criteria = {"date_published": -1}
                pipeline.append({"$sort": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
            elif research_filter in tagList:
                sort_criteria = {"tag": research_filter}
                pipeline.append({"$match": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
            else:
                # this returns the research ordered "Oldest"
                sort_criteria = {"date_published": 1}
                pipeline.append({"$sort": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
        else:
            if research_filter == "Newest":
                sort_criteria = {"date_published": -1}
                pipeline.append({"$sort": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
            elif research_filter in tagList:
                sort_criteria = {"tag": research_filter}
                pipeline.append({"$match": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))
            else:
                sort_criteria = {"date_published": 1}
                pipeline.append({"$sort": sort_criteria})
                return json.loads(json_util.dumps(collection.aggregate(pipeline)))

    def to_json(self):
        """ Converts a research object to json format
        """
        return {'research_id': self.research_id, 'title': self.title, 'information': self.information,
                'link': self.link,
                'date_published': self.date_published, 'user_id': self.user_id, 'tag': self.tag, 'file': self.file}
