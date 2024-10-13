from aws_cdk import (
    BundlingOptions,
    Duration,
    Stack,
)
from constructs import Construct
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as sns_subscriptions
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets


class AppsnipStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        topic = sns.Topic(self, "AppsnipTopic", display_name="Appsnip Topic")
        topic.add_subscription(sns_subscriptions.EmailSubscription("foo@bar.com"))

        appsnip_lambda = _lambda.Function(
            self,
            id="AppsnipLambda",
            code=_lambda.Code.from_asset(
                "./src",
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -au /asset-input/. /asset-output",
                    ],
                ),
            ),
            handler="app.handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            environment={"TOPIC_ARN": topic.topic_arn},
            timeout=Duration.minutes(1),
        )

        topic.grant_publish(appsnip_lambda)
        rule = events.Rule(
            self,
            "ScheduleRule",
            schedule=events.Schedule.rate(Duration.hours(1)),
        )
        rule.add_target(targets.LambdaFunction(appsnip_lambda))
