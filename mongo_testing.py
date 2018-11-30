#! /usr/bin/python

from pymongo import MongoClient
import pprint

pp = pprint.PrettyPrinter(indent=4)

client = MongoClient()

# Connect
client = MongoClient('localhost', 27017)
test_db = client.test_db # Access a particular database

# Insert a single 'document'
posts = test_db.posts
post_data = {
    'title': 'Python and MongoDB',
    'content': 'PyMongo is fun, you guys',
    'author': 'Steve'
}
result = posts.insert_one(post_data)
pp.pprint(result)

# Retrieve a single document
steves_post = posts.find_one({'author': 'Steve'})
pp.pprint(steves_post)
