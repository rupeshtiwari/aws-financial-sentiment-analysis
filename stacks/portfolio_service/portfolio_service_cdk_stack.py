# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
 
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb_,
    aws_lambda as lambda_,
    aws_apigateway as apigw_,
    aws_ec2 as ec2,
    aws_iam as iam,
    Duration,
    CfnOutput,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
)
from constructs import Construct

TABLE_NAME = "portfolio_table"


class PortfolioServiceCdkStack(Stack):
    state_machine_arn:str =''
    
    def __init__(
        self, scope: Construct, construct_id: str, sentiment_api_arn: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id)
        self.create_portfolio_service(sentiment_api_arn)

    def create_portfolio_service(self, sentiment_api_arn) -> None:
        # Create DynamoDb Table
        portfolio_table = dynamodb_.Table(
            self,
            TABLE_NAME,
            partition_key=dynamodb_.Attribute(
                name="id", type=dynamodb_.AttributeType.STRING
            ),
        )

        # Create the Lambda function to fetch sentiments
        get_sentiments_handler = lambda_.Function(
            self,
            "GetSentiments",
            function_name="get_sentiments_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset(
                "stacks/portfolio_service/lambda/get-sentiments-handler"
            ),
            handler="index.handler",
            memory_size=1024,
            timeout=Duration.minutes(5),
        )

        # Create the Lambda function to fetch Riskscore
        get_riskscore_handler = lambda_.Function(
            self,
            "GetRiskScore",
            function_name="get_riskscore_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset(
                "stacks/portfolio_service/lambda/get-risk-score-handler"
            ),
            handler="index.handler",
            memory_size=1024,
            timeout=Duration.minutes(5),
        )

        # Create Lambda state machine
        #TODO: write state machine logic
        state_machine = sfn.StateMachine(
            self,
            "PortfolioStateMachine",
            definition=tasks.LambdaInvoke(
                self, "GetSentimentsTask", lambda_function=get_sentiments_handler
            )
            .next(
                tasks.LambdaInvoke(
                    self, "GetScoreTasks", lambda_function=get_riskscore_handler
                )
            )
            .next(sfn.Succeed(self, "GreetedWorld")),
        )
        
        self.state_machine_arn =state_machine.state_machine_arn

        # grant permission to lambda to write to demo table
        portfolio_table.grant_write_data(get_riskscore_handler)
        portfolio_table.grant_write_data(get_sentiments_handler)

        # add env variables of lambda
        get_riskscore_handler.add_environment("TABLE_NAME", portfolio_table.table_name)
        get_sentiments_handler.add_environment(
            "SENTIMENT_API_ARN", sentiment_api_arn
        )
