#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import route, default_app


@route('/role/<rolename>')
def make_role(rolename):
    """Create a role and assign needed policies and trusted entities"""
    pass


def get_webapp():
    """Give back the bottle default_app, for direct use in wsgi scripts"""
    return default_app()
