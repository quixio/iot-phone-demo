import os
import datetime
import json
from flask import Flask, request, Response
from waitress import serve

from setup_logging import get_logger
from quixstreams import Application
from flask_restx import Api, Resource

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

quix_app = Application()
topic =  quix_app.topic(os.environ["output"])
producer = quix_app.get_producer()

logger = get_logger()

app = Flask(__name__)
api = Api(app, version='1.0', title='API Documentation', description='A simple API')

ns = api.namespace('my_namespace', description='Namespace operations')

@app.route("/", methods=['POST'])
def post_data():
    
    data = request.json

    print(data)

    logger.info(f"{str(datetime.datetime.utcnow())} posted.")
    
    producer.produce(topic.name, json.dumps(data), "test data")

    response = Response(status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=80)