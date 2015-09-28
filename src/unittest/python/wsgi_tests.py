#!/usr/bin/python
# -*- coding: utf-8 -*-

from unittest2 import TestCase
from webtest import TestApp

import afp_ressource_maker.wsgi as wsgi_api


class WsgiApiTests(TestCase):
    def setUp(self):
        self.app = TestApp(wsgi_api.get_webapp())
