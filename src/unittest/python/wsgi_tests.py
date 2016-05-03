#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import yaml
import shutil
import tempfile

import boto

from moto import mock_iam
from webtest import TestApp
from mock import patch, Mock
from unittest2 import TestCase

import afp_resource_maker.wsgi as wsgi_api


class BaseWsgiApiTests(TestCase):
    def setUp(self):
        self.patcher = patch('afp_resource_maker.RoleMaker._boto_connect')
        self.mock_boto_connect = self.patcher.start()
        self.mock_boto_connection = Mock()
        self.mock_boto_connect.return_value = self.mock_boto_connection
        # https://github.com/gabrielfalcao/HTTPretty/issues/122
        self.restore_proxy = os.environ.get('http_proxy')
        if self.restore_proxy is not None:
            del os.environ['http_proxy']
        self.config_path = tempfile.mkdtemp(prefix='afp-resource-maker-tests-')
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
        # https://github.com/gabrielfalcao/HTTPretty/issues/122
        if self.restore_proxy:
            os.environ['http_proxy'] = self.restore_proxy
        shutil.rmtree(self.config_path)
        self.patcher.stop()

    @staticmethod
    def writeyaml(data, yamlfile):
        with open(yamlfile, "w") as target:
            target.write(yaml.dump(data))


class WsgiApiTests(BaseWsgiApiTests):
    @mock_iam
    def test_should_make_role(self):
        result = self.app.put('/role/testrole')
        self.assertEqual(result.status_int, 201)

    def test_status_good_case(self):
        result = self.app.get('/status')
        expected_json = {"status": "200", "message": "OK"}
        self.assertEqual(result.json, expected_json)

    def test_status_bad_case_with_missing_config(self):
        missing_config = os.path.join(self.config_path, "missing_config.yaml")
        env_with_wrong_config_path = {'CONFIG_PATH': missing_config}
        self.app = TestApp(wsgi_api.get_webapp(), extra_environ=env_with_wrong_config_path)

        result = self.app.get('/status', expect_errors=True)

        self.assertEqual(result.status_int, 500)

    def test_should_give_401_return_code(self):
        self.mock_boto_connection.create_role.side_effect = \
            [boto.exception.BotoServerError('', '', {'Error': {"Code": "InvalidClientTokenId"}})]
        result = self.app.put('/role/testrole', expect_errors=True)
        self.assertEqual(result.status_int, 401)

    def test_should_give_509_return_code(self):
        self.mock_boto_connection.create_role.side_effect = \
            [boto.exception.BotoServerError('', '', {'Error': {"Code": "LimitExceeded"}})]
        result = self.app.put('/role/testrole', expect_errors=True)
        self.assertEqual(result.status_int, 509)

    def test_should_give_502_return_code(self):
        self.mock_boto_connection.create_role.side_effect = \
            [boto.exception.BotoServerError('', '', {'Error': {"Code": "CanNotContinueException"}})]
        result = self.app.put('/role/testrole', expect_errors=True)
        self.assertEqual(result.status_int, 502)

    @patch('afp_resource_maker.wsgi.yaml_load')
    def test_load_config_uses_default_path(self, mock_yaml_load):
        env_without_config_path = {}
        self.app = TestApp(wsgi_api.get_webapp(), extra_environ=env_without_config_path)

        wsgi_api.get_config()

        mock_yaml_load.assert_called_with('/etc/afp-resource-maker')
