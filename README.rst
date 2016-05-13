django-tornado-websockets
=========================

.. image:: https://coveralls.io/repos/github/Kocal/django-tornado-websockets/badge.svg?branch=develop
    :target: https://coveralls.io/github/Kocal/django-tornado-websockets?branch=develop

Django-tornado-websockets is a useful solution to provide an easy way to use Tornado WebSockets with a Django
application.

Documentation
-------------

Documentation is available on readthedocs:

- Stable: http://django-tornado-websockets.readthedocs.io/en/stable/
- Latest: http://django-tornado-websockets.readthedocs.io/en/latest/
- Develop: http://django-tornado-websockets.readthedocs.io/en/develop/

Compatibility
-------------

All django-tornado-websockets unit tests fail on Travis (`see logs <https://s3.amazonaws.com/archive.travis-ci.org/
jobs/130111696/log.txt>`_) and I can't find where and how it fails.

Also you can run tests with Tox ``$ tox -r -e pyXX-djangoXX``, it works for Python 2.7/3.3 but it fails for Python
3.4/3.5, showing the same error than Travis one. Here a compatibility table of unit tests I made of my machine:

+------------+----------------+----------------+
|            | Django 1.8     | Django 1.9     |
+============+================+================+
| Python 2.7 | Works fine     | Works fine     |
+------------+----------------+----------------+
| Python 3.3 | Works fine     | Not supported  |
+------------+----------------+----------------+
| Python 3.4 | Same as Travis | Same as Travis |
+------------+----------------+----------------+
| Python 3.5 | Same as Travis | Same as Travis |
+------------+----------------+----------------+

To conclude, when I read the traceback it seems this error come from Tornado HTTP client that I used for tests:

.. code-block::

    Traceback (most recent call last):
      File "/home/kocal/Dev/Python/django-tornado-websockets/.tox/py35-django19/lib/python3.5/site-packages/tornado/http1connection.py", line 238, in _read_message
        delegate.finish()
      File "/home/kocal/Dev/Python/django-tornado-websockets/.tox/py35-django19/lib/python3.5/site-packages/tornado/http1connection.py", line 651, in finish
        return self._delegate.finish()
      File "/home/kocal/Dev/Python/django-tornado-websockets/.tox/py35-django19/lib/python3.5/site-packages/tornado/simple_httpclient.py", line 518, in finish
        self.client.fetch(new_request, final_callback)
        AttributeError: 'NoneType' object has no attribute 'fetch'
