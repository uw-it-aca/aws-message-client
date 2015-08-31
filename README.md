ACA AWS SNS/SQS Message App
===========================

A Django Application on which to build AWS SNS endpoints and SQS gatherers

Installation
------------

**Project directory**

Install django-aws-message in your project.

    $ cd [project]
    $ pip install -e git+https://github.com/uw-it-aca/django-aws-message/#egg=django_aws_message

Project settings.py
------------------

**AWS App settings**

     # AWS SQS gather app
     AWS_SQS = {
         'ENROLLMENT' : {
             'TOPIC_ARN' : 'arn:aws:sns:...',
             'QUEUE': 'some:specific:queue:id',
             'KEY_ID': '<lograndomlookingstring>',
             'KEY': '<longerrandomlookingstring>',
             'VISIBILITY_TIMEOUT': 60,
             'MESSAGE_GATHER_SIZE': 12,
             'VALIDATE_SNS_SIGNATURE': True,
             'VALIDATE_MSG_SIGNATURE': True,
             'PAYLOAD_SETTINGS': {}
         }
     }
