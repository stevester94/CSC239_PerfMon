#! /usr/bin/python

from pymongo import MongoClient
import pprint

pp = pprint.PrettyPrinter(indent=4)

client = MongoClient()

# Connect
client = MongoClient('localhost', 27017)
test_db = client.test_db # Access a particular database

# Insert a single 'document' into a collection
posts = test_db.posts
post_data = {
    'title': 'Python and MongoDB',
    'content': 'PyMongo is fun, you guys',
    'author': 'Steve'
}
result = posts.insert_one(post_data)
pp.pprint(result)

# Retrieve all documents matching the criteria
steves_posts = posts.find({'author': 'Steve'})
for document in steves_posts:
    pp.pprint(document)


# Update a single document if it exists, or create it
posts.find_one_and_update(
    {'author': 'Steve'},
    {'$set': {'jej': 1337}}, # this arg is the update, needs to have a '$' operator, $set will update or add a field
    upsert=True) # Create if it doesn't exist

# Retrieve all documents matching the criteria
print "====================================="
print "All documents containing the update:"
print "====================================="
steves_posts = posts.find({'jej': 1337})
for document in steves_posts:
    pp.pprint(document)