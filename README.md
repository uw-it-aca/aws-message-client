# AWS SNS/SQS Message App

[![Build Status](https://github.com/uw-it-aca/django-aws-message/workflows/tests/badge.svg?branch=main)](https://github.com/uw-it-aca/django-aws-message/actions)
[![Coverage Status](https://coveralls.io/repos/github/uw-it-aca/django-aws-message/badge.svg?branch=main)](https://coveralls.io/github/uw-it-aca/django-aws-message?branch=main)
[![PyPi Version](https://img.shields.io/pypi/v/django-aws-message.svg)](https://pypi.python.org/pypi/django-aws-message)
![Python versions](https://img.shields.io/pypi/pyversions/django-aws-message.svg)

Application on which to build AWS SNS endpoints and SQS gatherers

Installation
------------

    $ pip install django-aws-message

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
