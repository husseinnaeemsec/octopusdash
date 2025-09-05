from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from octopusdash.admin.views import IsAdminIsStaffPermissionMixin
# from octopusdash.admin.utils import load_plugins,delete_plugin
from django.contrib.auth import logout
from django.urls import reverse
from django.conf import settings as django_settings
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from zipfile import ZipFile
from octopusdash.admin.variables import MAX_PLUGIN_SIZE
from octopusdash.admin.settings import settings
from octopusdash.admin.plugins.registry import plugins_registry
from octopusdash.signals import delete_plugin_signal,refresh_plugins_registry_signal
from octopusdash.admin.utils import delete_plugin

class DashboardLoginView(View):
    template_name = "od/auth/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("octopusdash-index")  # redirect to dashboard index
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("octopusdash-index")
        else:
            messages.error(request, "Invalid username or password")
            return render(request, self.template_name)


class DashboardView(IsAdminIsStaffPermissionMixin,View):
    template_name = 'od/index.html'
    def get(self,request):
        return render(request,self.template_name)



class PluginsView(IsAdminIsStaffPermissionMixin, View):
    template_name = 'od/plugins/plugins.html'

    def get(self, request):
        context = {
            'loaded_plugins': plugins_registry.get_registry()
        }
        return render(request, self.template_name, context)

    def remove_plugin(self):
        
        plugin = self.request.POST.get("plugin")

        if not plugin:
            messages.error(self.request,"Could not find the plugin")
            return redirect(self.request.path)

        plugin_info = plugins_registry.get(plugin)
        if plugin_info:
            deleted = delete_plugin(django_settings.BASE_DIR,plugin)
            if deleted:
                delete_plugin_signal.send(None,plugin_name=plugin)
                messages.success(self.request,f"Plugin {getattr(plugin_info,'name',plugin)} removed")
            else:
                messages.error(self.request,f"Can not delete the plugin {plugin}")
        
        return redirect(self.request.path)

    def post(self, request):
        
        request_type = request.POST.get("__request__type")
        
        if request_type == 'delete_plugin':
            return self.remove_plugin()
        
        if not settings.get("ALLOW_UPLOADING_PLUGINS",False):
            messages.error(request,'Your project deos not allow uploading custom plugins.')
            return redirect(request.path)
        
        uploaded_file = request.FILES.get("plugin_file")
        if not uploaded_file:
            messages.error(request, "No file uploaded.")
            return redirect(request.path)

        if uploaded_file.size > MAX_PLUGIN_SIZE:
            messages.error(request, "File exceeds maximum size of 200MB.")
            return redirect(request.path)

        # Ensure plugins folder exists
        plugins_dir = os.path.join(django_settings.BASE_DIR, "plugins")
        os.makedirs(plugins_dir, exist_ok=True)

        # Save uploaded file
        file_path = os.path.join(plugins_dir, uploaded_file.name)
        with open(file_path, "wb+") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # If zip, extract it
        if uploaded_file.name.endswith(".zip"):
            try:
                with ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(plugins_dir)
                os.remove(file_path)  # remove zip after extraction
            except Exception as e:
                messages.error(request, f"Failed to extract plugin: {e}")
                return redirect(request.path)

        refresh_plugins_registry_signal.send(None)
        messages.success(request, f"Plugin '{uploaded_file.name}' uploaded successfully.")
        return redirect(request.path)


def logout_view(request):
    """
    Logs out the current user and redirects to the login page.
    """
    logout(request)
    return redirect(reverse("octopusdash-login"))