===================
afp-ressource-maker
===================

Create ressources on aws, which are needed by afp-core. For this you have a
commandline tool and a *wsgi* endpoint.

Configuration
=============

By default the configuration directory points to ``/etc/afp-ressource-maker``.
For testing purposes you are able to override this by using the ``--config``
switch on the commandline tool.

Apache
------
For the wsgi endpoint you can use e.g. apache. The configuration part could
look like this:

.. code-block:: apache

    WSGIScriptAlias /api/latest/ressources

Licence
=======

Copyright 2015 Immobilienscout24 GmbH

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
