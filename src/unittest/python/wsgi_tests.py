#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import yaml
import shutil
import tempfile

from moto import mock_iam
from webtest import TestApp
from unittest2 import TestCase

import afp_ressource_maker.wsgi as wsgi_api


class BaseWsgiApiTests(TestCase):
    def setUp(self):
        self.config_path = tempfile.mkdtemp(prefix='afp-ressource-maker-tests-')
        auth_config = {
            'access_key_id': 'AKIAIOSFODNN7EXAMPLE',
            'secret_access_key': 'aJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY'
        }
        role_config = {
            'role': {
                'prefix': 'foobar_',
                'trust_policy_document': '',
                'policy_name': 'test_policy_name',
                'policy_document': ''
            },
        }
        self.writeyaml(auth_config, os.path.join(self.config_path, 'auth.yaml'))
        self.writeyaml(role_config, os.path.join(self.config_path, 'role.yaml'))
        environment = dict(CONFIG_PATH=self.config_path)
        self.app = TestApp(wsgi_api.get_webapp(), extra_environ=environment)

    def tearDown(self):
        shutil.rmtree(self.config_path)

    @staticmethod
    def writeyaml(data, yamlfile):
        with open(yamlfile, "w") as target:
            target.write(yaml.dump(data))


class WsgiApiTests(BaseWsgiApiTests):
    @mock_iam
    def test_should_make_role(self):
        result = self.app.put('/role/testrole')
        self.assertEqual(result.status_int, 200)

    def test_status_good_case(self):
        result = self.app.get('/status')
        expected_json = {"status": "200", "message": "OK"}
        self.assertEqual(result.json, expected_json)
