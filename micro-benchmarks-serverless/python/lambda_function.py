import json
import os
from datetime import datetime
import http


def lambda_handler(event, context):
    response_body = {
        "message": "Hello, World!"
    }

    # Serialize
    json_body = json.dumps(response_body)

    response = {
        "statusCode": http.HTTPStatus.OK,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": str(len(json_body)),
            "Server": "AWS Lambda",
            "Date": datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),
        },
        "body": json_body,
        "isBase64Encoded": False
    }

    return response
