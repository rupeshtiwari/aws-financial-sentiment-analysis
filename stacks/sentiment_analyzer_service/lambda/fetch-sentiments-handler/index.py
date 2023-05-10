# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")

#TODO: confirm this code works I copied from quip 
def handler(event, context):
    table = os.environ.get("TABLE_NAME")
    endpoint_name =  os.environ.get("SAGEMAKER_ENDPOINT_NAME")

    # Create a low-level client representing Amazon SageMaker Runtime
    sagemaker_runtime = boto3.client("sagemaker-runtime")

    # The name of the endpoint. The name must be unique within an AWS Region in your AWS account.
    endpoint_name = "huggingface-pytorch-inference-2023-04-27-19-15-14-283"

    # After you deploy a model into production using SageMaker hosting
    # services, your client applications use this API to get inferences
    # from the model hosted at the specified endpoint.
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Body=bytes(
            '{"inputs":"Meta Platforms (  META - Free Report) reported first-quarter 2023 earnings of $2.20 per share, beating the Zacks Consensus Estimate by 34.69%.  Revenues of $28.65 billion beat the Zacks Consensus Estimate by 4.21% and increased 2.6% year over year. At constant currency (cc), the top line improved 6%.  Top-Line Details  Geographically, the Rest of the World (RoW) revenues grew 10% on a year-over-year basis. The Asia-Pacific and the United States & Canada revenues increased 3.5% and 3% year over year, respectively. However, Europe revenues declined 2.2% year over year.  Revenues from Family of Apps (98.8% of total revenues), which includes Facebook, Instagram, Messenger, WhatsApp and other services, increased 4% year over year to $28.31 billion.  Meta Platforms, Inc. Price, Consensus and EPS Surprise    Meta Platforms, Inc. Price, Consensus and EPS Surprise Meta Platforms,"}',
            "utf-8",
        ),  # Replace with your own data.
    )

    # Optional - Print the response body and decode it so it is human read-able.
    print(response["Body"].read().decode("utf-8"))