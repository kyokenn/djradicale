DjRadicale
==========

[Radicale](http://radicale.org/) is a free and open-source CalDAV and CardDAV server.

DjRadicale is an Django Application for integration Radicale with a Django.


Features
========

With all features that Radicale have you will also get:

* Django Models as a storage backend (it's possible to use any database supported by Django)
* Django Admin web interface for browsing/editing stored data
* Django Authentication as an authentication backend
* Django Settings as a Radicale config


Requirements
============

* Python >= 3.0
* Django >= 4.0.1
* Radicale >= 3.1.2, < 4.0.0


Installation
============

Install using PIP
-----------------

```
$ pip install djradicale
```

Configuration
=============

Modify your settings.py
-----------------------

```python
INSTALLED_APPS = (
    ...
    'djradicale',
    ...
)

DJRADICALE_PREFIX = '/radicale/'
DJRADICALE_CONFIG = {
    'auth': {
        'type': 'djradicale.auth',
    },
    'rights': {
        'type': 'djradicale.rights',
    },
    'storage': {
        'type': 'djradicale.storage',
    },
}

```

Modify you urls.py
------------------

```python
urlpatterns = [
    ...
    path("" + settings.DJRADICALE_PREFIX.lstrip("/"),
         include(("djradicale.urls", "djradicale-caldav"), namespace="djradicale")),
    ...
]
```

well-known urls configuration
=============================

You need to choose an implementation for handling of the "well-known" urls

External DjRadicale implementation
----------------------------------

Add this to your urls'py:
```python
from djradicale.views import WellKnownView

urlpatterns = [
    ...
    path(".well-known/caldav",
         WellKnownView.as_view(type="caldav"), name="well-known-caldav"),
    path(".well-known/carddav",
         WellKnownView.as_view(type="carddav"), name="well-known-carddav"),
    ...
]
```
