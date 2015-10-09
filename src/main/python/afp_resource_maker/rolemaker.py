#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

import boto


class LimitExceededException(Exception):
    pass


class CanNotContinueException(Exception):
    pass


class InvalidClientTokenIdException(Exception):
    pass


class RoleMaker(object):
    """Create a role with policies to allow cross account operations"""

    def __init__(self, configuration):
        self.prefix = configuration['role']['prefix']
        self.trust_policy_document = \
            configuration['role']['trust_policy_document']
        self.policy_name = configuration['role']['policy_name']
        self.policy_document = configuration['role']['policy_document']
        access_key_id = configuration['access_key_id']
        secret_access_key = configuration['secret_access_key']
        self.boto_connection = self._boto_connect(access_key_id,
                                                  secret_access_key)

    def _boto_connect(self, access_key_id, secret_access_key):
        """Establish a boto iam connection and return the connection object"""
        try:
            return boto.connect_iam(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key)
        except boto.exception.NoAuthHandlerFound as exc:
            raise CanNotContinueException(exc)

    def _add_policy(self, role_name):
        """Add policy document to given role"""
        try:
            self.boto_connection.put_role_policy(role_name,
                                                 self.policy_name,
                                                 self.policy_document)
        except boto.exception.BotoServerError as exc:
            message = "Cannot add inline policy to role: %s" % exc.message
            raise CanNotContinueException(message)

    def _add_trust_relationship(self, role_name):
        """Add trust relationship to given role"""
        try:
            self.boto_connection.update_assume_role_policy(
                role_name, self.trust_policy_document)
        except boto.exception.BotoServerError as exc:
            message = "Cannot add trust relationship to role: %s" % exc.message
            raise CanNotContinueException(message)

    def _create_role(self, role_name):
        """Add Role to AWS"""
        try:
            self.boto_connection.create_role(role_name)
        except boto.exception.BotoServerError as exc:
            message = "Failed to create role: '{0}'".format(role_name)
            if exc.error_code == "EntityAlreadyExists":
                return
            elif exc.error_code == "LimitExceeded":
                raise LimitExceededException(message)
            elif exc.error_code == "InvalidClientTokenId":
                raise InvalidClientTokenIdException(message)
            else:
                raise CanNotContinueException(traceback.format_exc())

    def make_role(self, role_name):
        """Generate Role with Trust relationship and policy"""
        prefixed_role_name = '{0}{1}'.format(self.prefix, role_name)
        self._create_role(prefixed_role_name)
        self._add_trust_relationship(prefixed_role_name)
        self._add_policy(prefixed_role_name)
