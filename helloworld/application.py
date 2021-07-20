# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Purpose

Shows how to use the AWS SDK for Python (Boto3) with Amazon Simple Notification
Service (Amazon SNS) to create notification topics, add subscribers, and publish
messages.
"""

from flask import Flask, Response, request
from helloworld.flaskrun import flaskrun
import requests
from flask_cors import CORS
import json
import logging
import time
import boto3
from botocore.exceptions import ClientError
application = Flask(__name__)
CORS(application, resources={r"/*": {"origins": "*"}})


    
@application.route('/sms/<phone_number>', methods=['POST'])
def publish_text_message(phone_number):
    """
    Publishes a text message directly to a phone number without need for a
    subscription.

    :param phone_number: The phone number that receives the message.
    :param message: The message to send.
    :return: The ID of the message.
    
    """
    
       # get post data  
    data = request.data
    # convert the json to dictionary
    data_dict = json.loads(data)
    # retreive the parameters
    message = data_dict.get('message','default')
    client = boto3.client('sns', region_name='us-east-1')
    response = client.publish(
        PhoneNumber=phone_number, Message=message)
    message_id = response['MessageId']
    return message_id

if __name__ == '__main__':
    flaskrun(application)
    