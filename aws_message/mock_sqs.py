from importlib import import_module
from hashlib import sha1
from http.client import HTTPSConnection
import socket
import ssl
import os
import sys
import inspect
import glob
import re
from django.conf import settings


class HTTPSConnectionValidating(HTTPSConnection):
    def __init__(self, host, port=None, key_file=None,
                 cert_file=None, timeout=None, strict=None):
        HTTPSConnection.__init__(
            self, host, port=port, key_file=key_file,
            cert_file=cert_file, timeout=timeout, strict=strict)
        self.key_file = key_file
        self.cert_file = cert_file
        self.timeout = timeout

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                    ca_certs=settings.AWS_CA_BUNDLE,
                                    cert_reqs=ssl.CERT_REQUIRED)


def https_connection_factory(host, port=None, strict=None):
    return HTTPSConnectionValidating(host, port=port, strict=strict,
                                     key_file=settings.EVENT_AWS_SQS_KEY,
                                     cert_file=settings.EVENT_AWS_SQS_CERT)


class SQSQueueMock(object):
    def __init__(self, *args, **kwargs):
        self._settings = kwargs.get('settings')
        self._fs_encoding = sys.getfilesystemencoding() or \
            sys.getdefaultencoding()
        self._app_mock_dirs = []
        self._seen_messages = []
        try:
            for app in settings.INSTALLED_APPS:
                mod = import_module(app)
                mock_dir = os.path.join(
                    os.path.dirname(mod.__file__), 'mock')
                if os.path.isdir(mock_dir):
                    data = {
                        'base': os.path.dirname(
                            mod.__file__).decode(self._fs_encoding),
                        'path': mock_dir.decode(self._fs_encoding),
                        'app': app,
                    }
                    self._app_mock_dirs.append(data)
        except Exception:
            pass

    def get_messages(self, max_msgs_to_fetch):
        try:
            module = self._calling_module()
            mock_dir = self._mock_dir(module)
            msg_files = glob.glob(os.path.join(mock_dir, 'message*'))
            for msg_file in msg_files:
                with open(msg_file, 'r') as handle:
                    msg = handle.read()
                    if self._hash(msg) not in self._seen_messages:
                        return [RawMessage(body=msg)]
        except Exception:
            pass

        return []

    def _hash(self, raw):
        return sha1(raw).hexdigest()

    def delete_message(self, msg):
        hash = self._hash(msg.get_body())
        if hash not in self._seen_messages:
            self._seen_messages.append(hash)

    def _calling_module(self):
        sqs_dir = os.path.dirname(__file__)
        for frame in inspect.stack():
            mod = inspect.getmodule(frame[0])
            if not mod.__file__.startswith(sqs_dir):
                return mod

        raise Exception("no calling module")

    def _mock_dir(self, module):
        dir = os.path.dirname(module.__file__)
        for mock_dir in self._app_mock_dirs:
            if dir.startswith(mock_dir['base']):
                msg_dir = os.path.join(mock_dir['path'],
                                       'aws_message',
                                       self._settings.get('QUEUE'))
                if os.path.isdir(msg_dir):
                    return msg_dir

        raise Exception("no mock directory")
