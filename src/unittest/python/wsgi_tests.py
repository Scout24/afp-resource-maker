#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest2 import TestCase
from webtest import TestApp

import afp_ressource_maker.wsgi as wsgi_api


class BaseWsgiApiTests(TestCase):
    def setUp(self):
        environment = dict(CONFIG_PATH='/etc/afp-ressource-maker')
        self.app = TestApp(wsgi_api.get_webapp(),
                           extra_environ=environment)


class WsgiApiTests(BaseWsgiApiTests):
    def test_should_make_role(self):
        result = self.app.put('/role/testrole')
        self.assertEqual(result.status_int, 200)

    def test_status_good_case(self):
        result = self.app.get('/status')
        expected_json = {"status": "200", "message": "OK"}
        self.assertEqual(result.json, expected_json)
