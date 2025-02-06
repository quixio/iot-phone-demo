from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flasgger import Swagger

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongodb:27017/sensor-data"
mongo = PyMongo(app)
Swagger(app, config={'url_prefix': '/index'})


@app.route("/documents", methods=["GET"])
def get_documents():
    """
    Get all documents from MongoDB
    ---
    responses:
      200:
        description: A list of documents
    """
    documents = list(mongo.db.collection.find({}, {"_id": 0}))
    return jsonify(documents)

@app.route("/documents", methods=["POST"])
def add_document():
    """
    Add a new document to MongoDB
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      201:
        description: Document added successfully
    """
    data = request.json
    mongo.db.collection.insert_one(data)
    return jsonify({"message": "Document added"}), 201

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
