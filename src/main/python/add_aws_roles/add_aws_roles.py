# -*- coding: utf-8 -*-


import boto


class RoleAdder(object):
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
