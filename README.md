[![Build Status](https://api.travis-ci.org/uw-it-aca/django-aws-message.svg?branch=master)](https://travis-ci.org/uw-it-aca/django-aws-message)
[![Coverage Status](https://coveralls.io/repos/uw-it-aca/django-aws-message/badge.png?branch=master)](https://coveralls.io/r/uw-it-aca/django-aws-message?branch=master)

ACA AWS SNS/SQS Message App
===========================

A Django Application on which to build AWS SNS endpoints and SQS gatherers

Installation
------------

**Project directory**

Install django-aws-message in your project.

    $ cd [project]
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
