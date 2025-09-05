from django.db import connection
from django.db.models import Q, CharField, TextField
from django.db.models.fields.json import JSONField

try:
    from django.contrib.postgres.search import SearchVector
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False



class ListViewSearchMixin:pass