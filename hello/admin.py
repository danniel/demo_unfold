from django.contrib import admin

from hello.models import Notebook, ContentRevision


class ContentRevisionInline(admin.TabularInline):
    model = ContentRevision
    extra = 0


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    inlines = (ContentRevisionInline, )
