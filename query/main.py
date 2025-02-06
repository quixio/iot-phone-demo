from flask import Flask, request, jsonify
from pymongo import MongoClient

from flasgger import Swagger
import json

app = Flask(__name__)

client = MongoClient("mongodb://mongodb:27017/")
db = client["sensordata"]
collection = db["sensordata"]

Swagger(app)


@app.route("/documents", methods=["GET"])
def get_documents():
    """
    Get all documents from MongoDB
    ---
    responses:
      200:
        description: A list of documents
    """

    documents = list(collection.find({}))  # Get all documents
    for doc in documents:
        print(doc)

    return jsonify(documents), 200

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
    mongo.db.sensordata.insert_one(data)
    return jsonify({"message": "Document added"}), 201

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
