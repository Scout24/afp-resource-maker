===================
afp-resource-maker
===================
.. image:: https://travis-ci.org/ImmobilienScout24/afp-resource-maker.png?branch=master
   :alt: Travis build status image
   :align: left
   :target: https://travis-ci.org/ImmobilienScout24/afp-resource-maker

.. image:: https://coveralls.io/repos/ImmobilienScout24/afp-resource-maker/badge.png?branch=master
    :alt: Coverage status
    :target: https://coveralls.io/r/ImmobilienScout24/afp-resource-maker?branch=master

Create resources on aws, which are needed by afp-core. For this you have a
commandline tool and a *wsgi* endpoint.

Configuration
=============

By default the configuration directory points to ``/etc/afp-resource-maker``.
For testing purposes you are able to override this by using the ``--config``
switch on the commandline tool.

Credentials
-----------
Needed to make the api calls to aws. e.g. create a dedicated user for this:

.. code-block:: yaml

    access_key_id: AKIAIOSFODNN7EXAMPLE
    secret_access_key: aJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY

Role
----
The role settings especially the policies are important for the machine auth
functionality of `afp-core <https://github.com/ImmobilienScout24/afp-core>`_.

To make a cross account permission granting possible you need a trusted entity
with allowed **AssumeRole** permissions. And a policy which grants all, but
deny everything within the main account. Here is an example of the settings:

.. code-block:: yaml

    role:
        prefix: foobar_
        trust_policy_document: |
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::1234567890:user/my-federation-user"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
        policy_name: allow_all_except_own_account
        policy_document: |
            {
                "Version": "2012-10-17",
                "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Action": [
                        "*"
                    ],
                    "Resource": [
                        "*"
                    ]
                },
                {
                    "Sid": "",
                    "Effect": "Deny",
                    "Action": [
                        "*"
                    ],
                    "Resource": [
                        "arn:aws:iam::1234567890:*",
                        "arn:aws:ec2:*:1234567890:*",
                        "... and so on ..."
                    ]
                }]
            }

For a complete list use the policy generator from aws.

The advantage of this setup is, that you are able to create a multiaccount
setup, where the the other accounts can grant permission on roles from the
main account.

Apache
------
For the wsgi endpoint you can use e.g. apache. The configuration part could
look like this:

.. code-block:: apache

    <Location /api/latest/resources>
        SetEnv CONFIG_PATH "/etc/afp-resource-maker"
    </Location>
    WSGIScriptAlias /api/latest/resources

The ``CONFIG_PATH`` is important, else the script is unable to find its
configuration.

Licence
=======

Copyright 2015 Immobilien Scout GmbH

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
