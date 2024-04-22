import os
import datetime
import json
from flask import Flask, request, Response
from waitress import serve

# Ensure these imports are correctly set up in your project
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

@ns.route('/', methods=['POST'])
class WebServer(Resource):

    def post(self):
        data = request.json
        logger.info(f"{str(datetime.datetime.utcnow())} posted: {data}")
        
        # It's recommended to catch potential exceptions here for robustness
        try:
            producer.produce(topic.name, json.dumps(data), "test data")
        except Exception as e:
            logger.error(f"Failed to produce to topic: {e}")
            return {"error": "Internal server error"}, 500
        
        return {"message": "Data posted successfully"}, 200


if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=80)
