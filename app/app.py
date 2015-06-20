import json
from flask import Flask
from flask import render_template
from pymongo import MongoClient

app = Flask(__name__)

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'names'
COLLECTION_NAME = 'data'
FIELDS = {'name': True,
          'gender': True,
          'name_type': True,
          'birth_year': True,
          'n_born': True,
          'n_born_and_alive': True,
          'n_dead': True,
          '_id': False}



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/names")
def names():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DB_NAME][COLLECTION_NAME]
    projects = collection.find(projection=FIELDS, limit=50)
    #projects = collection.find(fields=FIELDS)
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects)
    connection.close()
    return json_projects


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)