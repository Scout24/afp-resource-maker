#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

from functools import wraps
from yamlreader import yaml_load
from bottle import route, abort, request, put, default_app

from afp_resource_maker import RoleMaker


def with_exception_handling(old_function):
    """Decorator function to ensure proper exception handling"""
    @wraps(old_function)
    def new_function(*args, **kwargs):
        try:
            result = old_function(*args, **kwargs)
        except Exception:
            message = traceback.format_exc()
            abort(500, 'Exception caught {0}'.format(message))
        return result
    return new_function


@put('/role/<rolename>')
@with_exception_handling
def make_role(rolename):
    """Create a role and assign needed policies and trusted entities"""
    config = yaml_load(request.environ.get('CONFIG_PATH'))
    rolemaker = RoleMaker(config)
    rolemaker.make_role(rolename)
    return


@route('/status')
def status():
    """Return status page for monitoring"""
    return {"status": "200", "message": "OK"}


def get_webapp():
    """Give back the bottle default_app, for direct use in wsgi scripts"""
    return default_app()