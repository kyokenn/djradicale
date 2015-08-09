djradicale
==========

Radicale is a free and open-source CalDAV and CardDAV server.

DjRadicale is an Django Application for integration Radicale with a Django.


Features
--------

With all features that Radicale have you will also get:

* Django Models as a storage backend (it's possible to use any database supported by Django)
* Django Admin web interface for browsing/editing stored data
* Django Authentication as an authentication backend
* Permissions backend based on regexp stored in Django Settings
* Django Settings as a Radicale config


Requirements
------------

* Python >= 3.0
* Django >= 1.7


Installation
------------

* pip install djradicale
* Modify your project's settings.py:

```python
INSTALLED_APPS = (
    ...
    'djradicale',
)

DJRADICALE_CONFIG = {
    'server': {
        'base_prefix': '/pim/',
        'realm': 'Radicale - Password Required',
    },
    'encoding': {
        'request': 'utf-8',
        'stock': 'utf-8',
    },
    'auth': {
        'type': 'custom',
        'custom_handler': 'djradicale.auth.django',
    },
    'rights': {
        'type': 'custom',
        'custom_handler': 'djradicale.rights.django',
    },
    'storage': {
        'type': 'custom',
        'custom_handler': 'djradicale.storage.django',
    },
    'well-known': {
        'carddav': '/pim/%(user)s/addressbook.vcf',
        'caldav': '/pim/%(user)s/calendar.ics',
    },
}

DJRADICALE_RIGHTS = {
    'rw': {
        'user': '.+',
        'collection': '^%(login)s/[a-z0-9\.\-_]+\.(vcf|ics)$',
        'permission': 'rw',
    },
    'rw-root': {
        'user': '.+',
        'collection': '^%(login)s$',
        'permission': 'rw',
    },
}
```

* Modify you project's urls.py:

```python
urlpatterns = [
    ...
    url(r'^' + settings.DJRADICALE_CONFIG['server']['base_prefix'].lstrip('/'),
        include('djradicale.urls', namespace='djradicale')),
    ...
]
```

* Choose one from those implementations for handling of "well-known" urls:

1. External DjRadicale implementation. Add this to your urls'py:

```python
from djradicale.views import WellKnownView

urlpatterns = [
    ...
    url(r'^\.well-known/(?P<type>(caldav|carddav))$',
        WellKnownView.as_view(), name='djradicale_well-known'),
    ...
]
```

2. Internal Radicale implementation (some clients does not work with it). Add this to your urls'py:

```python
from djradicale.views import DjRadicaleView

urlpatterns = [
    ...
    url(r'^\.well-known/(?P<type>(caldav|carddav))$',
        DjRadicaleView.as_view(), name='djradicale_well-known'),
    ...
]
```
