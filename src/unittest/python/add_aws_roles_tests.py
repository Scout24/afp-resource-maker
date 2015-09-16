import unittest2 as unittest
from mock import patch, Mock, ANY
from requests.utils import quote
import json
import boto

from add_aws_roles import (RoleAdder,
                           CanNotContinueException,
                           _get_credentials,
                           )


class TestGetCredentials(unittest.TestCase):

    @patch('__builtin__.raw_input')
    def test_should_return_none_none(self, raw_input_mock):
        raw_input_mock.return_value = ''
        received = _get_credentials()
        self.assertEqual(received, (None, None))

    @patch('__builtin__.raw_input')
    def test_should_return_value_none(self, raw_input_mock):
        raw_input_mock.side_effect = ['XXYYZZ', '']
        received = _get_credentials()
        self.assertEqual(received, ('XXYYZZ', None))

    @patch('__builtin__.raw_input')
    def test_should_return_value_value(self, raw_input_mock):
        raw_input_mock.side_effect = ['XXYYZZ', 'AABBCC']
        received = _get_credentials()
        self.assertEqual(received, ('XXYYZZ', 'AABBCC'))


class TestRoleAdder(unittest.TestCase):

    def setUp(self):
        self.roles = ['devfoo', 'devbar']
        self.prefix = 'rz_'
        self.trusted_arn = 'arn:test'

    @patch('add_aws_roles._boto_connect')
    def test_initialization_of_role_adder(self, boto_connect_mock):
        access_key_id = None
        secret_access_key = None
        role_adder = RoleAdder(
            self.roles,
            self.prefix,
            self.trusted_arn,
            access_key_id,
            secret_access_key,
        )
        self.assertEqual(self.roles, role_adder.roles)
        self.assertEqual(self.prefix, role_adder.prefix)
        self.assertEqual(self.trusted_arn, role_adder.trusted_arn)
        boto_connect_mock.assert_called_once_with(None, None)

    @patch('add_aws_roles._boto_connect')
    def test_init_of_role_adder_with_aws_credentials(self, boto_connect_mock):
        access_key_id = 'access_key_id'
        secret_access_key = 'secret_access_key'
        RoleAdder(
            self.roles,
            self.prefix,
            self.trusted_arn,
            access_key_id,
            secret_access_key,
        )
        boto_connect_mock.assert_called_once_with(
            'access_key_id',
            'secret_access_key')


class TestAddingRoles(unittest.TestCase):

    @patch('add_aws_roles._boto_connect')
    def setUp(self, mock_boto_connect):
        self.mock_boto_connection = Mock()
        mock_boto_connect.return_value = self.mock_boto_connection
        self.roles = ['devfoo', 'devbar']
        self.prefix = 'rz_'
        self.trusted_arn = 'arn:test'
        self.policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": self.trusted_arn
                    },
                    "Action": "sts:AssumeRole"
                }
            ]}
        access_key_id = None
        secret_access_key = None
        self.role_adder = RoleAdder(
            self.roles,
            self.prefix,
            self.trusted_arn,
            access_key_id,
            secret_access_key,
        )

    def test_add_role_should_call_boto_create_role(self):
        self.role_adder.add_role('devfoo')
        self.mock_boto_connection.create_role.assert_called_once_with('devfoo')

    @patch('add_aws_roles.RoleAdder.message')
    def test_add_role_should_handle_existing_role(self, message_mock):

        self.mock_boto_connection.create_role.side_effect = \
            [boto.exception.BotoServerError('', '', {'Error': {"Code": "EntityAlreadyExists"}})]
        self.role_adder.add_role('devfoo')
        message_mock.assert_called_once_with('devfoo', 'Already exists')

    def test_add_role_should_raise_exception_on_limit_exceeded(self):

        self.mock_boto_connection.create_role.side_effect = \
            [boto.exception.BotoServerError('', '', {'Error': {"Code": "LimitExceeded"}})]
        self.assertRaises(CanNotContinueException, self.role_adder.add_role, 'devfoo')

    def test_add_role_should_raise_exception_on_incorrect_permissions(self):

        self.mock_boto_connection.create_role.side_effect = \
            [boto.exception.BotoServerError('', '', {'Error': {"Code": "InvalidClientTokenId"}})]
        self.assertRaises(CanNotContinueException, self.role_adder.add_role, 'devfoo')

    def test_add_role_should_raise_exception_on_other_exceptions(self):

        self.mock_boto_connection.create_role.side_effect = \
            [boto.exception.BotoServerError('', '', '')]
        self.assertRaises(CanNotContinueException, self.role_adder.add_role, 'devfoo')

    def test_add_trust_relationship_shld_call_update_assume_role_policy(self):
        self.role_adder.add_trust_relationship('devfoo')
        self.mock_boto_connection.update_assume_role_policy.\
            assert_called_once_with('devfoo', ANY)

    def test_add_trust_relationship_should_throw_exception_on_error(self):
        self.mock_boto_connection.update_assume_role_policy.side_effect = \
            [boto.exception.BotoServerError('', '', {'Error': {"Code": "InvalidClientTokenId"}})]
        self.assertRaises(CanNotContinueException,
                          self.role_adder.add_trust_relationship,
                          'devfoo')

    def test_check_role_policy_should_return_true_on_already_set_policy(self):
        assume_role_policy_doc = quote(
            json.dumps(self.policy))
        boto_return_value = {
            'get_role_response': {
                'get_role_result': {
                    'role': {
                        'assume_role_policy_document': assume_role_policy_doc,
                    }
                },
            }
        }
        self.mock_boto_connection.get_role.return_value = boto_return_value
        self.assertTrue(self.role_adder.check_role_policy('devfoo'))

    def test_check_role_policy_should_return_false_on_no_policy(self):
        assume_role_policy_doc = quote(
            json.dumps({}))
        boto_return_value = {
            'get_role_response': {
                'get_role_result': {
                    'role': {
                        'assume_role_policy_document': assume_role_policy_doc,
                    }
                },
            }
        }
        self.mock_boto_connection.get_role.return_value = boto_return_value
        self.assertFalse(self.role_adder.check_role_policy('devfoo'))
