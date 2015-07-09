import json
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
    db_names = collection.find(projection={'name': True})
    found_names = sorted(set((p['name'] for p in db_names)))
    connection.close()
    return json.dumps(found_names)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)