#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto
import unittest2 as unittest

from mock import patch, Mock
from afp_resource_maker import (RoleMaker,
                                LimitExceededException,
                                CanNotContinueException)


class TestRoleMaker(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('afp_resource_maker.RoleMaker._boto_connect')
        self.mock_boto_connect = self.patcher.start()
        self.mock_boto_connection = Mock()
        self.mock_boto_connect.return_value = self.mock_boto_connection
        self.trust_policy_document = '''{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::123456789:role/foobar"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]}'''
        self.policy_name = 'policy name foobar'
        self.role_name = 'testrole'
        self.policy_document = '''{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*"
                }
            ]}'''
        self.configuration = {
            'access_key_id': None,
            'secret_access_key': None,
            'role': {
                'prefix': 'foobar_',
                'trust_policy_document': self.trust_policy_document,
                'policy_name': self.policy_name,
                'policy_document': self.policy_document,
            }
        }
        self.rolemaker = RoleMaker(self.configuration)

    def tearDown(self):
        self.patcher.stop()


class TestCreateRole(TestRoleMaker):
    def test_create_role_should_call_boto_create_role(self):
        self.rolemaker._create_role(self.role_name)
        self.mock_boto_connection.create_role.\
            assert_called_once_with(self.role_name)

    def test_create_role_should_handle_existing_role(self):
        error_dict = {'Error': {"Code": "EntityAlreadyExists"}}
        self.mock_boto_connection.create_role.side_effect = \
            [boto.exception.BotoServerError('', '', error_dict)]
        self.rolemaker._create_role(self.role_name)

    def test_create_role_should_raise_exception_on_limit_exceeded(self):
        error_dict = {'Error': {"Code": "LimitExceeded"}}
        self.mock_boto_connection.create_role.side_effect = \
            [boto.exception.BotoServerError('', '', error_dict)]
        self.assertRaises(LimitExceededException,
                          self.rolemaker._create_role,
                          self.role_name)

    def test_create_role_should_raise_exception_on_other_exceptions(self):
        self.mock_boto_connection.create_role.side_effect = \
            [boto.exception.BotoServerError('', '', '')]
        self.assertRaises(CanNotContinueException,
                          self.rolemaker._create_role,
                          self.role_name)


class TestAddTrustRelationship(TestRoleMaker):
    def test_add_trust_relationship_should_call_update_assume_role_policy(self):
        self.rolemaker._add_trust_relationship(self.role_name)
        self.mock_boto_connection.update_assume_role_policy.\
            assert_called_once_with(self.role_name, self.trust_policy_document)

    def test_add_trust_relationship_should_throw_exception_on_error(self):
        self.mock_boto_connection.update_assume_role_policy.side_effect = \
            [boto.exception.BotoServerError('', '', '')]
        self.assertRaises(CanNotContinueException,
                          self.rolemaker._add_trust_relationship,
                          self.role_name)


class TestAddPolicy(TestRoleMaker):
    def test_add_policy_should_call_put_role_policy(self):
        self.rolemaker._add_policy(self.role_name)
        self.mock_boto_connection.put_role_policy.\
            assert_called_once_with(self.role_name,
                                    self.policy_name,
                                    self.policy_document)

    def test_add_policy_should_throw_exception_on_error(self):
        self.mock_boto_connection.put_role_policy.side_effect = \
            [boto.exception.BotoServerError('', '', '')]
        self.assertRaises(CanNotContinueException,
                          self.rolemaker._add_policy,
                          self.role_name)
