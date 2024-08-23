from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.views.generic.edit import FormView
from unfold.admin import ModelAdmin
from unfold.views import UnfoldModelAdminViewMixin

from hello.forms import DemoForm
from hello.models import Notebook, ContentRevision


class DemoFormView(UnfoldModelAdminViewMixin, FormView):
    title = "Demo Form"  # required: custom page header title
    permission_required = ()  # required: tuple of permissions
    template_name = "hello/demo_form.html"
    success_url = "/admin/"
    form_class = DemoForm

    def form_valid(self, form: DemoForm) -> HttpResponse:
        print("GREAT SUCCESS!!!")
        return super().form_valid(form)


class ContentRevisionInline(admin.TabularInline):
    model = ContentRevision
    extra = 0


@admin.register(Notebook)
class NotebookAdmin(ModelAdmin):
    inlines = (ContentRevisionInline,)

    def get_urls(self):
        return [
            path(
                "demo-form/",
                DemoFormView.as_view(
                    model_admin=self
                ),  # IMPORTANT: model_admin is required
                name="demo_form",
            ),
        ] + super().get_urls()
