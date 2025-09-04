from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from octopusdash.admin.views import IsAdminIsStaffPermissionMixin
from django.contrib.auth import logout
from django.urls import reverse

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


def logout_view(request):
    """
    Logs out the current user and redirects to the login page.
    """
    logout(request)
    return redirect(reverse("octopusdash-login"))