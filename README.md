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

     # AWS SQS gather app
     AWS_SQS = {
         '[settings_name]' : {
             'TOPIC_ARN' : 'arn:aws:sqs:...',
             'KEY_ID': '<longrandomlookingstring>',
             'KEY': '<longerrandomlookingstring>',
             'VISIBILITY_TIMEOUT': 60,
             'MESSAGE_GATHER_SIZE': 10,
             'VALIDATE_SNS_SIGNATURE': True,
             'VALIDATE_MSG_SIGNATURE': True,
             'PAYLOAD_SETTINGS': {}
         }
     }
