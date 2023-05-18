# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
from aws_cdk import aws_sagemaker as sagemaker
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb_,
    aws_lambda as lambda_,
    aws_apigateway as apigw_,
    aws_ec2 as ec2,
    aws_iam as iam,
    Duration,
    CfnOutput,
)
from constructs import Construct
from sagemaker.huggingface import HuggingFaceModel

TABLE_NAME = "fin_news_table"
ROLE="arn:aws:iam::164941468929:role/service-role/AmazonSageMaker-ExecutionRole-20230214T170512"

## This calss will create all components required for sentiment analyzer
class SentimentAnalyzerServiceCdkStack(Stack):
    sentiment_api_arn: str = ""

    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)
        self.create_sm_endpoint()

    def create_sm_endpoint(self) -> None:
        # Create FinNews DynamoDb Table
        demo_table = dynamodb_.Table(
            self,
            TABLE_NAME,
            partition_key=dynamodb_.Attribute(
                name="id", type=dynamodb_.AttributeType.STRING
            ),
        )

        # Hub Model configuration. https://huggingface.co/models
        hub = {"HF_MODEL_ID": "ProsusAI/finbert", "HF_TASK": "text-classification"}

        # create Hugging Face Model Class
        huggingface_model = HuggingFaceModel(
            transformers_version="4.17.0",
            pytorch_version="1.10.2",
            py_version="py38",
            env=hub,
            role=ROLE,
        )

        # Define the SageMaker endpoint
        predictor = huggingface_model.deploy(
            initial_instance_count=1,  # number of instances
            instance_type="ml.t2.medium",  # ec2 instance type #TODO: change instance to higher level ml.m5.4xlarge
        )

        CfnOutput(self, "SageMakerEndpoint", value=predictor.endpoint_name)

        # Create the Lambda function to access Sagemaker and dynamodb
        sentiment_handler = lambda_.Function(
            self,
            "FetchSentimentHandler",
            function_name="fetch_sentiment_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset(
                "stacks/sentiment_analyzer_service/lambda/fetch-sentiments-handler"
            ),
            handler="index.handler",
            memory_size=1024,
            timeout=Duration.minutes(5),
        )

        # grant permission to lambda to write dynamodb and sagemaker
        demo_table.grant_write_data(sentiment_handler)

        # Create a policy statement to allow the Lambda function to invoke the SageMaker endpoint
        sagemaker_policy_statement = iam.Policy(
            self,
            "Policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["sagemaker:InvokeEndpoint"],
                    resources=["*"],
                )
            ],
        )
        # Attach the policy statement to the Lambda function role
        sentiment_handler.role.attach_inline_policy(sagemaker_policy_statement)

        # Add env variables
        sentiment_handler.add_environment("TABLE_NAME", demo_table.table_name)
        sentiment_handler.add_environment(
            "SAGEMAKER_ENDPOINT_NAME", predictor.endpoint_name
        )
        sentiment_handler.grant_invoke(iam.ServicePrincipal("apigateway.amazonaws.com"))

        # Create API Gateway to call lambda
        api = apigw_.RestApi(
            self,
            "widgets-api",
            rest_api_name="Fetch Sentiments Service",
            description="This service serves sentiments.",
        )
        # Define the API Gateway resources and methods
        api_resource = api.root.add_resource('myresource')
        api_resource.add_method('GET', apigw_.LambdaIntegration(sentiment_handler))

        dev_deployment = apigw_.Deployment(self, "DevDeployment", api=api)
        dev_stage = apigw_.Stage(self, 'DevStage', deployment=dev_deployment, stage_name='dev')
        # expose arn of api gateway 
        self.sentiment_api_arn = api.arn_for_execute_api("GET", "/", "dev")
