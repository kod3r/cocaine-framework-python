# encoding: utf-8
#
#    Copyright (c) 2011-2013 Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2011-2013 Other contributors as noted in the AUTHORS file.
#
#    This file is part of Cocaine.
#
#    Cocaine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    Cocaine is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>. 
#

import urlparse

import msgpack

from _callablewrappers import proxy_factory

__all__ = ["http"]


class _HTTPResponse(object):

    def __init__(self, stream):
        self._stream = stream

    def write(self, body):
        self._stream.write(body)

    def write_head(self, code, headers):
        self._stream.write((code, headers))

    def close(self):
        self._stream.close()

    @property
    def closed(self):
        return self._stream.closed


class _HTTPRequest(object):

    def __init__(self, data):
        #self._data = msgpack.unpackb(data)
        method, url, version, headers, self._body = msgpack.unpackb(data)
        self._meta = dict()
        self._headers = dict(headers)
        self._meta['method'] = method
        self._meta['version'] = version
        self._meta['host'] = self._headers.get('host', '')
        self._meta['query_string'] = urlparse.urlparse(url).query
        tmp = urlparse.parse_qs(urlparse.urlparse(url).query)
        self._request = dict((k,v[0]) for k,v in tmp.iteritems() if len(v) > 0)

    @property
    def body(self):
        """Return request body"""
        return self._body

    @property
    def meta(self):
        """ Return dict like:
        {'cookies': {},
        'headers': {'ACCEPT': '*/*',
        'CONTENT-TYPE': '',
        'HOST': 'somehost',
        'USER-AGENT': 'curl/7.19.7 (x86_64-pc-linux-gnu) libcurl/7.19.7 OpenSSL/0.9.8k zlib/1.2.3.3 libidn/1.15'},
        'host': 'someurl.com',
        'method': 'GET',
        'path_info': '',
        'query_string': 'partnerID=ntp_tb',
        'remote_addr': '1.11.111.111',
        'script_name': '/someone/get/',
        'secure': False,
        'server_addr': '1.1.1.1',
        'url': 'someurl'}
        """
        return self._meta

    @property
    def request(self):
        return self._request


def http_request_decorator(obj):
    def dec(func):
        def wrapper(chunk):
            return func(_HTTPRequest(chunk))
        return wrapper
    obj.push = dec(obj.push)
    return obj


def http(func):
    return proxy_factory(func, response_handler=_HTTPResponse, request_handler=http_request_decorator)
