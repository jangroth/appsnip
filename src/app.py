import urllib3
import os
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

SNIP_URL = "https://www.apple.com/au/shop/refurbished/mac/2024-macbook-air-24gb"
# SNIP_URL = "https://www.ccc.de"
TOPIC_ARN = os.getenv("TOPIC_ARN")


logger = Logger()


class AppSnip(object):

    def __init__(self):
        self.sns = boto3.client("sns")
        self.http = urllib3.PoolManager()

    def _test_url(self):
        resp = self.http.request("GET", SNIP_URL, redirect=False)
        return resp

    def _send_sns(self, message):
        self.sns.publish(TopicArn=TOPIC_ARN, Message=message)

    def handler(self, event, context):
        resp = self._test_url()

        if resp.status == 200:
            message = f"Success! {SNIP_URL} is up."
        else:
            message = f"Bad Luck! {SNIP_URL} is redirecting."
        self._send_sns(message=message)
        return message


@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    return AppSnip().handler(event, context)
