from django.conf import settings as django_settings

DEFAULT_SETTINGS = {
    "SHOW_WIDGET_DOCS_LINK": True,
    "SITE_TITLE":'Octopusdash',
    "ALLOW_UPLOADING_PLUGINS":False,
    
}

# Get user-defined dict if exists, otherwise empty dict
USER_SETTINGS = getattr(django_settings, "OCTOPUSDASH", {})

# Merge without overriding unspecified keys
DEFAULT_SETTINGS.update(USER_SETTINGS)

settings = DEFAULT_SETTINGS
