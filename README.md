# OctopusDash v2

OctopusDash is now v2 — a fully redesigned Django admin dashboard with DaisyUI integration, inline form updates, context menu support, computed fields, custom sidebar icons, and much more.

> Important: This is a complete rewrite of the API. The old version is deprecated. Please migrate your admin registrations accordingly.

---

## What’s New in v2

**1. Inline Form Updates**

Edit objects directly in the table without reloading the entire page. Only forms marked as dirty (i.e., their data changed) are submitted, boosting performance. This approach improves responsiveness compared to bulk updates, which are planned for a future release. Fields marked as editable in `list_editable` can be updated inline, while computed fields are read-only and accessed via queryset annotations for high performance.


**2. Computed Fields**

* Add dynamic fields to your `list_display` that return Django annotation expressions.
* Accessed efficiently on the queryset level for high performance without frequent DB hits.

**3. Context Menu Support**

* Right-click on any table row to access actions and shortcuts.
* Enables faster workflow for admins.

**4. Custom Sidebar Icons**

* Assign unique icons to each model in the sidebar.
* Enhances visual navigation and recognition.

**5. DaisyUI Themed UI**

* Fully responsive, clean design powered by TailwindCSS and DaisyUI.
* Supports dark/light mode automatically via themes.

**6. Custom Actions & Widgets**

* Define actions per model directly in `ModelAdmin`.
* Extend the UI with custom inputs, widgets, and reusable components.

**7. Performance-Focused Design**

* Inline-form updates replace bulk updates by default for speed.
* Efficient queryset annotations for computed fields.
* Ready for high-volume dashboards.

---

## Coming Soon Features

* **Custom Widgets System**: Developers will be able to create plugins that can edit, organize, or modify model instances (e.g., for analytics or other operations). Plugins can be installed via PyPI or added to a project folder called `widgets`, and OctopusDash will automatically handle them.

* **Pre-made UI Widgets**: A set of ready-to-use UI components to extend the UI/UX, including transfer lists, radio option cards, dropdown menus, and more.

* **Horizontal Filtering & Search**: Enhanced table filtering and search capabilities for faster and more precise data exploration.

* **Object & Field Permissions**: Fine-grained permissions to control whether users can view, edit, or add specific fields, combined with role-based access control.

* **And much more**: Additional features to improve dashboard customization, workflow, and performance will be added over time.


## Screenshots

![Screenshot](screenshots/screenshot1.png)
![Screenshot](screenshots/screenshot2.png)
![Screenshot](screenshots/screenshot5.png)
![Screenshot](screenshots/screenshot3.png)
![Screenshot](screenshots/screenshot4.png)


---



## Quick Start

### ⚠️ Important Note
Currently, OctopusDash does not implement Permission validation
It only checks if the user `is_supperuser` or `is_staff`
This means:

* Any user with these attributes set to True can have access to /dashboard/ and use it.

* You are responsible for securing this route (e.g., using Django’s built-in authentication, middleware, or a reverse proxy).

Authentication support is planned for a future release.

To enable **OctopusDash**, follow these steps:

1. Clone the repo into your `django` project:

```bash

git clone https://github.com/husseinaneemsec/octopusdash ./my_django_project/octopusdash

```


2. Add `octopusdash` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    "octopusdash",
    # ...
]
```

3. Add `octopusdash` global context:

```python

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'octopusdash.context.octopusdash_context'
            ],
        },
    },
]
```

4. Include the OctopusDash URLs in your project’s main urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("octopusdash.urls")),
]
```

5. Register your `models`:

```python
from octopusdash.admin import admin as od_admin, ModelAdmin, action
from blog.models import Post

class PostAdmin(ModelAdmin):
    list_display = [
        'title', 'computed_field', 'slug', 'author', 'category',
        'status', 'is_pinned', 'is_featured',
        'scheduled_at', 'created_at', 'updated_at', 'published_at',
        'reading_time', 'word_count'
    ]
    list_editable = ['author', 'is_pinned']

    # Computed field: must return a Django annotation expression
    def get_computed_field(self):
        from django.db.models import Value
        from django.db.models.functions import Concat
        return Concat('title', Value(' '), 'author__username')

    @action("Mark posts as featured")
    def mark_posts_as_featured(self, queryset):
        queryset.update(is_featured=True)

class PostImageAdmin(ModelAdmin):
    list_display = ['post', 'image', 'caption']

# Register models to OctopusDash
od_admin.register(Post, PostAdmin)
od_admin.register(PostImage, PostImageAdmin)
```

6. Add `OCTOPUSDASH` configuration for site customization

```python
OCTOPUSDASH = {
    'SHOW_WIDGET_DOCS_LINK':False,
    'SITE_TITLE':"My Site."
}

```

**Notes:**

* `computed_field` is not a model field. It works only via annotation expressions to improve performance.
* Inline-form updates are used for single-row updates instead of bulk updates to boost responsiveness. Bulk update and bulk upload will be added in future releases.

---

## Quick Highlights

* Inline row updates for speed
* Computed fields via annotation expressions
* Custom actions per model
* Context menus on table rows
* Custom sidebar icons
* DaisyUI themed components
* Future-ready bulk updates and CSV uploads
* Custom widgets and inputs for enhanced UI experience

OctopusDash v2 is built for developers and teams who want speed, flexibility, and a modern admin experience.

Made with love by [husseinnaeemsec](https://github.com/husseinnaeemsec)
