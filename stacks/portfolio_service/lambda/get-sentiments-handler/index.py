# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    sentiment_api_arn = os.environ.get("SENTIMENT_API_ARN")
    logging.info(f"## Calling sentiment api: {sentiment_api_arn}")
    # TODO: add code to fetch sentiments
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "TODO call sentiment_api_arn"}),
    }
