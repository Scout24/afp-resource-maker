#!/usr/bin/env python
# -*- coding: utf-8 -*-


class LimitExceededException(Exception):
    """ Signify that the program can not continue. """
    pass


class AWSErrorException(Exception):
    """ Signify that the program can not continue. """
    pass


class AlreadyExistsException(Exception):
    """ Signify that the entity already exists. """
    pass


class RoleMaker(object):
    def __init__(self,configuration):
        pass

    def _boto_connect(access_key_id, secret_access_key):
        pass

    def add_policy(self, role_name):
        """Add policy document to given role"""
        pass

    def add_trust_relationship(self, role_name):
        """Add trust relationship to given role"""
        pass

    def create_role(self, role_name):
        """Add Role to AWS"""
        pass

    def put_role(self, role_name):
        """Generate Role with Trust relationship and policy"""
        self.create_role(role_name)
        self.add_trust_relationship(role_name)
        self.add_policy(role_name)
