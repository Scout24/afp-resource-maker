#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

from functools import wraps
from yamlreader import yaml_load
from bottle import route, abort, request, put, HTTPResponse, default_app

from afp_resource_maker import (RoleMaker,
                                InvalidClientTokenIdException,
                                LimitExceededException,
                                CanNotContinueException)


def with_exception_handling(old_function):
    """Decorator function to ensure proper exception handling"""
    @wraps(old_function)
    def new_function(*args, **kwargs):
        try:
            result = old_function(*args, **kwargs)
        except InvalidClientTokenIdException as error:
            abort(code=401, text=error)
        except LimitExceededException as error:
            abort(code=509, text=error)
        except CanNotContinueException as error:
            abort(code=502, text=error)
        except Exception:
            message = traceback.format_exc()
            abort(code=500, text='Exception caught {0}'.format(message))
        return result
    return new_function


def get_config():
    config_path = request.environ.get('CONFIG_PATH', '/etc/afp-resource-maker')
    return yaml_load(config_path)


@put('/role/<rolename>')
@with_exception_handling
def make_role(rolename):
    """Create a role and assign needed policies and trusted entities"""
    config = get_config()
    rolemaker = RoleMaker(config)
    rolemaker.make_role(rolename)
    return HTTPResponse(status=201)


@route('/status')
def status():
    """Return status page for monitoring"""
    get_config()
    return {"status": "200", "message": "OK"}


def get_webapp():
    """Give back the bottle default_app, for direct use in wsgi scripts"""
    return default_app()
