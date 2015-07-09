import json
from bson import json_util
from flask import Flask
from flask import render_template
from pymongo import MongoClient

app = Flask(__name__)

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'names'
COLLECTION_NAME = 'data'
FIELDS = {'name': True,}



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/names")
def names():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DB_NAME][COLLECTION_NAME]
    projects = collection.find(projection=FIELDS)
    json_projects = []
    for project in projects:
        json_projects.append(project['name'])
    json_projects = json.dumps(json_projects)
    connection.close()
    return json_projects


@app.route("/search")
def search():
    """ Get searchable names.
    :return: JSON string with names
    """
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DB_NAME][COLLECTION_NAME]
    db_names = collection.find(projection={'name': True}).distinct('name')
    found_names = sorted(db_names)
    connection.close()
    return json_util.dumps(found_names)


@app.route("/stats/<name>")
def stats(name):
    """ Get stats for a name.
    :param name: Name
    :return: JSON string with name stats
    """
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DB_NAME][COLLECTION_NAME]
    # TODO: make case insensitive
    # TODO: Catch unknown names
    items = collection.find({'name': name.lower()},
                            {'name': True,
                             'gender': True,
                             'name_type': True,
                             'data': True})
    return json_util.dumps(items)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)