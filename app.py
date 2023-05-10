"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from stacks.finbot.finbot_cdk_stack import FinBotCdkStack

from stacks.portfolio_service.portfolio_service_cdk_stack import PortfolioServiceCdkStack

from stacks.sentiment_analyzer_service.sentiment_analyzer_service_cdk_stack import    SentimentAnalyzerServiceCdkStack

import aws_cdk as cdk
app = cdk.App()

# create sentiment analyzer service
sentiment_analyzer_service = SentimentAnalyzerServiceCdkStack(
    app, "SentiMentAnalyzerServiceCdkStack"
)

# create portfolio service
portfolio_service = PortfolioServiceCdkStack(
    app, "PortfolioServiceCdkStack", sentiment_analyzer_service.sentiment_api_arn
)

# create finbot service
bot_service = FinBotCdkStack(app, "FinBotCdkStack", portfolio_service.state_machine_arn)

app.synth()
