from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.db import models, router, transaction
from django.db.models.deletion import Collector
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from octopusdash.admin.forms import DynamicModelForm
from .views_mixin import ListviewFiltersMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

class IsAdminIsStaffPermissionMixin:
    
    def dispatch(self,request,*args,**kwargs):
        
        if not request.user.is_superuser or not request.user.is_staff:
            
            return HttpResponseRedirect(reverse("octopusdash-login"))
        
        return super().dispatch(request,*args,**kwargs)

class BaseView:
    @classmethod
    def view_factory(cls, model: models.Model, context: dict):
        return type(
            f"{model._meta.model_name.capitalize()}ModelListView",
            (cls,),
            {
                'model': model,
                'extra_context': context,
            }
        )
    

class ModelListView(BaseView,ListView,ListviewFiltersMixin):
    paginate_by = 20
    template_name = 'od/model/list.html'
    context_object_name = 'objects'
    extra_context = {}

    

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.extra_context)

        formset_class = self.admin.get_formset_class()
        qs = getattr(self, 'queryset', self.model.objects.all())  # this should already be annotated
        page_objects = context['page_obj'].object_list
        pks = [obj.pk for obj in page_objects]
        # Reuse same queryset to avoid droping computed fields
        formset = formset_class(queryset=qs.filter(pk__in=pks))
        context['formset'] = formset

        return context

    def post(self, request):
        request_type = request.POST.get("__request__type",None)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return self.handle_inline_form(request)


        if request_type == 'admin_action':
            
            return self.handle_custom_action(request)
        
        messages.error(request, "The requested action could not be performed.")
        return render(request, self.template_name, self.get_context_data())

    def handle_custom_action(self, request):
        action_name = request.POST.get("action")
        if not action_name:
            messages.error(request, "No action selected.")
            return render(request, self.template_name, self.get_context_data())

        action_callable = self.admin.get_action(action_name)
        if not action_callable:
            messages.error(request, f"Invalid action: '{action_name}'.")
            return render(request, self.template_name, self.get_context_data())

        try:
            ids = request.POST.getlist("__selected__")
            
            if not ids or not isinstance(ids,(list,tuple,)):
                messages.error(request,f"No valid objects were selected.")
            
            qs = self.queryset.filter(id__in=ids)
            
            action_callable(qs)
            if qs.count():
                messages.success(
                    request,
                    f"({qs.count()}) instances {self.admin.opts.verbose_name_plural} were updated successfully."
                )
        except Exception as e:
            messages.error(
                request,
                f"An error occurred while applying '{action_name}': {str(e)}"
            )

        return render(request, self.template_name, self.get_context_data())

    def handle_inline_form(self, request):
        instance_id = request.POST.get("instance_id")
        if not instance_id:
            return JsonResponse({"error": "Instance not found."}, status=404)

        try:
            instance = self.admin.model.objects.get(pk=instance_id)
        except self.admin.model.DoesNotExist:
            return JsonResponse({"error": "Instance not found."}, status=404)

        form_class = DynamicModelForm.form_factory(
            self.admin.model,
            self.admin.get_list_editable()
        )
        form = form_class(request.POST, files=request.FILES, instance=instance)

        if form.is_valid():
            form.save()
            return JsonResponse({
                "message": f'The instance "{instance}" has been successfully updated.'
            })
        return JsonResponse(form.errors, status=400)


class ModelUpdateView(UpdateView, BaseView):
    template_name = 'od/model/update.html'
    form_class = None
    success_url = None

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Instance '{self.object}' was updated successfully."
        )
        return response


class ModelDeleteView(DeleteView, BaseView):
    template_name = 'od/model/delete.html'
    form_class = None
    success_url = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        using = router.db_for_write(self.object.__class__, instance=self.object)

        collector = Collector(using=using)
        collector.collect([self.object])

        related_objects = {model.__name__: list(objs) for model, objs in collector.data.items()}

        context = self.get_context_data()
        context.update({
            'object': self.object,
            'related_objects': related_objects,
        })

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_str = str(self.object)

        response = super().delete(request, *args, **kwargs)

        messages.success(request, f"Instance '{object_str}' was deleted successfully.")
        return response


class ModelCreateView(CreateView, BaseView):
    template_name = 'od/model/update.html'
    form_class = None
    success_url = None

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Instance '{self.object}' was created successfully."
        )
        return response
