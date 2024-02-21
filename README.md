# AWS SNS/SQS Message App

[![Build Status](https://github.com/uw-it-aca/aws-message-client/workflows/tests/badge.svg?branch=main)](https://github.com/uw-it-aca/aws-message-client/actions)
[![Coverage Status](https://coveralls.io/repos/github/uw-it-aca/aws-message-client/badge.svg?branch=main)](https://coveralls.io/github/uw-it-aca/aws-message-client?branch=main)
[![PyPi Version](https://img.shields.io/pypi/v/aws-message-client.svg)](https://pypi.python.org/pypi/aws-message-client)
![Python versions](https://img.shields.io/badge/python-3.10-blue.svg)

Application on which to build AWS SNS endpoints and SQS gatherers

Installation
------------

    $ pip install aws-message-client

Project settings.py
------------------

**AWS App settings**

     AWS_SQS = {
         '<settings_name>': {
             'QUEUE_ARN': 'arn:aws:sqs:...',
             'KEY_ID': '<longrandomlookingstring>',
             'KEY': '<longerrandomlookingstring>',
             'WAIT_TIME': 10,
             'VISIBILITY_TIMEOUT': 10,
             'MESSAGE_GATHER_SIZE': 10,
             'VALIDATE_SNS_SIGNATURE': True,
             'VALIDATE_BODY_SIGNATURE': False,
             'BODY_DECRYPT_KEYS': {
                '<key>': '<secret>',
             },
         },
         ...
     }
