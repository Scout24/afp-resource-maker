# -*- coding: utf-8 -*-


import boto
import json
from requests.utils import unquote


class CanNotContinueException(Exception):
    """ Signify that the program can not continue. """
    pass


class AlreadyExistsException(Exception):
    """ Signify that the entity already exists. """
    pass


def _boto_connect(access_key_id, secret_access_key):
    try:
        return boto.connect_iam(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key)
    except boto.exception.NoAuthHandlerFound, exc:
        raise CanNotContinueException(exc)


def _get_credentials():
    print "Enter credentials. Leave empty to use boto defaults."
    access_key_id = raw_input("Access Key ID: ").strip() or None
    if access_key_id is None:
        secret_access_key = None
    else:
        secret_access_key = raw_input("Secret Access Key: ").strip() or None
    return access_key_id, secret_access_key


class RoleAdder(object):
    def __init__(self, roles, prefix, trusted_arn,
                 access_key_id, secret_access_key):
        self.padding = max(map(len, roles)) + len(prefix)
        self.roles = roles
        self.prefix = prefix or ""
        self.trusted_arn = trusted_arn
        self.boto_connection = _boto_connect(access_key_id, secret_access_key)
        self.trust_policy = {
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

    def message(self, full_role, message):
        messagetemplate = "{role:%d} {message}" % (self.padding)
        print messagetemplate.format(
            role=full_role,
            message=message)

    def die(role, message, intro='Cannot create role'):
        error = "{intro} {role}: {message}".format(
            intro=intro,
            role=role,
            message=message)
        raise CanNotContinueException(error)

    def add_roles(self):
        for role in self.roles:
            full_role = self.prefix + role
            role_message = ""
            try:
                self.add_role(full_role)
            except AlreadyExistsException:
                role_message += "exists "
            else:
                role_message += "created"
            if self.trusted_arn:
                role_message += " and "
                try:
                    self.add_trust_relationship(full_role)
                except AlreadyExistsException:
                    role_message += "relationship exists "
                else:
                    role_message += "relationship created"
            self.message(full_role, role_message)

    def add_role(self, full_role):
        try:
            self.boto_connection.create_role(full_role)
        except boto.exception.BotoServerError, exc:
            if exc.error_code == "EntityAlreadyExists":
                raise AlreadyExistsException()
            elif exc.error_code in ("LimitExceeded", "InvalidClientTokenId"):
                self.die(full_role, exc.message)
            else:
                self.die(full_role, exc)

    def check_role_policy(self, full_role):
        aws_role = self.boto_connection.get_role(full_role)['get_role_response']['get_role_result']['role']
        assume_role_policy_string = aws_role['assume_role_policy_document']
        assume_role_policy_document = json.loads(unquote(assume_role_policy_string))
        return assume_role_policy_document == self.trust_policy

    def add_trust_relationship(self, full_role):
        if self.check_role_policy(full_role):
            raise AlreadyExistsException()
        try:
            self.boto_connection.update_assume_role_policy(
                full_role,
                json.dumps(self.trust_policy))
        except boto.exception.BotoServerError, exc:
            self.die(
                full_role,
                "Cannot add trust relationship to role: %s" % exc.message)
