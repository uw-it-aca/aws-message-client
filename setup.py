import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/aws-message-client>`_.
"""

version_path = 'aws_message/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='aws-message-client',
    version=VERSION,
    packages=['aws_message'],
    include_package_data=True,
    install_requires = [
        'boto3',
        'pycrypto',
        'oscrypto',
        'urllib3',
        'commonconf',
        'uw-memcached-clients~=1.0',
    ],
    license='Apache License, Version 2.0',
    description=('An application on which to build AWS SQS endpoints and '
                 'SQS gatherers'),
    long_description=README,
    url='https://github.com/uw-it-aca/aws-message-client',
    author = "UW-IT AXDD",
    author_email = "aca-it@uw.edu",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
