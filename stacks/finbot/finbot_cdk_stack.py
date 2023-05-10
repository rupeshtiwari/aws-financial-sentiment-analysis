# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os

from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_lex as lex,
    Duration,
    CfnOutput,
)
from constructs import Construct


ROLE_ARN_TO_BUILD_RUN_BOT = (
    "arn:aws:iam::855874109978:role/AllPayments-Wonderland-Admin"
)


class FinBotCdkStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, state_machine_arn: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id)
        self.create_lex(state_machine_arn)

    def create_lex(self, state_machine_arn) -> None:
        # Create the Lambda function to handle bot requests
        bot_request_handler = lambda_.Function(
            self,
            "BotRequestHandler",
            function_name="bot_request_handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("stacks/finbot/lambda/bot-req-handler"),
            handler="index.handler",
            memory_size=1024,
            timeout=Duration.minutes(5),
        )

        # Create Bot
        cfn_bot = lex.CfnBot(
            self,
            "FinBot",
            idle_session_ttl_in_seconds=123,
            name="finbot",
            role_arn="{ROLE_ARN_TO_BUILD_RUN_BOT}",
        )

        # Attach req handler to bot
        lambda_code_hook_property = lex.CfnBot.LambdaCodeHookProperty(
            code_hook_interface_version="1.0",
            lambda_arn=bot_request_handler.function_arn,
        )

        CfnOutput(self, "FinBot created", value=cfn_bot.attr_arn)
        CfnOutput(
            self,
            "Created Bot request handler lambda",
            value=bot_request_handler.function_arn,
        )
        CfnOutput(
            self,
            "FinBot linked with lambda",
            value=lambda_code_hook_property.lambda_arn,
        )

        # Add statemachine arn to lambda env
        bot_request_handler.add_environment("STATE_MACHINE_ARN", state_machine_arn)
